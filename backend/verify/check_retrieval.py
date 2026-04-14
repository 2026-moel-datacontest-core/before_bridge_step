from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.services.embedding import OUTPUT_DIMENSIONALITY, embed_query
from backend.app.services.retrieval import (
    build_cited_articles,
    search_law_chunks,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Natural-language query to retrieve against")
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of nearest chunks to return",
    )
    parser.add_argument(
        "--ef-search",
        type=int,
        default=100,
        help="Runtime HNSW ef_search value",
    )
    return parser.parse_args()


def summarize_content(content: str, width: int = 180) -> str:
    normalized = " ".join(content.split())
    return textwrap.shorten(normalized, width=width, placeholder="...")


def main() -> None:
    args = parse_args()
    query = args.query.strip()
    if not query:
        raise ValueError("query must not be blank.")

    query_vector = embed_query(query)
    chunks = search_law_chunks(
        query_vector=query_vector,
        top_k=args.top_k,
        ef_search=args.ef_search,
    )
    cited_articles = build_cited_articles(chunks)

    print("=" * 72)
    print("Retrieval verification")
    print("=" * 72)
    print(f"query: {query}")
    print(f"query_embedding_dimension: {len(query_vector)}")
    print(f"expected_dimension: {OUTPUT_DIMENSIONALITY}")
    print(f"top_k: {args.top_k}")
    print(f"ef_search: {args.ef_search}")
    print(f"result_count: {len(chunks)}")
    print(f"cited_articles: {cited_articles}")

    if not chunks:
        return

    print("-" * 72)
    for index, chunk in enumerate(chunks, start=1):
        print(f"[{index}] similarity={chunk.similarity:.6f}")
        print(f"     citation={chunk.citation_label}")
        print(f"     chunk_id={chunk.chunk_id}")
        print(f"     law_name={chunk.law_name}")
        print(f"     article_no={chunk.article_no}")
        print(f"     article_title={chunk.article_title}")
        print(f"     paragraph_no={chunk.paragraph_no}")
        print(f"     tier={chunk.tier}")
        print(f"     structure_path={chunk.structure_path}")
        print(f"     content={summarize_content(chunk.content)}")


if __name__ == "__main__":
    main()
