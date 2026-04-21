from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.before_stack.core.settings import LAW_CHUNKS_PATH
from backend.app.before_stack.services.law_chunk_cache import (
    load_all_chunks_from_db,
    load_all_chunks_from_file,
)
from backend.app.before_stack.services.law_retriever import (
    build_extra_law_map,
    retrieve_law_chunks,
)


REPRESENTATIVE_CITATIONS = [
    "근로기준법 제7조 (강제 근로의 금지)",
    "근로기준법 제20조 (위약 예정의 금지)",
    "근로기준법 제43조 (임금 지급)",
    "외국인근로자의 고용 등에 관한 법률 제22조 (기숙사의 제공 등) [중복순번 2]",
]

EXTRA_SECTIONS = [
    {"number": "12", "title": "경업금지", "full_text": "경업금지 및 위약금 조항이 있습니다."},
    {"number": "13", "title": "기숙사", "full_text": "기숙사비와 숙소 제공 관련 조항이 있습니다."},
    {"number": "14", "title": "무관 키워드", "full_text": "특별한 키워드가 없는 일반 문장입니다."},
]

FOREIGN_WORKER_CONTEXT = {
    "worker_group": "foreign_worker",
    "worker_group_confidence": "confirmed",
}


def _citation_labels(items: list[dict], limit: int | None = None) -> list[str]:
    selected = items[:limit] if limit is not None else items
    return [item["citation_label"] for item in selected]


def _find_by_citation(chunks: list[dict], citation_label: str) -> dict | None:
    for chunk in chunks:
        if chunk["citation_label"] == citation_label:
            return chunk
    return None


def main() -> int:
    file_chunks = load_all_chunks_from_file(LAW_CHUNKS_PATH)
    db_chunks = load_all_chunks_from_db()

    file_ids = {chunk["chunk_id"] for chunk in file_chunks}
    db_ids = {chunk["chunk_id"] for chunk in db_chunks}
    only_in_file = sorted(file_ids - db_ids)
    only_in_db = sorted(db_ids - file_ids)

    print("== Before Law Source Parity ==")
    print(f"file_count: {len(file_chunks)}")
    print(f"db_count:   {len(db_chunks)}")
    print(f"only_in_file_count: {len(only_in_file)}")
    print(f"only_in_db_count:   {len(only_in_db)}")
    if only_in_file:
        print("only_in_file_sample:")
        for chunk_id in only_in_file[:10]:
            print(f"  - {chunk_id}")
    if only_in_db:
        print("only_in_db_sample:")
        for chunk_id in only_in_db[:10]:
            print(f"  - {chunk_id}")

    print("\n== Representative Citation Checks ==")
    representative_ok = True
    for citation_label in REPRESENTATIVE_CITATIONS:
        file_chunk = _find_by_citation(file_chunks, citation_label)
        db_chunk = _find_by_citation(db_chunks, citation_label)
        same = (
            file_chunk is not None
            and db_chunk is not None
            and file_chunk["chunk_id"] == db_chunk["chunk_id"]
        )
        print(f"- {citation_label}: {'OK' if same else 'DIFF'}")
        if not same:
            representative_ok = False
            print(f"  file: {file_chunk['chunk_id'] if file_chunk else None}")
            print(f"  db:   {db_chunk['chunk_id'] if db_chunk else None}")

    fallback_file = _citation_labels(retrieve_law_chunks("키워드 없는 문장", file_chunks), limit=5)
    fallback_db = _citation_labels(retrieve_law_chunks("키워드 없는 문장", db_chunks), limit=5)
    fallback_ok = fallback_file == fallback_db

    print("\n== Fallback Check ==")
    print(f"same: {fallback_ok}")
    print(f"file: {fallback_file}")
    print(f"db:   {fallback_db}")

    extra_file = build_extra_law_map(EXTRA_SECTIONS, file_chunks, FOREIGN_WORKER_CONTEXT)
    extra_db = build_extra_law_map(EXTRA_SECTIONS, db_chunks, FOREIGN_WORKER_CONTEXT)

    print("\n== Extra Section Checks ==")
    extra_ok = True
    for section in EXTRA_SECTIONS:
        sec_no = section["number"]
        file_labels = _citation_labels(extra_file[sec_no])
        db_labels = _citation_labels(extra_db[sec_no])
        same = file_labels == db_labels
        print(f"- section {sec_no}: {'OK' if same else 'DIFF'}")
        print(f"  file: {file_labels}")
        print(f"  db:   {db_labels}")
        if not same:
            extra_ok = False

    behavioral_parity_ok = representative_ok and fallback_ok and extra_ok

    print("\n== Summary ==")
    print(f"behavioral_parity_ok: {behavioral_parity_ok}")
    print(f"source_count_match:   {len(file_chunks) == len(db_chunks)}")
    print(
        "note: count mismatch alone is reported as source drift and does not fail "
        "behavioral parity if representative retrieval results still match."
    )

    return 0 if behavioral_parity_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
