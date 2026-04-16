from __future__ import annotations

import argparse
import json
import signal
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Mapping

from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.schemas.document_draft import LegalBasisInput
from backend.main import app
from backend.verify.document_draft_fixture_utils import (
    legal_basis_from_answer_response,
    stable_fixture_dumps,
    write_fixture_json,
)


SCENARIO_QUESTION_SET_PATH = REPO_ROOT / "eval/scenario_demo_question_sets_v1.json"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
DEFAULT_SCN_DEMO_TOP_K = 10
DEFAULT_EF_SEARCH = 100
DEFAULT_REQUEST_TIMEOUT_SECONDS = 180


@dataclass(frozen=True)
class RecaptureCase:
    question_id: str
    fixture_path: Path
    expected_citation_keywords: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class CapturedFixture:
    case: RecaptureCase
    question: str
    top_k: int
    ef_search: int
    legal_basis: dict[str, Any]
    changed: bool


SUPPORTED_CASES: dict[str, RecaptureCase] = {
    "SCN-004-Q2": RecaptureCase(
        question_id="SCN-004-Q2",
        fixture_path=(
            FIXTURE_DIR
            / "document_draft_scn004_answer_legal_basis_unfair_dismissal_brief.json"
        ),
        expected_citation_keywords=(
            ("근로기준법", "제23조"),
            ("근로기준법", "제26조"),
            ("근로기준법", "제27조"),
            ("근로기준법", "제28조"),
        ),
    ),
    "SCN-004-Q3": RecaptureCase(
        question_id="SCN-004-Q3",
        fixture_path=(
            FIXTURE_DIR
            / "document_draft_scn004_answer_legal_basis_wage_complaint.json"
        ),
        expected_citation_keywords=(
            ("근로기준법", "제36조"),
            ("퇴직급여", "제9조"),
        ),
    ),
}


class RecaptureError(RuntimeError):
    pass


class ProviderTimeoutError(TimeoutError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Recapture SCN-004 answer-derived LegalBasisInput fixtures. "
            "The default mode is dry-run preview; use --write to update files."
        )
    )
    parser.add_argument(
        "--scenario-id",
        action="append",
        choices=sorted(SUPPORTED_CASES),
        help="Supported SCN demo question id to recapture. Repeatable.",
    )
    parser.add_argument(
        "--all-scn004",
        action="store_true",
        help="Recapture all supported SCN-004 answer-derived fixtures.",
    )
    parser.add_argument(
        "--ef-search",
        type=int,
        default=DEFAULT_EF_SEARCH,
        help="ef_search value for /api/v1/answer. Defaults to 100.",
    )
    parser.add_argument(
        "--request-timeout-seconds",
        type=int,
        default=DEFAULT_REQUEST_TIMEOUT_SECONDS,
        help="Per-answer provider timeout. Use 0 to disable.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write recaptured JSON to the existing answer-derived fixture files.",
    )
    args = parser.parse_args()
    if args.all_scn004 and args.scenario_id:
        parser.error("--all-scn004 cannot be combined with --scenario-id.")
    if not args.all_scn004 and not args.scenario_id:
        parser.error("one of --all-scn004 or --scenario-id is required.")
    return args


@contextmanager
def request_timeout(seconds: int) -> Iterator[None]:
    if seconds <= 0:
        yield
        return

    def raise_timeout(_signum: int, _frame: object) -> None:
        raise ProviderTimeoutError(
            f"/api/v1/answer call exceeded {seconds} seconds"
        )

    previous_handler = signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)


def load_scn004_questions() -> dict[str, Mapping[str, Any]]:
    with SCENARIO_QUESTION_SET_PATH.open(encoding="utf-8") as question_file:
        dataset = json.load(question_file)
    for scenario in dataset["scenarios"]:
        if scenario["scenario_id"] == "SCN-004":
            return {
                question["id"]: question
                for question in scenario["questions"]
                if question["id"] in SUPPORTED_CASES
            }
    raise RecaptureError("SCN-004 questions not found in scenario demo set.")


def selected_cases(args: argparse.Namespace) -> list[RecaptureCase]:
    if args.all_scn004:
        return [SUPPORTED_CASES[question_id] for question_id in sorted(SUPPORTED_CASES)]
    return [SUPPORTED_CASES[question_id] for question_id in args.scenario_id]


