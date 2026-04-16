from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.services.answer_generation import (
    answer_question,
    build_answer_texts_for_citation_check,
    find_explicit_citation_grounding_violations,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Natural-language query to answer against")
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of retrieved chunks to ground against",
    )
    parser.add_argument(
        "--ef-search",
        type=int,
        default=100,
        help="Runtime HNSW ef_search value",
    )
    parser.add_argument(
        "--model-name",
        help="Override answer generation model name",
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

    result = answer_question(
        query=query,
        top_k=args.top_k,
        ef_search=args.ef_search,
        model_name=args.model_name,
    )
    valid_context_ids = {chunk.context_id for chunk in result.retrieved_chunks}

    assert result.answer.strip(), "answer must not be blank"
    assert result.key_points, "key_points must not be empty"
    assert result.cited_articles, "cited_articles must not be empty"
    assert result.raw_cited_context_ids, "raw_cited_context_ids must not be empty"
    assert result.grounded_context_ids, "grounded_context_ids must not be empty"
    assert all(
        context_id in valid_context_ids for context_id in result.raw_cited_context_ids
    ), "raw_cited_context_ids must be contained in retrieved context ids"
    assert all(
        context_id in valid_context_ids for context_id in result.grounded_context_ids
    ), "grounded_context_ids must be contained in retrieved context ids"
    citation_violations = find_explicit_citation_grounding_violations(
        build_answer_texts_for_citation_check(
            answer=result.answer,
            key_points=result.key_points,
            cautions=result.cautions,
        ),
        retrieved_chunks=result.retrieved_chunks,
        grounded_context_ids=result.grounded_context_ids,
    )
    assert not citation_violations, (
        "answer text referenced invalid citations: "
        + "; ".join(
            f"{violation.category}:{violation.raw_mention}"
            for violation in citation_violations
        )
    )

    print("=" * 72)
    print("Grounded answer verification")
    print("=" * 72)
    print(f"query: {result.query}")
    print(f"model_name: {result.model_name}")
    print(f"retrieval_total: {result.retrieval_total}")
    print(f"raw_cited_context_ids: {result.raw_cited_context_ids}")
    print(
        "expanded_cited_context_ids: "
        f"{getattr(result, 'expanded_cited_context_ids', result.grounded_context_ids)}"
    )
    print(f"grounded_context_ids: {result.grounded_context_ids}")
    print(f"cited_articles: {result.cited_articles}")
    print(
        "citation_postprocess_additions: "
        f"{getattr(result, 'citation_postprocess_additions', [])}"
    )
    print(f"citation_violations: {len(citation_violations)}")
    print("-" * 72)
    print("answer:")
    print(result.answer)
    print("-" * 72)
    print("key_points:")
    for point in result.key_points:
        print(f"- {point}")
    print("-" * 72)
    print("cautions:")
    for caution in result.cautions:
        print(f"- {caution}")
    print("-" * 72)
    print("retrieved_chunks:")
    for chunk in result.retrieved_chunks:
        grounded_marker = "*" if chunk.context_id in result.grounded_context_ids else " "
        print(
            f"{grounded_marker}[{chunk.context_id}] similarity={chunk.similarity:.6f} "
            f"citation={chunk.citation_label}"
        )
        print(f"     chunk_id={chunk.chunk_id}")
        print(f"     content={summarize_content(chunk.content)}")


if __name__ == "__main__":
    main()
