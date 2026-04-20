# K-Labor Shield

외국인 근로자를 포함한 취약 노동자를 위한 노동권 보호 통합 AI MVP입니다.  
현재 저장소 기준으로는 `retrieval + grounded answer generation + RAG refinement + SCN-004 문서 초안 backend + SCN-004 After frontend demo flow + presentation-local fixed answer preset + demo preflight + item-level eval evidence`까지 구현된 상태입니다.
`SCN-004` QA 정합성 검증, content output 확인, browser rehearsal, final demo preflight까지 통과한 상태입니다.
`SCN-001-BRIDGE-DEMO`는 Before/Bridge handoff 설명용 answer-only preset으로 준비되어 있고, 실제 SCN-001 frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 진행합니다.
`SCN-005`는 현재 frontend preset UI에서 제외되어 있으며, 후속 확장 후보로만 유지합니다.

## 현재 상태

기준일: `2026-04-20`

- source of truth: `backend/data/law_chunks/all_chunks.json`
- `selected_as_of = 2026-04-11`
- current live chunks: `1722`
- PostgreSQL `law_chunks`: `1722`
- embedding populated: `1722 / 1722`
- vector dimension: `768`
- HNSW index: `idx_law_chunks_embedding`
- alembic head: `20260413_000003`
- answer model: `gemini-2.5-flash`
- embedding model: `gemini-embedding-001`
- frontend: Next.js `16.2.4`, React `19.2.5`
- current phase: SCN-004 demo freeze 유지, 제출 전 재현성 확인, 팀원 Before/Bridge contract 확인 대기

핵심 상태:

- retrieval MVP 완료
- grounded answer generation MVP 완료
- `cited_articles` 강제 및 retrieval 밖 citation 금지 완료
- answer grounding 검증, hard timeout, eval 안정화 완료
- scenario expansion 검증 완료
- RAG refinement landing 완료 (`expected_point_strict_coverage = 137/153`, `16` partial)
- full 60 answer evidence report 완료 (`PASS=44`, `PARTIAL=16`, `FAIL=0`, expected point coverage `135/153`)
- `POST /api/v1/documents/draft` SCN-004 deterministic draft MVP 완료
- frontend `/after -> /after/result -> /after/intake -> /after/draft` API-connected flow 구현 완료
- frontend Phase 3 A/B(copy/print)까지 반영. Phase 3C 이후 확장성 작업은 데모 리스크 때문에 보류
- SCN-004 draft navigation race 수정 완료
- SCN-004 free input document eligibility guard 완료
- SCN-001/004 presentation-local fixed answer preset architecture 완료
- `scripts/demo_preflight.sh` 추가 및 final pass 확인 완료
- SCN-004-DEMO-FREEZE fixed answer와 2종 document draft output 정합성 확인 완료

진화 기록:

- 2026-04-17 기준으로 RAG refinement, SCN-004 document draft backend, SCN-004 After frontend Phase 3A/B, content QA, manual browser rehearsal까지 완료됐다.
- 2026-04-20에는 위 기준을 유지하면서 presentation-local preset, free-input guard, preflight script, item-level answer evidence report를 추가해 MVP 제출 근거를 보강했다.

## 지금까지 완료된 것

### 1. Data / DB / Embedding

- 법령 청킹 파이프라인 baseline 완료
- `backend/data/law_chunks/all_chunks.json` 운영 기준선 확정
- PostgreSQL + pgvector 로컬 DB 구성 완료
- `law_chunks` ingestion 완료
- embedding `1722 / 1722` 완료
- HNSW 인덱스 구성 완료

### 2. Retrieval

- `POST /api/v1/retrieve` 구현 완료
- pgvector cosine retrieval 구현 완료
- retrieval eval 기준:
  - `hit@1 = 51/60 (85.00%)`
  - `hit@3 = 59/60 (98.33%)`
  - `hit@5 = 60/60 (100.00%)`

### 3. Answer Generation

- `POST /api/v1/answer` 구현 완료
- retrieval 결과를 사용하는 grounded answer flow 구현 완료
- `cited_articles` 포함 응답 강제
- retrieval 결과 밖 citation 인용 금지
- answer text explicit citation grounding 검증 구현
- timeout / provider failure / malformed response 안정화 완료

현재 full 60 answer eval 기준:

- `items_answered = 60/60`
- `JSON/schema failure = 0`
- `timed_out_ids = []`
- `citation_grounding_clean = 60/60`
- `gold_citation_hit = 60/60`
- `expected_point_strict_coverage = 137/153`
- `failures_or_partial_coverage = 16`

2026-04-20 item-level answer evidence 기준:

