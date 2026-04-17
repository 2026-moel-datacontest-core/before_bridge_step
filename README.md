# K-Labor Shield

외국인 근로자를 포함한 취약 노동자를 위한 노동권 보호 통합 AI MVP입니다.  
현재 저장소 기준으로는 `retrieval + grounded answer generation + RAG refinement + SCN-004 문서 초안 backend + SCN-004 After frontend demo flow`까지 구현된 상태입니다.
즉시 다음 단계는 `SCN-004` QA 정합성 검증과 demo rehearsal입니다.
SCN-004 QA/freeze 확인 후 다음 확장 후보는 `SCN-005` After frontend / 문서 타입입니다.
`SCN-001` frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 진행합니다.

## 현재 상태

기준일: `2026-04-17`

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
- current phase: SCN-004 QA 정합성 검증 / demo rehearsal

핵심 상태:

- retrieval MVP 완료
- grounded answer generation MVP 완료
- `cited_articles` 강제 및 retrieval 밖 citation 금지 완료
- answer grounding 검증, hard timeout, eval 안정화 완료
- scenario expansion 검증 완료
- RAG refinement landing 완료 (`expected_point_strict_coverage = 137/153`, `16` partial)
- `POST /api/v1/documents/draft` SCN-004 deterministic draft MVP 완료
- frontend `/after -> /after/result -> /after/intake -> /after/draft` API-connected flow 구현 완료
- frontend Phase 3 A/B(copy/print)까지 반영. Phase 3C 이후 확장성 작업은 데모 리스크 때문에 보류

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
- `SCN-002`: partial
  - 최저임금/수습 꼼수 설명형은 가능
  - 현재는 설명형 Before 데모 범위로 고정
- `SCN-003`: covered
  - 장애인 관련 조문 9개 최소 추가 + 재임베딩 완료
- `SCN-004`: covered
  - 카톡 해고/임금·퇴직금 체불 After frontend demo 구현 완료
- `SCN-005`: covered
  - 육아휴직/가족돌봄휴가 부당 거절 answer smoke 가능
  - After frontend / 문서 타입 확장은 SCN-004 QA/freeze 확인 후 진행 가능

## 현재 데모 자산

### SCN-004 After frontend

- [docs/planning/14_frontend_implementation_handoff.md](docs/planning/14_frontend_implementation_handoff.md)
- [frontend/](frontend/)

주요 흐름:

1. `/after`에서 상황 진술 입력 또는 SCN-004 preset 사용
2. `/after/result`에서 grounded answer와 인용 조문 확인
3. 문서 타입 선택 후 `/after/intake`에서 선택적 사건 정보 입력
4. `/after/draft`에서 진정서 또는 이유서 초안 확인, 복사, 인쇄

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

### 1. QA 정합성 검증

- backend response schema와 frontend type/interface 정합성 확인
- `/api/v1/answer -> /api/v1/documents/draft` legal basis 전달 경로 확인
- SCN-004 preset과 document draft fixture의 cited_articles / grounded_context_ids 보존 확인
- 직접 URL 접근, API 실패, 빈 필드, citation 없음 상태 확인
- desktop/mobile 기본 레이아웃 smoke 확인

### 2. 데모 운영 고정

- 발표용 main path는 SCN-004 After document draft demo로 고정
- `top_k=10`, `ef_search=100`은 SCN demo preset 경로에 명시
- 일반 자유 입력은 `top_k=5`, `ef_search=100` 유지
- `/before`, `/bridge`, Recovery는 이번 frontend demo 범위에서 확장하지 않음

### 3. 선택적 후속

- 남은 `16` partial에 대한 answer-side surface / completeness 보강
- `SCN-001 Full`은 `top_k=10`, `ef_search=100` demo path로만 운영
- `SCN-002`는 설명형 Before 데모 범위 유지
- `SCN-005` After frontend / 문서 타입 확장은 SCN-004 QA/freeze 확인 후 진행 가능
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

2026-04-17 기준 SCN-004 QA/rehearsal에서 확인한 범위:

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
  - SCN-004 preset `/api/v1/answer`: `top_k=10`, `ef_search=100`, `cited_articles=5`, `grounded_context_ids=[1, 2, 3, 5, 10]`, `retrieved_chunks=10`
  - `labor_office_wage_complaint` draft: HTTP 200, `rendered_text` 974자, `missing_fields=12`, `cautions=6`, `evidence_checklist=5`, `cited_articles=2`
  - `labor_commission_unfair_dismissal_brief` draft: HTTP 200, `rendered_text` 1061자, `missing_fields=12`, `cautions=5`, `evidence_checklist=5`, `cited_articles=3`
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

- Playwright / Cypress / Puppeteer 및 Chrome / Chromium 기반 자동 DOM click smoke는 미수행
- direct URL guard는 manual browser runtime에서 확인했으며, HTTP GET만으로는 redirect를 검증할 수 없음
- 필요 시 Playwright/Chromium 설치 후 자동화 click smoke를 별도 실행 가능

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
- `SCN-004` QA 정합성 검증과 manual browser rehearsal은 통과 상태입니다.
- 이후 기능 확장 후보는 `SCN-005` After frontend / 문서 타입입니다.
- `SCN-001` frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 진행합니다.
