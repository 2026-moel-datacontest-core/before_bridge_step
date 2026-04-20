# AGENTS.md — law_main_road

## Purpose

실행 중심 작업 가이드.  
전역 규칙은 `CLAUDE.md`, 상세 설계는 `docs/planning/*`, 영역별 규칙은 하위 `CLAUDE.md` 참조.

## Current Phase

기준일: `2026-04-20`

- RAG refinement landing 완료
- SCN-004 document draft backend 완료
- SCN-004 After frontend 4-route flow 완료
- Phase 3A/B 완료: rendered_text copy, browser print, print disclaimer
- SCN-004 QA 정합성 검증, content output 확인, manual browser rehearsal 통과
- SCN-004 draft navigation race 수정 완료
- SCN-004 free input document eligibility guard 완료
- SCN-001/004 presentation-local fixed answer preset architecture 완료
- demo preflight script와 full 60 answer evidence report 추가 완료
- 현재 작업 중심은 **SCN-004 demo freeze 유지와 제출 전 재현성 확인**
- `SCN-001-BRIDGE-DEMO`는 Before/Bridge handoff 설명용 answer-only preset
- `SCN-004-DEMO-FREEZE`는 main demo / document draft freeze용 preset
- SCN-005는 현재 frontend preset UI에서 제외하고 후속 확장 후보로만 유지
- SCN-001 frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 진행
- 현재 source of truth는 `backend/data/law_chunks/all_chunks.json`
- current live corpus: `1722` chunks, `selected_as_of = 2026-04-11`

Evolution note:

- 2026-04-17 기준 상태는 RAG refinement, SCN-004 document draft backend, SCN-004 After frontend Phase 3A/B, content QA, manual browser rehearsal 완료였다.
- 2026-04-20에는 위 상태를 흔들지 않고 presentation-local preset, preflight, free-input guard, eval evidence report를 추가해 MVP 제출 기준을 보강했다.

## Read Order

1. `CLAUDE.md`
2. related file under `docs/planning/`
3. local `CLAUDE.md` in current directory
4. existing code
5. this file

## Repo Layout

| Path | Use |
|---|---|
| `backend/` | FastAPI, retrieval / answer / document draft, LLM routing, DB |
| `frontend/` | Next.js SCN-004 After demo UI |
| `scripts/` | preprocessing / chunking pipeline |
| `data/legalize-kr/` | source submodule |
| `backend/data/law_chunks/` | preprocessing outputs |
| `docs/` | planning / product / demo / ops |
| `eval/` | eval set / metrics |

## Environment

| Item | Value |
|---|---|
| OS | WSL Ubuntu |
| Python env | conda |
| Main env | project-specific env, not `base` |
| Package manager | `pip` inside conda env |
| Node | frontend only |
| Backend DB | PostgreSQL + pgvector |
| Frontend API base | `NEXT_PUBLIC_API_BASE_URL`, default `http://localhost:8000` |

## Setup

### Python / repo
```bash
conda activate law_main_road
git status
```

### if repo is not initialized

```bash
git init
mkdir -p data scripts backend/data/law_chunks
git submodule add https://github.com/legalize-kr/legalize-kr.git data/legalize-kr
git submodule update --init --recursive
pip install python-frontmatter
```

## Core Commands

### QA quick checks

```bash
python -c "from backend.main import app; print('import_ok')"
python backend/verify/check_document_draft.py
cd frontend
npm run build
```

### chunking pipeline

```bash
python scripts/step1_select_effective_snapshots.py --as-of 2026-04-10
python scripts/step4_chunk_articles.py
python scripts/step5_normalize.py
python scripts/step6_split_long_articles.py
python scripts/step7_finalize_metadata.py
python scripts/step8_dedupe_and_validate.py
python scripts/step9_quality_check.py
python scripts/step10_finalize.py
```

### backend

```bash
uvicorn backend.main:app --reload
```

### frontend

```bash
cd frontend
npm install
npm run dev
```

## Current Implemented API

| Method | Path | Status |
|---|---|---|
| `POST` | `/api/v1/retrieve` | implemented |
| `POST` | `/api/v1/answer` | implemented |
| `POST` | `/api/v1/documents/draft` | implemented |

Runtime defaults:

* general `/api/v1/retrieve` and `/api/v1/answer`: `top_k=5`, `ef_search=100`
* SCN demo / scenario smoke: explicitly send `top_k=10`, `ef_search=100`
* answer model default: `gemini-2.5-flash`
* embedding model default: `gemini-embedding-001`, `768` dimensions
* `SCN-001 Full` selective decomposition only triggers on the demo path when `top_k >= 8` and marker rules match

## Current Frontend Scope

Implemented routes:

* `/`
* `/after`
* `/after/result`
* `/after/intake`
* `/after/draft`

Implemented integration:

* `/after` uses fixed `AnswerResponse` fixture for unchanged presentation preset path, otherwise calls `POST /api/v1/answer`
* `/after/result` guards draft flow when `cited_articles` or `grounded_context_ids` is empty and filters SCN-004 document types by answer evidence
* `/after/intake` sends only `buildCaseIntake()` and `buildLegalBasis()` output to `POST /api/v1/documents/draft`
* `/after/draft` displays `rendered_text`, `missing_fields`, `cautions`, `evidence_checklist`, `cited_articles`, source context ids, copy, and print
* state is React Context + `useReducer` memory state only

## Working Rules

