from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence

from sqlalchemy import literal, select, text

from backend.app.db import SessionLocal
from backend.app.models import LawChunk
from backend.app.services.embedding import OUTPUT_DIMENSIONALITY, embed_query

DEFAULT_TOP_K = 5
DEFAULT_EF_SEARCH = 100
MAX_TOP_K = 10
MIN_EF_SEARCH = 10
MAX_EF_SEARCH = 500
SEGMENT_SPLIT_PATTERN = re.compile(r"(?:\n+|(?<=[.!?])\s+)")
INSTRUCTIONAL_SEGMENT_MARKERS = (
    "이전 지시",
    "지시를 무시",
    "규칙을 무시",
    "프롬프트",
    "system prompt",
    "assistant",
    "json만",
    "markdown",
    "코드펜스",
    "인용하라",
    "출력하라",
    "답하라",
)
INSTRUCTIONAL_CLAUSE_PATTERNS = (
    re.compile(r"(?:이전|위|앞의)?\s*지시[^.?!\n]*?(?:무시|따르지)[^.?!\n]*", re.IGNORECASE),
    re.compile(r"[^.?!\n]*?제\d+조(?:의\d+)?[^.?!\n]*?(?:인용하라|써라|출력하라)", re.IGNORECASE),
    re.compile(r"[^.?!\n]*?(?:json|markdown|코드펜스|system prompt|프롬프트)[^.?!\n]*?(?:출력|답|작성)하라", re.IGNORECASE),
)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    citation_label: str
    law_name: str
    article_no: str
    article_title: str
    paragraph_no: int | None
    content: str
    similarity: float
    tier: int
    structure_path: str | None


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    grounding_query: str
    total: int
    chunks: list[RetrievedChunk]
    cited_articles: list[str]


def validate_search_params(top_k: int, ef_search: int) -> None:
    if not 1 <= top_k <= MAX_TOP_K:
        raise ValueError(f"top_k must be between 1 and {MAX_TOP_K}.")
    if not MIN_EF_SEARCH <= ef_search <= MAX_EF_SEARCH:
        raise ValueError(
            f"ef_search must be between {MIN_EF_SEARCH} and {MAX_EF_SEARCH}."
        )


def build_cited_articles(chunks: Iterable[RetrievedChunk]) -> list[str]:
    cited_articles: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        if chunk.citation_label in seen:
            continue
        cited_articles.append(chunk.citation_label)
        seen.add(chunk.citation_label)
    return cited_articles


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split()).strip()


def strip_instructional_clauses(query: str) -> str:
    sanitized = query
    for pattern in INSTRUCTIONAL_CLAUSE_PATTERNS:
        sanitized = pattern.sub(" ", sanitized)
    return normalize_whitespace(sanitized)


def is_instructional_segment(segment: str) -> bool:
    normalized = segment.lower()
    return any(marker in normalized for marker in INSTRUCTIONAL_SEGMENT_MARKERS)


def normalize_grounding_query(query: str) -> str:
    query_text = normalize_whitespace(query)
    if not query_text:
        return query_text

    clause_stripped = strip_instructional_clauses(query_text)
    segments = [
        segment.strip()
        for segment in SEGMENT_SPLIT_PATTERN.split(clause_stripped)
        if segment.strip()
    ]
    clean_segments = [segment for segment in segments if not is_instructional_segment(segment)]
    if clean_segments:
        return normalize_whitespace(
            re.sub(r"^[,.;:!?]+", "", " ".join(clean_segments)).strip()
        )
    if clause_stripped:
        return normalize_whitespace(re.sub(r"^[,.;:!?]+", "", clause_stripped).strip())
    return query_text


def search_law_chunks(
    query_vector: Sequence[float],
    *,
    top_k: int = DEFAULT_TOP_K,
    ef_search: int = DEFAULT_EF_SEARCH,
) -> list[RetrievedChunk]:
    validate_search_params(top_k=top_k, ef_search=ef_search)
    if len(query_vector) != OUTPUT_DIMENSIONALITY:
        raise ValueError(
            "query_vector must be 768-dimensional. "
            f"Received {len(query_vector)} values."
        )

    distance_expr = LawChunk.embedding.cosine_distance(query_vector)
    similarity_expr = (literal(1.0) - distance_expr).label("similarity")

    statement = (
        select(
            LawChunk.chunk_id,
            LawChunk.citation_label,
            LawChunk.law_name,
            LawChunk.article_no,
            LawChunk.article_title,
            LawChunk.paragraph_no,
            LawChunk.content,
            LawChunk.tier,
            LawChunk.structure_path,
            similarity_expr,
        )
        .where(LawChunk.embedding.is_not(None))
        .order_by(distance_expr.asc())
        .limit(top_k)
    )

    with SessionLocal() as session:
        with session.begin():
            # PostgreSQL `SET LOCAL` does not bind cleanly through SQLAlchemy here,
            # so only the already range-validated integer is interpolated.
            session.execute(text(f"SET LOCAL hnsw.ef_search = {ef_search}"))
            rows = session.execute(statement).all()

    return [
        RetrievedChunk(
            chunk_id=row.chunk_id,
            citation_label=row.citation_label,
            law_name=row.law_name,
            article_no=row.article_no,
            article_title=row.article_title,
            paragraph_no=row.paragraph_no,
            content=row.content,
            similarity=float(row.similarity),
            tier=row.tier,
            structure_path=row.structure_path,
        )
        for row in rows
    ]


def retrieve_law_chunks(
    query: str,
    *,
    top_k: int = DEFAULT_TOP_K,
    ef_search: int = DEFAULT_EF_SEARCH,
) -> RetrievalResult:
    query_text = query.strip()
    if not query_text:
        raise ValueError("query must not be blank.")

    grounding_query = normalize_grounding_query(query_text)
    query_vector = embed_query(grounding_query)
    chunks = search_law_chunks(
        query_vector=query_vector,
        top_k=top_k,
        ef_search=ef_search,
    )
    return RetrievalResult(
        query=query_text,
        grounding_query=grounding_query,
        total=len(chunks),
        chunks=chunks,
        cited_articles=build_cited_articles(chunks),
    )