- `PASS = 44`
- `PARTIAL = 16`
- `FAIL = 0`
- `expected point coverage = 135/153`
- `citation grounding violation = 0`
- `invalid raw / grounded context id = 0`
- `timeout / provider / schema error = 0`

`PARTIAL` 16건은 retrieval / citation / grounding failure가 아니라 expected point 일부 누락이다. MVP 기준으로는 acceptable이며, 후속 answer quality tuning 후보로 분리한다.

### 4. Document Draft

- `POST /api/v1/documents/draft` 구현 완료
- `SCN-004` 문서 타입 2개 지원:
  - `labor_office_wage_complaint`
  - `labor_commission_unfair_dismissal_brief`
- deterministic template 기반으로 facts / legal_basis / request / evidence_checklist / missing_fields / cautions / rendered_text 반환
- request로 받은 `/api/v1/answer` legal basis 안에서만 citation 사용
- answer-derived legal basis fixture와 manual fixture smoke 구현 완료

### 5. Frontend

- `frontend/`에 Next.js App Router 기반 SCN-004 After demo 구현
- 구현 route:
  - `/`
  - `/after`
  - `/after/result`
  - `/after/intake`
  - `/after/draft`
- 실제 backend API 연동:
  - `/api/v1/answer`
  - `/api/v1/documents/draft`
- route guard, loading/error state, focus management, skip link, cited_articles/grounding guard 구현
- 문서 초안 복사 및 인쇄 기능 구현
- 증거 체크리스트는 화면 내 로컬 상태만 사용하며 저장하지 않음
- `sessionStorage` / `localStorage` backup-restore는 개인정보/데모 안정성 리스크 때문에 구현하지 않음

### 6. Scenario Expansion

현재 시나리오 기준선:

- `SCN-001`: covered
  - 외국인 근로자 계약/기숙사/차별/사업장 변경
  - Full 단일 질의는 `top_k=10`, `ef_search=100` demo path에서 운영
  - 현재 frontend에서는 `SCN-001-BRIDGE-DEMO` answer-only preset으로 Before/Bridge handoff 설명만 제공
- `SCN-002`: partial
  - 최저임금/수습 꼼수 설명형은 가능
  - 현재는 설명형 Before 데모 범위로 고정
- `SCN-003`: covered
  - 장애인 관련 조문 9개 최소 추가 + 재임베딩 완료
- `SCN-004`: covered
  - 카톡 해고/임금·퇴직금 체불 After frontend demo 구현 완료
- `SCN-005`: covered
  - 육아휴직/가족돌봄휴가 부당 거절 answer smoke 가능
  - 현재 frontend preset UI에서는 제외
  - After frontend / 문서 타입 확장은 SCN-004 freeze 기준을 유지한 별도 패치에서만 진행 가능

## 현재 데모 자산

### SCN-004 After frontend

- [docs/planning/14_frontend_implementation_handoff.md](docs/planning/14_frontend_implementation_handoff.md)
- [frontend/](frontend/)

주요 흐름:

1. `/after`에서 상황 진술 입력 또는 presentation-local preset 사용
2. `/after/result`에서 grounded answer와 인용 조문 확인
3. 문서 타입 선택 후 `/after/intake`에서 선택적 사건 정보 입력
4. `/after/draft`에서 진정서 또는 이유서 초안 확인, 복사, 인쇄

현재 preset:

- `SCN-001-BRIDGE-DEMO`: Before/Bridge handoff 설명용 answer-only preset
- `SCN-004-DEMO-FREEZE`: main demo / document draft freeze용 preset
- SCN-005 preset은 현재 UI에서 제외

### 시나리오 문서

- [docs/planning/12_scenario_expansion_plan.md](docs/planning/12_scenario_expansion_plan.md)

### 시나리오 질문 세트

- [eval/scenario_demo_question_sets_v1.json](eval/scenario_demo_question_sets_v1.json)

포함 시나리오:

- `SCN-001`
- `SCN-004`
- `SCN-005`

이 파일은 baseline 60문항 eval과 별개로, 발표 시연이나 retrieval/answer smoke용으로 바로 재사용할 수 있게 만든 질문 세트입니다.

## 다음 작업

현재 우선순위는 아래 순서입니다.

### 1. SCN-004 demo freeze 유지

- backend response schema와 frontend type/interface 정합성은 통과 상태로 유지
- `/api/v1/answer -> /api/v1/documents/draft` legal basis 전달 경로는 통과 상태로 유지
- SCN-004-DEMO-FREEZE fixed answer는 `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]` 기준으로 유지
- document draft 2종은 `missing_legal_basis=[]` 기준으로 유지
- 제출 전 직접 URL 접근, API 실패, 빈 필드, citation 없음 상태, desktop/mobile 기본 레이아웃만 재확인

### 2. 데모 운영 고정

