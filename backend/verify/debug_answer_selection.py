from __future__ import annotations

import argparse
import json
import sys
import textwrap
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.services.answer_generation import (
    CLAUSE_PRIORITY_MARKERS,
    LOW_SIGNAL_VALUES,
    OUTPUT_KEY_POINT_LIMIT,
    PROCEDURE_QUERY_HINTS,
    PROMPT_NUMERIC_SIGNAL_PATTERN,
    CitationPostprocessAddition,
    GroundedClauseCandidate,
    GroundedRetrievedChunk,
    build_clause_candidates_for_chunk,
    build_cited_articles_from_context_ids,
    build_grounded_chunks,
    build_signal_summary_key_point,
    collect_narrow_chunk_bias_reasons,
    collect_narrow_clause_bias_reasons,
    compact_text,
    contains_query_token,
    extract_prompt_signal_phrases,
    generate_grounded_answer,
    get_active_query_focuses,
    get_clause_focuses,
    normalize_article_reference,
    normalize_output_style,
    normalize_text,
    sanitize_output_clause_references,
    serialize_citation_postprocess_addition,
    serialize_score_adjustment_reason,
    score_grounded_chunk,
    score_grounded_clause,
    select_grounded_clause_key_points,
    select_grounded_chunks_by_context_ids,
)
from backend.app.services.embedding import build_query_embedding_text, matching_query_hints
from backend.app.services.retrieval import RetrievalResult, retrieve_law_chunks

DEFAULT_EVAL_DATASET_PATH = REPO_ROOT / "eval" / "mvp_in_scope_eval_v1.json"
DEFAULT_SCENARIO_DATASET_PATH = REPO_ROOT / "eval" / "scenario_demo_question_sets_v1.json"
DEFAULT_EVAL_IDS = ("KLS-EVAL-010", "KLS-EVAL-017", "KLS-EVAL-058")
DEFAULT_SCENARIO_IDS = ("SCN-005-Q3",)
DEFAULT_REGRESSION_IDS = ("SCN-004-Q1",)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "backend" / "logs" / "answer_selection_debug"
DEFAULT_TOP_K = 5
DEFAULT_EF_SEARCH = 100
PROMPT_COVERAGE_POINT_LIMIT = 2


@dataclass(frozen=True)
class DebugQuestion:
    item_id: str
    source: str
    question: str
    expected_citations: list[str]
    expected_points: list[str]
    recommended_top_k: int | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--eval-dataset",
        type=Path,
        default=DEFAULT_EVAL_DATASET_PATH,
        help="Path to the baseline answer eval dataset JSON file.",
    )
    parser.add_argument(
        "--scenario-dataset",
        type=Path,
        default=DEFAULT_SCENARIO_DATASET_PATH,
        help="Path to the scenario smoke dataset JSON file.",
    )
    parser.add_argument(
        "--eval-ids",
        nargs="*",
        default=list(DEFAULT_EVAL_IDS),
        help="Baseline eval ids to inspect.",
    )
    parser.add_argument(
        "--scenario-ids",
        nargs="*",
        default=list(DEFAULT_SCENARIO_IDS),
        help="Scenario question ids to inspect.",
    )
    parser.add_argument(
        "--regression-ids",
        nargs="*",
        default=[],
        help="Additional scenario ids to run as regression samples.",
    )
    parser.add_argument(
        "--include-default-regression",
        action="store_true",
        help="Also run the default SCN-004 regression sample.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help="Default retrieval top-k when an item does not define a recommended top-k.",
    )
    parser.add_argument(
        "--ef-search",
        type=int,
        default=DEFAULT_EF_SEARCH,
        help="Runtime HNSW ef_search value.",
    )
    parser.add_argument(
        "--model-name",
        help="Override answer generation model name.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where JSON and text debug reports will be written.",
    )
    parser.add_argument(
        "--output-prefix",
        default="answer_selection_debug",
        help="Prefix used for generated report filenames.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_eval_questions(dataset_path: Path, requested_ids: list[str]) -> list[DebugQuestion]:
    payload = load_json(dataset_path)
    items = payload.get("items")
    if not isinstance(items, list):
        raise ValueError('Eval payload must contain a top-level "items" list.')

    item_by_id = {item["id"]: item for item in items}
    missing_ids = [item_id for item_id in requested_ids if item_id not in item_by_id]
    if missing_ids:
        raise ValueError(f"Unknown eval ids: {missing_ids}")

    questions: list[DebugQuestion] = []
    for item_id in requested_ids:
        item = item_by_id[item_id]
        questions.append(
            DebugQuestion(
                item_id=item["id"],
                source="eval",
                question=item["question"],
                expected_citations=list(item.get("gold_citations", [])),
                expected_points=list(item.get("expected_points", [])),
            )
        )
    return questions


def load_scenario_questions(dataset_path: Path, requested_ids: list[str]) -> list[DebugQuestion]:
    payload = load_json(dataset_path)
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list):
        raise ValueError('Scenario payload must contain a top-level "scenarios" list.')

    question_by_id: dict[str, dict[str, Any]] = {}
    for scenario in scenarios:
        for question in scenario.get("questions", []):
            question_by_id[question["id"]] = question

    missing_ids = [item_id for item_id in requested_ids if item_id not in question_by_id]
    if missing_ids:
        raise ValueError(f"Unknown scenario ids: {missing_ids}")

    questions: list[DebugQuestion] = []
    for item_id in requested_ids:
        question = question_by_id[item_id]
        questions.append(
            DebugQuestion(
                item_id=question["id"],
                source="scenario",
                question=question["question"],
                expected_citations=list(question.get("expected_citations", [])),
                expected_points=list(question.get("expected_points", [])),
                recommended_top_k=question.get("recommended_top_k"),
            )
        )
    return questions