def call_answer_api(
    client: TestClient,
    *,
    question_id: str,
    question: str,
    top_k: int,
    ef_search: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    payload = {
        "query": question,
        "top_k": top_k,
        "ef_search": ef_search,
    }
    try:
        with request_timeout(timeout_seconds):
            response = client.post("/api/v1/answer", json=payload)
    except ProviderTimeoutError:
        raise
    except Exception as exc:  # pragma: no cover - depends on provider/runtime state
        raise RecaptureError(f"{question_id}: /api/v1/answer failed: {exc!r}") from exc

    if response.status_code != 200:
        raise RecaptureError(
            f"{question_id}: /api/v1/answer returned {response.status_code}: "
            f"{response.text[:2000]}"
        )
    return response.json()


def assert_expected_citations(
    case: RecaptureCase,
    cited_articles: list[str],
) -> None:
    missing_keywords = [
        keywords
        for keywords in case.expected_citation_keywords
        if not any(
            all(keyword in article for keyword in keywords)
            for article in cited_articles
        )
    ]
    if missing_keywords:
        expected = ["/".join(keywords) for keywords in missing_keywords]
        raise RecaptureError(
            f"{case.question_id}: missing expected citation keywords {expected}; "
            f"actual cited_articles={cited_articles!r}"
        )


def assert_safe_legal_basis(case: RecaptureCase, legal_basis: dict[str, Any]) -> None:
    LegalBasisInput.model_validate(legal_basis)

    cited_articles = list(legal_basis["cited_articles"])
    source_context_ids = list(legal_basis["source_context_ids"])
    retrieved_chunks = list(legal_basis["retrieved_chunks"])
    if not cited_articles:
        raise RecaptureError(f"{case.question_id}: cited_articles must not be empty.")
    if not source_context_ids:
        raise RecaptureError(
            f"{case.question_id}: source_context_ids must not be empty."
        )
    if not retrieved_chunks:
        raise RecaptureError(f"{case.question_id}: retrieved_chunks must not be empty.")

    source_context_id_set = set(source_context_ids)
    retrieved_context_ids = {chunk["context_id"] for chunk in retrieved_chunks}
    if retrieved_context_ids != source_context_id_set:
        raise RecaptureError(
            f"{case.question_id}: retrieved_chunks must match grounded "
            f"source_context_ids; source={source_context_ids!r}, "
            f"retrieved={sorted(retrieved_context_ids)!r}"
        )

    assert_expected_citations(case, cited_articles)


def load_existing_fixture(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def capture_fixture(
    client: TestClient,
    case: RecaptureCase,
    question_info: Mapping[str, Any],
    *,
    ef_search: int,
    timeout_seconds: int,
) -> CapturedFixture:
    question = str(question_info["question"])
    top_k = int(question_info.get("recommended_top_k") or DEFAULT_SCN_DEMO_TOP_K)
    answer_response = call_answer_api(
        client,
        question_id=case.question_id,
        question=question,
        top_k=top_k,
        ef_search=ef_search,
        timeout_seconds=timeout_seconds,
    )
    legal_basis = legal_basis_from_answer_response(answer_response)
    assert_safe_legal_basis(case, legal_basis)
    existing_fixture = load_existing_fixture(case.fixture_path)
    return CapturedFixture(
        case=case,
        question=question,
        top_k=top_k,
        ef_search=ef_search,
        legal_basis=legal_basis,
        changed=existing_fixture != legal_basis,
    )


def print_preview(captured: CapturedFixture) -> None:
    fixture_path = captured.case.fixture_path.relative_to(REPO_ROOT)
    print("=" * 80)
    print(f"dry-run {captured.case.question_id}")
    print(f"fixture: {fixture_path}")
    print(f"payload: top_k={captured.top_k} ef_search={captured.ef_search}")
    print(f"changed: {captured.changed}")
    print(f"cited_articles: {captured.legal_basis['cited_articles']}")
    print(f"source_context_ids: {captured.legal_basis['source_context_ids']}")
    print(f"retrieved_chunks: {len(captured.legal_basis['retrieved_chunks'])}")
    print("-" * 80)
    print(stable_fixture_dumps(captured.legal_basis), end="")


def main() -> int:
    args = parse_args()
    questions_by_id = load_scn004_questions()
    cases = selected_cases(args)
    missing_questions = [
        case.question_id for case in cases if case.question_id not in questions_by_id
    ]
    if missing_questions:
        raise RecaptureError(
            "Question ids missing from scenario demo set: "
            + ", ".join(missing_questions)
        )

    client = TestClient(app)
    captured_fixtures = [
        capture_fixture(
            client,
            case,
            questions_by_id[case.question_id],
            ef_search=args.ef_search,
            timeout_seconds=args.request_timeout_seconds,
        )
        for case in cases
    ]

    if args.write:
        for captured in captured_fixtures:
            if not captured.changed:
                print(
                    f"unchanged {captured.case.question_id}: "
                    f"{captured.case.fixture_path.relative_to(REPO_ROOT)}"
                )
                continue
            write_fixture_json(captured.case.fixture_path, captured.legal_basis)
            print(
                f"wrote {captured.case.question_id}: "
                f"{captured.case.fixture_path.relative_to(REPO_ROOT)}"
            )
        return 0

    for captured in captured_fixtures:
        print_preview(captured)
    print("=" * 80)
    print("dry-run only; rerun with --write to update fixture files.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ProviderTimeoutError, RecaptureError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