- 발표용 main path는 `SCN-004-DEMO-FREEZE` After document draft demo로 고정
- exact preset path는 fixed answer fixture를 사용해 `/api/v1/answer`를 호출하지 않음
- preset modified path는 `top_k=10`, `ef_search=100`으로 live `/api/v1/answer` 호출
- 일반 자유 입력은 `top_k=5`, `ef_search=100` 유지
- SCN-004 범위 밖 자유 입력은 answer-only로 처리
- `/before`, `/bridge`, Recovery는 이번 frontend demo 범위에서 확장하지 않음

### 3. 선택적 후속

- full 60 answer evidence `PARTIAL` 16건에 대한 answer-side surface / completeness 보강
- `SCN-001 Full`은 `top_k=10`, `ef_search=100` demo path로만 운영
- `SCN-002`는 설명형 Before 데모 범위 유지
- `SCN-005` After frontend / 문서 타입 확장은 SCN-004 freeze 기준을 유지한 별도 패치에서만 진행 가능
- `SCN-001` 문서 타입과 `Before -> Bridge -> After` frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 검토

## 저장소 구조

| Path | Role |
|---|---|
| `backend/` | FastAPI, RAG, DB, verification |
| `frontend/` | Next.js SCN-004 After demo UI |
| `scripts/` | 법령 전처리 / chunking pipeline |
| `data/legalize-kr/` | 법령 원본 submodule |
| `backend/data/law_chunks/` | chunk 산출물 및 `all_chunks.json` |
| `docs/planning/` | 기준 설계 문서 |
| `docs/ops/` | 운영 / 상태 문서 |
| `eval/` | baseline eval, scenario demo question sets |

## 빠른 참고 문서

작업을 이어갈 때 우선 보면 되는 문서:

1. [docs/ops/runbook.md](docs/ops/runbook.md)
2. [docs/planning/14_frontend_implementation_handoff.md](docs/planning/14_frontend_implementation_handoff.md)
3. [docs/planning/13_document_draft_plan.md](docs/planning/13_document_draft_plan.md)
4. [docs/planning/00_project_overview.md](docs/planning/00_project_overview.md)
5. [docs/ops/task6_answer_generation_status.md](docs/ops/task6_answer_generation_status.md)
6. [docs/planning/02_rag_strategy.md](docs/planning/02_rag_strategy.md)
7. [docs/planning/12_scenario_expansion_plan.md](docs/planning/12_scenario_expansion_plan.md)

## Freeze QA 순서

문서/QA 작업의 기본 검증 순서는 아래로 고정합니다.

발표 직전 기본 preflight:

```bash
bash scripts/demo_preflight.sh
```

이 script는 `main == origin/main`, PostgreSQL readiness, conda env activation, backend import, document draft smoke, frontend build, WSL Playwright Chromium smoke를 확인한다. DB / dev server를 자동 실행하거나 full 60 eval을 실행하지 않는다.

### 1. backend import

```bash
conda activate law_main_road
python -c "from backend.main import app; print('import_ok')"
```

### 2. document draft smoke

```bash
conda activate law_main_road
python backend/verify/check_document_draft.py
```

### 3. frontend build

```bash
cd frontend
npm run build
```

### 4. optional RAG answer smoke

RAG / answer / retrieval behavior를 수정했거나, demo citation survival을 다시 확인해야 할 때만 실행합니다.

```bash
conda activate law_main_road
python backend/verify/check_answer_generation.py "해고를 당했는데 서면통지는 없고 30일 전에 예고도 못 받았습니다. 부당해고 구제신청은 어디에 언제까지 할 수 있나요?" --top-k 10 --ef-search 100
```

full 60 retrieval / answer eval은 `backend/app/services/retrieval.py`, `backend/app/services/answer_generation.py`, embedding behavior, DB contents, API response contract가 바뀐 경우에 우선 검토합니다.

## SCN-004 QA 기록

2026-04-20 final demo preflight / dry-run에서 확인한 범위:

- `bash scripts/demo_preflight.sh` 통과, exit code `0`
- PostgreSQL readiness, backend import, document draft smoke, frontend build, WSL Playwright Chromium smoke 통과
- `http://localhost:3000/after` 기준 browser dry-run 통과
- `SCN-004-DEMO-FREEZE` fixed path는 `/api/v1/answer` 호출 0회
- `/after/result`: `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`, 문서 타입 2개 표시
- 임금체불 진정서 draft: `source_context_ids=[5, 10]`, `cited_articles=2`, `missing_legal_basis=[]`
- 부당해고 이유서 draft: `source_context_ids=[1, 2, 3, 4]`, `cited_articles=4`, `missing_legal_basis=[]`
- copy 성공, headless browser에서 `window.print()` 호출 확인
- `다른 문서 타입으로 생성하기` -> `/after/result` 복귀와 answer state 유지 확인
- `SCN-001-BRIDGE-DEMO`: fixed answer-only, `/api/v1/answer` 호출 0회, 문서 선택 UI 없음
- direct URL guard: `/after/result`, `/after/intake`, `/after/draft` state 없음 -> `/after`
- Web Storage: `localStorage.length=0`, `sessionStorage.length=0`

