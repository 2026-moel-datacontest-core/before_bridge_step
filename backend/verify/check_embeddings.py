from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import func, select, text

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / ".env")

from app.db import SessionLocal
from app.models import LawChunk

EXPECTED_DIMENSION = 768
DEFAULT_SAMPLE_SIZE = 5
INDEX_NAME = "idx_law_chunks_embedding"
LOG_PATH = BACKEND_DIR / "logs" / "embed_chunks.log"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help="Number of non-null embedding rows to inspect",
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Exit non-zero when any embedding is still NULL",
    )
    parser.add_argument(
        "--require-index",
        action="store_true",
        help="Exit non-zero when the HNSW index is missing",
    )
    return parser.parse_args()


def log_level_counts(log_path: Path) -> tuple[bool, int, int]:
    if not log_path.exists():
        return False, 0, 0

    warning_count = 0
    error_count = 0
    with log_path.open(encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if " WARNING " in line:
                warning_count += 1
            if " ERROR " in line:
                error_count += 1

    return True, warning_count, error_count


def main() -> None:
    args = parse_args()
    if args.sample_size <= 0:
        raise ValueError("--sample-size must be greater than 0.")

    with SessionLocal() as session:
        total_rows = session.scalar(select(func.count()).select_from(LawChunk)) or 0
        embedded_rows = (
            session.scalar(
                select(func.count())
                .select_from(LawChunk)
                .where(LawChunk.embedding.is_not(None))
            )
            or 0
        )
        null_rows = total_rows - embedded_rows

        sample_rows = session.execute(
            select(LawChunk.chunk_id, LawChunk.embedding)
            .where(LawChunk.embedding.is_not(None))
            .order_by(LawChunk.chunk_id)
            .limit(args.sample_size)
        ).all()

        index_exists = bool(
            session.execute(
                text(
                    """
                    SELECT 1
                    FROM pg_indexes
                    WHERE schemaname = current_schema()
                      AND tablename = 'law_chunks'
                      AND indexname = :index_name
                    """
                ),
                {"index_name": INDEX_NAME},
            ).first()
        )

    bad_dimensions: list[tuple[str, int]] = []
    sample_dimensions: list[tuple[str, int]] = []
    for row in sample_rows:
        dimension = len(row.embedding) if row.embedding is not None else 0
        sample_dimensions.append((row.chunk_id, dimension))
        if dimension != EXPECTED_DIMENSION:
            bad_dimensions.append((row.chunk_id, dimension))

    log_exists, warning_count, error_count = log_level_counts(LOG_PATH)

    print("=" * 72)
    print("Embedding verification")
    print("=" * 72)
    print(f"total_rows: {total_rows}")
    print(f"embedded_rows: {embedded_rows}")
    print(f"null_rows: {null_rows}")
    print(f"expected_dimension: {EXPECTED_DIMENSION}")
    print(f"sample_rows_checked: {len(sample_dimensions)}")
    print(f"bad_dimension_rows: {len(bad_dimensions)}")
    print(f"log_path: {LOG_PATH}")
    print(f"log_exists: {log_exists}")
    print(f"log_warning_count: {warning_count}")
    print(f"log_error_count: {error_count}")
    print(f"hnsw_index_exists: {index_exists}")

    if sample_dimensions:
        print("-" * 72)
        for chunk_id, dimension in sample_dimensions:
            print(f"{chunk_id}: dimension={dimension}")

    failures: list[str] = []
    if bad_dimensions:
        failures.append("sampled embeddings with unexpected dimension were found")
    if args.require_complete and null_rows != 0:
        failures.append("some embeddings are still NULL")
    if args.require_index and not index_exists:
        failures.append("HNSW index is missing")

    if failures:
        print("-" * 72)
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