def summarize_content(content: str, width: int = 180) -> str:
    normalized = " ".join(content.split())
    return textwrap.shorten(normalized, width=width, placeholder="...")


def build_clause_score_debug(
    query: str,
    query_terms: list[str],
    active_focuses: list[str],
    chunk: GroundedRetrievedChunk,
    candidate: GroundedClauseCandidate,
) -> dict[str, Any]:
    normalized_clause = normalize_text(candidate.text)
    clause_focuses = sorted(get_clause_focuses(normalized_clause))
    matched_query_terms = [
        token for token in query_terms if contains_query_token(normalized_clause, token)
    ]
    matched_focuses = [focus for focus in active_focuses if focus in clause_focuses]
    priority_markers = [
        marker for marker in CLAUSE_PRIORITY_MARKERS if marker in normalized_clause
    ]
    narrow_bias_reasons = [
        serialize_score_adjustment_reason(reason)
        for reason in collect_narrow_clause_bias_reasons(
            query,
            active_focuses,
            chunk,
            candidate.text,
            set(clause_focuses),
        )
    ]

    score_reasons: list[dict[str, Any]] = []
    for token in matched_query_terms:
        score_reasons.append(
            {
                "label": f"query_term:{token}",
                "delta": 4,
            }
        )

    if matched_query_terms:
        score_reasons.append(
            {
                "label": "matched_query_terms_bonus",
                "delta": min(6, len(matched_query_terms) * 2),
            }
        )
    elif matched_focuses:
        score_reasons.append(
            {
                "label": "focus_only_penalty",
                "delta": -1,
            }
        )
    else:
        score_reasons.append(
            {
                "label": "no_query_alignment_penalty",
                "delta": -6,
            }
        )

    if PROMPT_NUMERIC_SIGNAL_PATTERN.search(normalized_clause):
        score_reasons.append({"label": "numeric_signal", "delta": 4})

    for marker in priority_markers:
        score_reasons.append({"label": f"priority_marker:{marker}", "delta": 2})

    for focus in matched_focuses:
        score_reasons.append({"label": f"focus_match:{focus}", "delta": 4})

    if normalized_clause.startswith("다만"):
        score_reasons.append({"label": "starts_with_exception_marker", "delta": 2})
    if "다만" in normalized_clause:
        score_reasons.append({"label": "contains_exception_marker", "delta": 2})

    for marker in ("근무장소의 변경", "표준근로계약서", "한국산업인력공단"):
        if marker in normalized_clause:
            score_reasons.append({"label": f"special_clause_marker:{marker}", "delta": 4})

    for marker in ("사업장 변경", "출국만기보험", "퇴직금제도"):
        if marker in normalized_clause:
            score_reasons.append({"label": f"special_clause_marker:{marker}", "delta": 3})

    if len(normalized_clause) > 240:
        score_reasons.append({"label": "long_clause_penalty", "delta": -1})

    score_reasons.extend(narrow_bias_reasons)

    return {
        "clause_index": candidate.clause_index,
        "text": candidate.text,
        "score": score_grounded_clause(
            query,
            query_terms,
            active_focuses,
            candidate.text,
            chunk=chunk,
        ),
        "matched_query_terms": matched_query_terms,
        "clause_focuses": clause_focuses,
        "matched_focuses": matched_focuses,
        "priority_markers": priority_markers,
        "narrow_bias_reasons": narrow_bias_reasons,
        "score_reasons": score_reasons,
    }