* 작은 단위로 수정
* 관련 문서 먼저 읽고 작업
* 기존 구조 존중
* 불필요한 전역 리팩토링 금지
* 스키마 변경은 최소화
* 문서와 코드 정합성 유지
* 불확실하면 TODO 또는 note 남기기

## Chunking Rules

* Step order fixed: `1 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10`
* Step 2, 3 do not run separately
* Step 1 / 4 / 7 are patched versions
* pipeline 재실행 command는 `--as-of 2026-04-10` 기준으로 재현성 우선
* 현재 frozen output metadata 기준은 `selected_as_of = 2026-04-11`
* Step 1~10 baseline output은 `1713` chunks
* current live source of truth는 SCN-003 최소 보강 `+9` chunks 포함 `1722` chunks
* Step 9 실패 시 다음 단계 진행 금지
* `article_ordinal` 보존
* `data/legalize-kr/` 직접 수정 금지
* `backend/data/law_chunks/` 직접 수정 금지. 필요한 경우 pipeline 또는 명시된 fixture/data 보강 절차로만 갱신

## Backend Rules

* HIGH / MEDIUM 민감 작업: local LLM 우선
* 현재 implemented answer / embedding path는 Vertex AI Gemini 기준
* 법률 답변에는 `cited_articles` 필요
* 검색 결과에 없는 조문 인용 금지
* API contract 임의 변경 금지
* `/api/v1/answer` contract를 문서 초안 용도로 확장하지 않음
* `/api/v1/documents/draft`는 request의 `legal_basis` 안에 있는 근거만 사용
* draft service는 retrieval / answer_generation service를 직접 호출하지 않음
* 사용자가 입력하지 않은 사실은 단정하지 않고 placeholder 또는 `missing_fields`로 남김
* SCN-005 After 문서 타입 확장은 SCN-004 freeze 기준을 유지한 별도 패치에서 진행 가능
* SCN-001 문서 타입 / Before-Bridge-After 확장은 팀원 Before / Bridge 코드와 contract 확인 후 검토

## Frontend Rules

* Korean primary, English secondary
* demo stability first
* backend schema 확인 없이 응답 필드 가정 금지
* 현재 구현 범위는 SCN-004 After 4-route flow
* `/before`, `/bridge`, Recovery 본 구현은 현재 freeze 범위에서 진행하지 않음
* 현재 SCN-004 demo freeze 유지 작업과 SCN-005 문서 타입 frontend 확장을 한 패치에 섞지 않음
* SCN-005 After frontend / 문서 타입 확장은 SCN-004 freeze 기준을 유지한 별도 패치에서 진행 가능
* SCN-001 `Before -> Bridge -> After` frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 별도 단계에서 검토
* raw `user_statement`, `answer_response`, `case_intake`, `draft_response`는 Web Storage에 저장하지 않음
* presentation preset exact path는 fixed answer fixture를 사용하고 `/api/v1/answer`를 호출하지 않음
* presentation preset modified path는 `top_k=10`, 자유 입력은 `top_k=5`, 항상 `ef_search=100`
* `SCN-001-BRIDGE-DEMO`는 fixed/live 여부와 관계없이 answer-only
* `SCN-004-DEMO-FREEZE`와 SCN-004 free input만 document eligibility guard 통과 시 draft flow 허용

## Git Rules

| Branch      | Use                 |
| ----------- | ------------------- |
| `main`      | stable / submission |
| `dev`       | integration         |
| `feature/*` | focused task branch |

### commit style

* small commits
* prefix with phase when relevant
* use: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Do Not

* edit `data/legalize-kr/`
* revive deprecated draft scripts
* mix SCN-004 freeze QA changes with feature expansion in one patch
* collect personal identity info
* change planning docs in-place without reason
* mix unrelated changes in one patch
* change API contracts to make frontend easier without backend/schema review
* run broad full eval for doc-only changes unless RAG / answer / retrieval behavior changed
* store raw case facts or full answer/draft payloads in browser storage

## Preferred 3-Pass Task Flow

1. code inspector pass: read relevant planning docs, local `CLAUDE.md`, and actual code paths before deciding status
2. doc updater pass: update the smallest valid document scope to match current code and freeze policy
3. verifier pass: check diff, run relevant smoke/build command, and report any command that was skipped or blocked

For current QA/doc tasks, prefer:

```bash
bash scripts/demo_preflight.sh
```

For focused checks, use:

```bash
python backend/verify/check_document_draft.py
cd frontend && npm run build
```

Run retrieval / answer full 60 only when `backend/app/services/retrieval.py`, `backend/app/services/answer_generation.py`, embedding behavior, DB contents, or API response contract changed. Use `eval/run_answer_evidence_report.py` when item-level PASS / PARTIAL / FAIL evidence is needed; do not add it to `scripts/demo_preflight.sh`.

## References

* `docs/planning/00_project_overview.md`
* `docs/planning/02_rag_strategy.md`
* `docs/planning/03_chunking_pipeline.md`
* `docs/planning/04_architecture.md`
* `docs/planning/05_eval_plan.md`
* `docs/planning/08_frontend_app_plan.md`
* `docs/planning/09_backend_embedding_plan.md`
* `docs/planning/10_backend_retrieval_plan.md`
* `docs/planning/12_scenario_expansion_plan.md`
* `docs/planning/13_document_draft_plan.md`
* `docs/planning/14_frontend_implementation_handoff.md`
* `docs/ops/task6_answer_generation_status.md`