2026-04-17 기준 SCN-004 QA/rehearsal에서 확인한 초기 범위:

- backend import smoke 통과: `import_ok`
- `python backend/verify/check_document_draft.py` 통과
  - `manual_wage_complaint`
  - `manual_unfair_dismissal_brief`
  - `answer_derived_wage_complaint`
  - `answer_derived_unfair_dismissal_brief`
- frontend `npm run build` 통과
  - `npm`이 PATH에 없을 때는 nvm Node path를 먼저 로드해야 함
  - build route: `/`, `/after`, `/after/result`, `/after/intake`, `/after/draft`
- dev server route smoke 통과
  - backend: `http://127.0.0.1:8000`
  - frontend: `http://127.0.0.1:3000`
  - `/health`, `/`, `/after`, `/after/result`, `/after/intake`, `/after/draft` HTTP 200
- live API smoke 통과
  - SCN-004 preset `/api/v1/answer`: `top_k=10`, `ef_search=100`, `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`, `retrieved_chunks=10`
  - `key_points`에 정당한 이유, 30일 전 예고/통상임금, 서면통지, 노동위원회, 3개월 이내, 14일 금품청산 내용 표시
  - `labor_office_wage_complaint` draft: HTTP 200, `rendered_text` 974자, `missing_fields=12`, `cautions=6`, `evidence_checklist=5`, `cited_articles=2`
  - `labor_commission_unfair_dismissal_brief` draft: HTTP 200, `rendered_text` 1123자, `missing_fields=12`, `cautions=5`, `evidence_checklist=5`, `cited_articles=4`
  - 두 draft 모두 `missing_legal_basis=[]`
- schema / guard / copy / print code path 확인
  - answer / draft backend schema와 frontend type 일치
  - `cited_articles`, `grounded_context_ids` guard 확인
  - `buildLegalBasis()`, `buildCaseIntake()` 전달 경로 확인
  - `navigator.clipboard.writeText`, `window.print()` 연결 확인
  - `localStorage`, `sessionStorage` 사용 없음 확인
- manual browser rehearsal 통과
  - `/after -> /after/result -> /after/intake -> /after/draft` runtime flow 확인
  - SCN-004 preset, result 표시, 문서 타입 선택, 빈 값 또는 일부 값 intake submit 확인
  - draft 표시, copy, print, direct URL guard 확인

제한 사항:

- 2026-04-17에는 Playwright / Cypress / Puppeteer 및 Chrome / Chromium 기반 자동 DOM click smoke를 미수행했다.
- 2026-04-20 이후 WSL Playwright Chromium 기반 smoke와 browser dry-run을 통과했다.
- headless Playwright에서는 실제 OS print dialog가 아니라 `window.print()` 호출만 확인한다. 발표 브라우저에서 실제 dialog는 육안 확인한다.
- direct URL guard는 client-side `router.replace` 방식이라 HTTP GET만으로는 redirect를 검증하지 않는다.

## 실행 예시

### backend

```bash
conda activate law_main_road
uvicorn backend.main:app --reload
```

### frontend

```bash
cd frontend
npm run build
npm run dev
```

### baseline retrieval eval

```bash
conda activate law_main_road
python eval/run_retrieval_eval.py --top-k 5 --ef-search 100 --show-failures 10
```

### baseline answer eval

```bash
conda activate law_main_road
python eval/run_answer_eval.py --top-k 5 --ef-search 100 --limit 60 --show-failures 20
```

## 주의

- `data/legalize-kr/`는 직접 수정하지 않습니다.
- frozen corpus 기준은 현재 `selected_as_of = 2026-04-11`입니다.
- raw source HEAD가 더 최신이어도, snapshot 재선정 없이 섞어 반영하면 안 됩니다.
- planning 문서의 오래된 숫자나 초안 조문은 항상 실제 `all_chunks.json`과 DB 상태로 재검증하는 것이 원칙입니다.
- frontend는 개인정보 저장을 피하기 위해 raw `user_statement`, `answer_response`, `case_intake`, `draft_response`를 Web Storage에 저장하지 않습니다.
- `SCN-004` QA 정합성 검증, content output 확인, manual browser rehearsal은 통과 상태입니다.
- 이후 기능 확장 후보는 `SCN-005` After frontend / 문서 타입입니다.
- `SCN-001` frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 진행합니다.