def build_chunk_score_debug(
    query: str,
    query_terms: list[str],
    active_focuses: list[str],
    chunk: GroundedRetrievedChunk,
) -> dict[str, Any]:
    searchable_text = normalize_text(
        " ".join(
            [
                chunk.citation_label,
                chunk.law_name,
                chunk.article_title,
                chunk.content[:600],
            ]
        )
    )
    reason_entries: list[dict[str, Any]] = [
        {
            "label": "similarity_base",
            "delta": round(chunk.similarity * 100, 6),
        }
    ]
    narrow_bias_reasons = [
        serialize_score_adjustment_reason(reason)
        for reason in collect_narrow_chunk_bias_reasons(
            query,
            active_focuses,
            chunk,
        )
    ]

    for token in query_terms:
        if contains_query_token(searchable_text, token):
            reason_entries.append(
                {
                    "label": f"searchable_text_token:{token}",
                    "delta": 2.5,
                }
            )
        if contains_query_token(chunk.article_title, token):
            reason_entries.append(
                {
                    "label": f"article_title_token:{token}",
                    "delta": 5.0,
                }
            )
        if contains_query_token(chunk.citation_label, token):
            reason_entries.append(
                {
                    "label": f"citation_label_token:{token}",
                    "delta": 4.0,
                }
            )

    law_name = normalize_text(chunk.law_name)
    if "시행규칙" in law_name:
        reason_entries.append({"label": "law_type:시행규칙", "delta": -1.0})
        if any(hint in query for hint in PROCEDURE_QUERY_HINTS):
            reason_entries.append(
                {
                    "label": "procedure_query_bonus_for_시행규칙",
                    "delta": 2.5,
                }
            )
    elif "시행령" in law_name:
        reason_entries.append({"label": "law_type:시행령", "delta": 0.5})
    else:
        reason_entries.append({"label": "law_type:법률", "delta": 2.0})

    clause_candidates = build_clause_candidates_for_chunk(chunk)
    clause_debug = [
        build_clause_score_debug(query, query_terms, active_focuses, chunk, candidate)
        for candidate in clause_candidates
    ]
    best_clause = max(clause_debug, key=lambda item: item["score"], default=None)
    if best_clause is not None:
        reason_entries.append(
            {
                "label": f"best_clause_boost:index={best_clause['clause_index']}",
                "delta": round(best_clause["score"] * 1.5, 6),
            }
        )

    reason_entries.extend(narrow_bias_reasons)

    return {
        "context_id": chunk.context_id,
        "chunk_id": chunk.chunk_id,
        "citation_label": chunk.citation_label,
        "similarity": chunk.similarity,
        "chunk_score": round(
            score_grounded_chunk(query, query_terms, active_focuses, chunk),
            6,
        ),
        "narrow_bias_reasons": narrow_bias_reasons,
        "chunk_score_reasons": reason_entries,
        "prompt_signals": extract_prompt_signal_phrases(chunk.content),
        "prompt_coverage_clauses": select_grounded_clause_key_points(
            query,
            [chunk],
            point_limit=PROMPT_COVERAGE_POINT_LIMIT,
        ),
        "content_summary": summarize_content(chunk.content),
        "clause_candidates": clause_debug,
    }


