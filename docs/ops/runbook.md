# Runbook

기준일: `2026-04-17`

## 목적

SCN-004 After document draft demo와 freeze 상태 재확인을 실행하기 위한 최소 운영 절차다.

현재 기준:

- RAG refinement landing 완료
- SCN-004 document draft backend 완료
- SCN-004 After frontend 4-route flow 완료
- SCN-004 QA 정합성 검증, content output 확인, manual browser rehearsal 통과
- QA 중심은 신규 기능 확장이 아니라 demo freeze 유지와 제출 전 재현성 확인
- current live corpus: `1722` chunks, `selected_as_of = 2026-04-11`

## Environment

Python:

```bash
conda activate law_main_road
```

Node:

```bash
cd frontend
npm install
```

셸에서 `conda`, `node`, `npm`이 바로 잡히지 않으면 로컬 shell profile 또는 `nvm` 설정을 먼저 확인한다.

## Backend

```bash
conda activate law_main_road
uvicorn backend.main:app --reload
```

기본 주소:

- `http://localhost:8000`
- health: `GET /health`

## Frontend

```bash
cd frontend
npm run dev
```

기본 주소:

- `http://localhost:3000`

필요 시 환경변수:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Browser QA

2026-04-20 이후 WSL browser QA는 Windows Chrome CDP / PowerShell 우회보다 WSL Playwright Chromium을 우선 사용한다. `frontend`에는 `@playwright/test` devDependency가 설치되어 있다.

최초 세팅 또는 환경 재설치 시 사용자가 직접 실행한다. `install-deps`는 `sudo` 권한이 필요할 수 있다.

```bash
cd frontend
npm install
npx playwright install-deps
npx playwright install chromium
```

WSL Chromium smoke:

```bash
cd frontend
node -e "const { chromium } = require('@playwright/test'); (async () => { const browser = await chromium.launch({ headless: true }); const page = await browser.newPage(); await page.goto('data:text/html,<h1>ok</h1>'); console.log(await page.textContent('h1')); await browser.close(); })().catch((error) => { console.error(error); process.exit(1); });"
```

Expected output:

```text
ok
```

AI agent는 WSL Playwright가 실패했을 때 Windows Chrome CDP / PowerShell 우회로 시간을 쓰기 전에 실패 원인과 필요한 사용자 조치를 보고한다.

## Verification

QA는 아래 순서로 실행한다.

### 1. Backend import check

```bash
conda activate law_main_road
python -c "from backend.main import app; print('import_ok')"
```

### 2. Backend document draft smoke

```bash
conda activate law_main_road
python backend/verify/check_document_draft.py
```

확인 대상:

- manual wage complaint fixture
- manual unfair dismissal brief fixture
- answer-derived wage complaint legal basis fixture
- answer-derived unfair dismissal legal basis fixture

### 3. Frontend build

```bash
cd frontend
npm run build
```

확인 대상:

- `/`
- `/after`
- `/after/result`
- `/after/intake`
- `/after/draft`

### 4. Optional RAG answer smoke

RAG / answer / retrieval behavior를 수정했거나, demo citation survival을 다시 확인해야 할 때만 실행한다.

```bash
conda activate law_main_road
python backend/verify/check_answer_generation.py "해고를 당했는데 서면통지는 없고 30일 전에 예고도 못 받았습니다. 부당해고 구제신청은 어디에 언제까지 할 수 있나요?" --top-k 10 --ef-search 100
```

원칙:

- 일반 `/api/v1/answer` 기본값은 `top_k=5`, `ef_search=100`
- SCN demo / scenario smoke는 `top_k=10`, `ef_search=100` 명시
- RAG / answer / retrieval behavior 변경 없는 doc-only 작업에서는 broad full eval을 기본 실행하지 않는다.
- full 60 retrieval / answer eval은 `backend/app/services/retrieval.py`, `backend/app/services/answer_generation.py`, embedding behavior, DB contents, API response contract가 바뀐 경우에 우선 검토한다.

## Latest QA Result

2026-04-17 SCN-004 QA/rehearsal 확인 범위:

- backend import smoke: pass, `import_ok`
- document draft verifier: pass
  - `manual_wage_complaint`
  - `manual_unfair_dismissal_brief`
  - `answer_derived_wage_complaint`
  - `answer_derived_unfair_dismissal_brief`
- frontend build: pass
  - nvm Node path 로드 후 `npm run build` 성공
  - build route: `/`, `/after`, `/after/result`, `/after/intake`, `/after/draft`
- live route smoke: pass
  - backend `http://127.0.0.1:8000`
  - frontend `http://127.0.0.1:3000`
  - `/health`, `/`, `/after`, `/after/result`, `/after/intake`, `/after/draft` HTTP 200
- live API smoke: pass
  - SCN-004 preset `/api/v1/answer`: `top_k=10`, `ef_search=100`, `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`, `retrieved_chunks=10`
  - answer `key_points`: 정당한 이유, 30일 전 예고/통상임금, 서면통지, 노동위원회, 3개월 이내, 14일 금품청산 표시
  - wage complaint draft: HTTP 200, `rendered_text` 974자, `missing_fields=12`, `cautions=6`, `evidence_checklist=5`, `cited_articles=2`
  - unfair dismissal brief draft: HTTP 200, `rendered_text` 1123자, `missing_fields=12`, `cautions=5`, `evidence_checklist=5`, `cited_articles=4`
  - 두 draft 모두 `missing_legal_basis=[]`
- code path check: pass
  - backend/frontend answer and draft schema alignment
  - cited_articles / grounded_context_ids guard
  - `buildLegalBasis()` / `buildCaseIntake()` draft payload boundary
  - copy / print handlers
  - no `localStorage` / `sessionStorage` usage
- manual browser rehearsal: pass
  - `/after -> /after/result -> /after/intake -> /after/draft` runtime flow
  - SCN-004 preset, result display, document type selection, empty/partial intake submit
  - draft display, copy, print, direct URL guard

제한 사항:

- Playwright / Cypress / Puppeteer 및 Chrome / Chromium 기반 자동 DOM click smoke는 미수행
- direct URL guard는 manual browser runtime에서 확인했으며, HTTP GET 200만으로는 검증하지 않음
- WSL Playwright Chromium smoke는 별도 browser QA 준비 상태 확인으로 사용한다.

## Manual QA Path

1. backend 실행
2. frontend 실행
3. `/after` 접속
4. SCN-004 preset 입력
5. 법 조문 찾기
6. `/after/result`에서 cited_articles 확인
7. 문서 타입 선택
8. `/after/intake`에서 빈 값 또는 일부 값만 입력
9. `/after/draft`에서 rendered_text, missing_fields, evidence_checklist 확인
10. copy / print 확인
11. direct URL guard 확인:
    - `/after/result`에 state 없음 -> `/after`
    - `/after/intake`에 answer 없음 -> `/after`
    - `/after/intake`에 document_type 없음 -> `/after/result`
    - `/after/draft`에 draft 없음 -> `/after`

## Scope Freeze

QA 중 아래 작업은 하지 않는다.

- `/before`, `/bridge`, Recovery 구현
- 현재 SCN-004 demo freeze 유지 작업 중 SCN-005 문서 타입 추가 작업 혼합
- 팀원 Before / Bridge contract 확인 없는 SCN-001 문서 타입 추가
- sessionStorage backup/restore
- backend API contract 변경
- data/legalize-kr 직접 수정
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response` Web Storage 저장