def build_selected_clause_entries(
    query: str,
    grounded_chunks: list[GroundedRetrievedChunk],
) -> tuple[list[str], list[dict[str, Any]], list[int]]:
    selected_points = select_grounded_clause_key_points(
        query,
        grounded_chunks,
        point_limit=OUTPUT_KEY_POINT_LIMIT,
    )
    point_keys = [compact_text(point) for point in selected_points]
    point_positions: dict[str, list[int]] = defaultdict(list)
    for index, point_key in enumerate(point_keys, start=1):
        point_positions[point_key].append(index)

    query_text = normalize_text(query)
    query_terms = [
        token
        for token in text_to_query_terms(query_text)
    ]
    active_focuses = get_active_query_focuses(query_text)

    ordered_chunks = sorted(
        grounded_chunks,
        key=lambda chunk: (
            -score_grounded_chunk(query_text, query_terms, active_focuses, chunk),
            chunk.context_id,
        ),
    )
    ordered_context_ids = [chunk.context_id for chunk in ordered_chunks]

    selected_entries: list[dict[str, Any]] = []
    used_orders: set[tuple[str, int]] = set()
    for chunk in ordered_chunks:
        for candidate in build_clause_candidates_for_chunk(chunk):
            candidate_key = compact_text(candidate.text)
            if candidate_key not in point_positions:
                continue
            for order in point_positions[candidate_key]:
                dedupe_key = (candidate_key, order)
                if dedupe_key in used_orders:
                    continue
                clause_debug = build_clause_score_debug(
                    query_text,
                    query_terms,
                    active_focuses,
                    chunk,
                    candidate,
                )
                selected_entries.append(
                    {
                        "order": order,
                        "context_id": chunk.context_id,
                        "citation_label": chunk.citation_label,
                        "clause_index": candidate.clause_index,
                        "text": candidate.text,
                        "score": clause_debug["score"],
                        "matched_query_terms": clause_debug["matched_query_terms"],
                        "matched_focuses": clause_debug["matched_focuses"],
                        "clause_focuses": clause_debug["clause_focuses"],
                        "score_reasons": clause_debug["score_reasons"],
                    }
                )
                used_orders.add(dedupe_key)
                break

    selected_entries.sort(key=lambda item: item["order"])
    return selected_points, selected_entries, ordered_context_ids


def text_to_query_terms(query: str) -> list[str]:
    from backend.app.services.answer_generation import tokenize_query_terms

    return tokenize_query_terms(query)


def build_possible_signal_summary_points(
    grounded_chunks: list[GroundedRetrievedChunk],
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for chunk in grounded_chunks:
        signals = [
            signal
            for signal in extract_prompt_signal_phrases(chunk.content)
            if signal not in LOW_SIGNAL_VALUES
        ]
        if not signals:
            continue
        summary = build_signal_summary_key_point(chunk, signals)
        if summary is None:
            continue
        summaries.append(
            {
                "context_id": chunk.context_id,
                "citation_label": chunk.citation_label,
                "summary_point": normalize_output_style(summary),
            }
        )
    return summaries


def classify_key_point_sources(
    key_points: list[str],
    *,
    selected_clause_entries: list[dict[str, Any]],
    signal_summary_points: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    def normalized_point_key(text: str) -> str:
        return compact_text(
            sanitize_output_clause_references(normalize_output_style(text))
        )

    selected_clause_by_key: dict[str, dict[str, Any]] = {}
    for entry in selected_clause_entries:
        selected_clause_by_key[normalized_point_key(entry["text"])] = entry

    signal_summary_by_key: dict[str, dict[str, Any]] = {}
    for entry in signal_summary_points:
        signal_summary_by_key[normalized_point_key(entry["summary_point"])] = entry

    key_point_sources: list[dict[str, Any]] = []
    for order, point in enumerate(key_points, start=1):
        point_key = normalized_point_key(point)
        selected_entry = selected_clause_by_key.get(point_key)
        if selected_entry is not None:
            key_point_sources.append(
                {
                    "order": order,
                    "key_point": point,
                    "source_type": "grounded_clause",
                    "context_id": selected_entry["context_id"],
                    "citation_label": selected_entry["citation_label"],
                    "clause_index": selected_entry["clause_index"],
                    "selected_clause_order": selected_entry["order"],
                }
            )
            continue

        signal_entry = signal_summary_by_key.get(point_key)
        if signal_entry is not None:
            key_point_sources.append(
                {
                    "order": order,
                    "key_point": point,
                    "source_type": "signal_summary",
                    "context_id": signal_entry["context_id"],
                    "citation_label": signal_entry["citation_label"],
                }
            )
            continue

        key_point_sources.append(
            {
                "order": order,
                "key_point": point,
                "source_type": "model_or_other",
            }
        )

    return key_point_sources


def build_citation_stage_summary(
    result: Any,
    retrieval_chunks: list[GroundedRetrievedChunk],
    expected_citations: list[str],
) -> dict[str, Any]:
    raw_context_id_set = set(result.raw_cited_context_ids)
    expanded_context_id_set = set(getattr(result, "expanded_cited_context_ids", []))
    grounded_context_id_set = set(result.grounded_context_ids)
    cited_article_set = set(result.cited_articles)

    per_context: list[dict[str, Any]] = []
    for chunk in retrieval_chunks:
        per_context.append(
            {
                "context_id": chunk.context_id,
                "citation_label": chunk.citation_label,
                "retrieved": True,
                "raw_model_cited": chunk.context_id in raw_context_id_set,
                "expanded_cited": chunk.context_id in expanded_context_id_set,
                "postprocess_added": chunk.context_id in expanded_context_id_set
                and chunk.context_id not in raw_context_id_set,
                "grounded": chunk.context_id in grounded_context_id_set,
                "cited_article_survived": chunk.citation_label in cited_article_set,
                "expected_citation": chunk.citation_label in expected_citations,
            }
        )

    expected_hit = [
        citation for citation in expected_citations if citation in cited_article_set
    ]
    expected_miss = [
        citation for citation in expected_citations if citation not in cited_article_set
    ]

    sibling_groups: list[dict[str, Any]] = []
    grouped_contexts: dict[tuple[str, str], list[GroundedRetrievedChunk]] = defaultdict(list)
    for chunk in retrieval_chunks:
        grouped_contexts[(chunk.law_name, normalize_article_reference(chunk.citation_label))].append(
            chunk
        )

    for (law_name, article_ref), group in grouped_contexts.items():
        if len(group) < 2 or not article_ref:
            continue
        sibling_groups.append(
            {
                "law_name": law_name,
                "article_ref": article_ref,
                "context_ids": [chunk.context_id for chunk in group],
                "citations": [chunk.citation_label for chunk in group],
                "raw_cited_context_ids": [
                    chunk.context_id for chunk in group if chunk.context_id in raw_context_id_set
                ],
                "expanded_cited_context_ids": [
                    chunk.context_id
                    for chunk in group
                    if chunk.context_id in expanded_context_id_set
                ],
                "grounded_context_ids": [
                    chunk.context_id
                    for chunk in group
                    if chunk.context_id in grounded_context_id_set
                ],
                "cited_articles": [
                    chunk.citation_label
                    for chunk in group
                    if chunk.citation_label in cited_article_set
                ],
            }
        )

    return {
        "raw_cited_context_ids": list(result.raw_cited_context_ids),
        "expanded_cited_context_ids": list(getattr(result, "expanded_cited_context_ids", [])),
        "grounded_context_ids": list(result.grounded_context_ids),
        "cited_articles": list(result.cited_articles),
        "citation_postprocess_additions": [
            serialize_citation_postprocess_addition(addition)
            for addition in getattr(result, "citation_postprocess_additions", [])
        ],
        "per_context": per_context,
        "expected_citation_hit": expected_hit,
        "expected_citation_miss": expected_miss,
        "sibling_article_groups": sibling_groups,
    }


def build_item_diagnostics(
    question: DebugQuestion,
    *,
    retrieval_chunks: list[GroundedRetrievedChunk],
    result: Any,
    selected_clause_entries: list[dict[str, Any]],
    citation_stage_summary: dict[str, Any],
) -> list[str]:
    notes: list[str] = []
    retrieved_labels = {chunk.citation_label for chunk in retrieval_chunks}
    expected_retrieved = [
        citation for citation in question.expected_citations if citation in retrieved_labels
    ]
    expected_missing = [
        citation for citation in question.expected_citations if citation not in retrieved_labels
    ]

    if expected_missing:
        notes.append(
            "expected citation retrieval miss: " + " | ".join(expected_missing)
        )
    if expected_retrieved:
        dropped = [
            citation
            for citation in expected_retrieved
            if citation not in set(result.cited_articles)
        ]
        if dropped:
            notes.append(
                "retrieved but dropped before final cited_articles: "
                + " | ".join(dropped)
            )

    if question.item_id == "SCN-005-Q3":
        sibling_groups = citation_stage_summary["sibling_article_groups"]
        if sibling_groups:
            group = sibling_groups[0]
            if len(group["context_ids"]) != len(group["grounded_context_ids"]):
                notes.append(
                    "same-article sibling subchunks were retrieved but only part of them survived grounded_context_ids"
                )

    if question.item_id in {"KLS-EVAL-010", "KLS-EVAL-017", "KLS-EVAL-058"}:
        selected_focuses = sorted(
            {
                focus
                for entry in selected_clause_entries
                for focus in entry.get("matched_focuses", [])
            }
        )
        notes.append(
            "selected clause focuses: " + (", ".join(selected_focuses) if selected_focuses else "(none)")
        )

    return notes


def analyze_question(
    question: DebugQuestion,
    *,
    top_k: int,
    ef_search: int,
    model_name: str | None,
) -> dict[str, Any]:
    retrieval_result: RetrievalResult = retrieve_law_chunks(
        query=question.question,
        top_k=top_k,
        ef_search=ef_search,
    )
    result = generate_grounded_answer(retrieval_result, model_name=model_name)
    retrieval_chunks = build_grounded_chunks(retrieval_result.chunks)

    query_text = normalize_text(retrieval_result.grounding_query)
    query_terms = text_to_query_terms(query_text)
    active_focuses = get_active_query_focuses(query_text)
    embedding_hints = matching_query_hints(query_text)
    embedding_text = build_query_embedding_text(query_text)

    chunk_debug_entries = []
    for retrieval_rank, chunk in enumerate(retrieval_chunks, start=1):
        entry = build_chunk_score_debug(query_text, query_terms, active_focuses, chunk)
        entry["retrieval_rank"] = retrieval_rank
        chunk_debug_entries.append(entry)
    chunk_debug_entries.sort(
        key=lambda item: (-item["chunk_score"], item["context_id"])
    )
    top_scored_context_ids = [item["context_id"] for item in chunk_debug_entries[:3]]

    selected_grounded_chunks = select_grounded_chunks_by_context_ids(
        retrieval_chunks,
        result.grounded_context_ids,
    )
    selected_points, selected_clause_entries, grounded_chunk_order = build_selected_clause_entries(
        query_text,
        selected_grounded_chunks,
    )
    signal_summary_points = build_possible_signal_summary_points(selected_grounded_chunks)
    key_point_sources = classify_key_point_sources(
        result.key_points,
        selected_clause_entries=selected_clause_entries,
        signal_summary_points=signal_summary_points,
    )
    citation_stage_summary = build_citation_stage_summary(
        result,
        retrieval_chunks,
        question.expected_citations,
    )
    diagnostics = build_item_diagnostics(
        question,
        retrieval_chunks=retrieval_chunks,
        result=result,
        selected_clause_entries=selected_clause_entries,
        citation_stage_summary=citation_stage_summary,
    )

    chunk_stage_lookup = {
        entry["context_id"]: {
            "raw_model_cited": entry["raw_model_cited"],
            "expanded_cited": entry["expanded_cited"],
            "postprocess_added": entry["postprocess_added"],
            "grounded": entry["grounded"],
            "cited_article_survived": entry["cited_article_survived"],
            "expected_citation": entry["expected_citation"],
        }
        for entry in citation_stage_summary["per_context"]
    }
    for rank, entry in enumerate(chunk_debug_entries, start=1):
        entry["chunk_score_rank"] = rank
        entry["selected_for_clause_ranking"] = entry["context_id"] in top_scored_context_ids
        entry["answer_stage"] = chunk_stage_lookup.get(entry["context_id"], {})

    return {
        "id": question.item_id,
        "source": question.source,
        "question": question.question,
        "top_k": top_k,
        "ef_search": ef_search,
        "expected_citations": question.expected_citations,
        "expected_points": question.expected_points,
        "grounding_query": retrieval_result.grounding_query,
        "embedding_query_hints": embedding_hints,
        "embedding_query_text": embedding_text,
        "active_query_focuses": active_focuses,
        "query_terms": query_terms,
        "answer_result": {
            "answer": result.answer,
            "key_points": result.key_points,
            "cautions": result.cautions,
            "raw_cited_context_ids": result.raw_cited_context_ids,
            "expanded_cited_context_ids": getattr(result, "expanded_cited_context_ids", []),
            "grounded_context_ids": result.grounded_context_ids,
            "cited_articles": result.cited_articles,
            "model_name": result.model_name,
            "citation_postprocess_additions": [
                serialize_citation_postprocess_addition(addition)
                for addition in getattr(result, "citation_postprocess_additions", [])
            ],
        },
        "retrieval_chunks": chunk_debug_entries,
        "grounded_chunk_score_order": grounded_chunk_order,
        "selected_clause_points": selected_points,
        "selected_clause_entries": selected_clause_entries,
        "signal_summary_candidates": signal_summary_points,
        "key_point_sources": key_point_sources,
        "citation_stage_summary": citation_stage_summary,
        "diagnostics": diagnostics,
    }


def format_item_report(item: dict[str, Any]) -> str:
    lines = [
        "=" * 88,
        f"{item['id']} ({item['source']})",
        "=" * 88,
        f"question: {item['question']}",
        f"top_k={item['top_k']} ef_search={item['ef_search']}",
        f"grounding_query: {item['grounding_query']}",
        f"embedding_query_hints: {item['embedding_query_hints'] or []}",
        f"active_query_focuses: {item['active_query_focuses'] or []}",
        f"raw_cited_context_ids: {item['answer_result']['raw_cited_context_ids']}",
        f"expanded_cited_context_ids: {item['answer_result']['expanded_cited_context_ids']}",
        f"grounded_context_ids: {item['answer_result']['grounded_context_ids']}",
        f"cited_articles: {item['answer_result']['cited_articles']}",
        "answer:",
        item["answer_result"]["answer"],
        "key_points:",
    ]
    for source in item["key_point_sources"]:
        source_label = source["source_type"]
        if source.get("citation_label"):
            source_label += f" [{source['citation_label']}]"
        lines.append(f"- {source['key_point']} ({source_label})")

    postprocess_additions = item["answer_result"]["citation_postprocess_additions"]
    if postprocess_additions:
        lines.append("citation_postprocess_additions:")
        for addition in postprocess_additions:
            lines.append(
                f"- rule={addition['rule']} added_ctx={addition['added_context_id']} "
                f"citation={addition['added_citation_label']} "
                f"source_ctx={addition.get('source_context_ids', [])} "
                f"query_patterns={addition.get('matched_query_patterns', [])}"
            )

    lines.append("selected_clauses:")
    for entry in item["selected_clause_entries"]:
        lines.append(
            f"- order={entry['order']} ctx={entry['context_id']} clause={entry['clause_index']} "
            f"score={entry['score']} citation={entry['citation_label']}"
        )
        lines.append(f"  text={entry['text']}")

    lines.append("retrieval_chunks_by_chunk_score:")
    for entry in item["retrieval_chunks"]:
        stage = entry["answer_stage"]
        lines.append(
            f"- retrieval_rank={entry['retrieval_rank']} chunk_rank={entry['chunk_score_rank']} "
            f"ctx={entry['context_id']} sim={entry['similarity']:.6f} "
            f"chunk_score={entry['chunk_score']:.2f} raw={stage.get('raw_model_cited')} "
            f"expanded={stage.get('expanded_cited')} "
            f"postprocess_added={stage.get('postprocess_added')} "
            f"grounded={stage.get('grounded')} cited={stage.get('cited_article_survived')} "
            f"expected={stage.get('expected_citation')} citation={entry['citation_label']}"
        )
        lines.append(f"  prompt_coverage={entry['prompt_coverage_clauses']}")
        for reason in entry["narrow_bias_reasons"]:
            lines.append(
                f"  chunk_narrow_bias rule={reason['rule']} delta={reason['delta']} "
                f"query_patterns={reason.get('matched_query_patterns', [])} "
                f"context_patterns={reason.get('matched_context_patterns', [])}"
            )
        for clause in entry["clause_candidates"][:5]:
            marker = ""
            for selected in item["selected_clause_entries"]:
                if (
                    selected["context_id"] == entry["context_id"]
                    and selected["clause_index"] == clause["clause_index"]
                ):
                    marker = f" selected_order={selected['order']}"
                    break
            lines.append(
                f"  - clause={clause['clause_index']} score={clause['score']}{marker} "
                f"focuses={clause['matched_focuses']} text={summarize_content(clause['text'], width=130)}"
            )
            for reason in clause["narrow_bias_reasons"]:
                lines.append(
                    f"    clause_narrow_bias rule={reason['rule']} delta={reason['delta']} "
                    f"query_patterns={reason.get('matched_query_patterns', [])} "
                    f"context_patterns={reason.get('matched_context_patterns', [])}"
                )

    if item["diagnostics"]:
        lines.append("diagnostics:")
        for note in item["diagnostics"]:
            lines.append(f"- {note}")

    sibling_groups = item["citation_stage_summary"]["sibling_article_groups"]
    if sibling_groups:
        lines.append("sibling_article_groups:")
        for group in sibling_groups:
            lines.append(
                f"- {group['law_name']} {group['article_ref']} "
                f"context_ids={group['context_ids']} raw={group['raw_cited_context_ids']} "
                f"expanded={group['expanded_cited_context_ids']} "
                f"grounded={group['grounded_context_ids']} cited_articles={group['cited_articles']}"
            )

    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    regression_ids = list(args.regression_ids)
    if args.include_default_regression:
        for item_id in DEFAULT_REGRESSION_IDS:
            if item_id not in regression_ids:
                regression_ids.append(item_id)

    questions = load_eval_questions(args.eval_dataset, list(args.eval_ids))
    questions.extend(load_scenario_questions(args.scenario_dataset, list(args.scenario_ids)))
    if regression_ids:
        questions.extend(load_scenario_questions(args.scenario_dataset, regression_ids))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{args.output_prefix}_{timestamp}.json"
    text_path = output_dir / f"{args.output_prefix}_{timestamp}.txt"

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for index, question in enumerate(questions, start=1):
        resolved_top_k = question.recommended_top_k or args.top_k
        print(
            f"[{index}/{len(questions)}] {question.item_id} start top_k={resolved_top_k} ef_search={args.ef_search}",
            flush=True,
        )
        try:
            item_result = analyze_question(
                question,
                top_k=resolved_top_k,
                ef_search=args.ef_search,
                model_name=args.model_name,
            )
        except Exception as exc:
            failures.append(
                {
                    "id": question.item_id,
                    "source": question.source,
                    "question": question.question,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            print(
                f"[{index}/{len(questions)}] {question.item_id} failed error={type(exc).__name__}",
                flush=True,
            )
            continue

        results.append(item_result)
        print(
            f"[{index}/{len(questions)}] {question.item_id} ok grounded={item_result['answer_result']['grounded_context_ids']}",
            flush=True,
        )

    payload = {
        "generated_at": datetime.now().isoformat(),
        "params": {
            "eval_ids": list(args.eval_ids),
            "scenario_ids": list(args.scenario_ids),
            "regression_ids": regression_ids,
            "top_k": args.top_k,
            "ef_search": args.ef_search,
            "model_name": args.model_name,
        },
        "results": results,
        "failures": failures,
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    rendered_reports = [format_item_report(item) for item in results]
    if failures:
        rendered_reports.append("=" * 88)
        rendered_reports.append("failures")
        rendered_reports.append("=" * 88)
        for failure in failures:
            rendered_reports.append(
                f"- {failure['id']} ({failure['source']}): {failure['error_type']}: {failure['error']}"
            )
    rendered_reports.append("")
    rendered_reports.append(f"json_report: {json_path}")
    text_path.write_text("\n\n".join(rendered_reports), encoding="utf-8")

    if rendered_reports:
        print("\n\n".join(rendered_reports))
    print(f"\ntext_report: {text_path}")
    print(f"json_report: {json_path}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
