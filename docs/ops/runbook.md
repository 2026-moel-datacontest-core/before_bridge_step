# Runbook

기준일: `2026-04-20`

## 목적

SCN-001/004 presentation-local After preset과 SCN-004 document draft freeze 상태를 재확인하기 위한 최소 운영 절차다.

현재 기준:

- RAG refinement landing 완료
- SCN-004 document draft backend 완료
- SCN-004 After frontend 4-route flow 완료
- SCN-004 QA 정합성 검증, content output 확인, manual browser rehearsal 통과
- SCN-001/004 presentation-local answer preset fixture architecture 추가
- SCN-005는 현재 frontend preset UI에서 제외하고 후속 확장 후보로 유지
- QA 중심은 신규 문서 타입 확장이 아니라 demo freeze 유지와 제출 전 재현성 확인
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
- browser demo / QA 기준 URL은 `http://localhost:3000`이다. `http://127.0.0.1:3000`은 Next dev HMR cross-origin warning 이력이 있어 QA 기준 URL로 쓰지 않는다.

필요 시 환경변수:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## After Preset Policy

`/after`는 발표 운영용 presentation-local preset 버튼 2개와 자유 입력을 지원한다.

현재 frontend preset:

- `SCN-001-BRIDGE-DEMO`: eval `SCN-001-Q3`이 아니라 Before/Bridge 발표 연결용 presentation-local query다. fixed/live 여부와 관계없이 answer-only이며 SCN-001 문서 타입을 열지 않는다.
- `SCN-004-DEMO-FREEZE`: eval `SCN-004-Q1`이 아니라 document draft freeze용 presentation-local query다. fixed/live 여부와 관계없이 SCN-004 draft eligibility를 적용한다.
- `SCN-005`: 현재 UI preset에서 제외한다. 문서상 후속 확장 후보로만 유지하며 SCN-005 문서 타입은 구현하지 않는다.

- preset exact path: 현재 textarea 값이 active preset의 `query`와 정확히 같으면 frontend fixed `AnswerResponse` fixture를 사용하고 `/api/v1/answer`를 호출하지 않는다.
- preset modified path: preset 버튼을 누른 뒤 문장을 수정하면 live `/api/v1/answer`를 호출하고 해당 preset의 `recommendedTopK`를 사용한다. 현재 frontend preset은 모두 `top_k=10`, `ef_search=100`이다.
- free input path: preset 없이 직접 입력하면 live `/api/v1/answer`를 호출하고 `top_k=5`, `ef_search=100`을 사용한다.
- `SCN-001-BRIDGE-DEMO` preset은 fixed/live 여부와 관계없이 answer-only다. SCN-004 문서 초안 선택지를 표시하지 않는다.
- `SCN-004-DEMO-FREEZE` preset은 fixed/live 여부와 관계없이 기존 `getScn004DraftEligibility(answer)` 기준으로 문서 타입을 필터링한다.
- `SCN-004-DEMO-FREEZE` exact preset fixed answer는 기존 document draft freeze 기준을 유지한다: `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`, `retrieval_total=10`, `model_name=gemini-2.5-flash`.
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response`는 Web Storage에 저장하지 않는다.

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

## Demo Preflight Script

발표 직전 preflight는 repo root에서 아래 script로 한 번에 실행한다.

```bash
bash scripts/demo_preflight.sh
```

이 script는 아래 순서로 smoke를 실행한다.

- `git status -sb`
- `main == origin/main` 확인
- `pg_isready -h 127.0.0.1 -p 5432`
- `source /home/jongwon/anaconda3/etc/profile.d/conda.sh`
- `conda activate law_main_road`
- `python -c "from backend.main import app; print('import_ok')"`
- `python backend/verify/check_document_draft.py`
- `cd frontend && npm run build`
- build 후 `git status -sb` 재확인
- WSL Playwright Chromium smoke

운영 원칙:

- backend / frontend dev server를 자동 실행하지 않는다.
- PostgreSQL을 start/stop하지 않는다.
- 포트 kill 또는 process kill을 하지 않는다.
- `git add`, `git commit`, `git restore`를 실행하지 않는다.
- local-only dirty file은 preflight 실패 사유가 아니다. 단, 제출/발표 commit 전 expected local-only file이 staged 상태인지 확인한다.
- `npm run build`가 `frontend/next-env.d.ts`를 갱신할 수 있으므로 build 후 status를 반드시 확인한다.

script가 통과하면 마지막에 demo server 수동 실행 명령을 출력한다.

## Verification

QA는 아래 순서로 실행한다.

### 1. PostgreSQL readiness

```bash
pg_isready -h 127.0.0.1 -p 5432
```

### 2. Backend import check

```bash
conda activate law_main_road
python -c "from backend.main import app; print('import_ok')"
```

### 3. Backend document draft smoke

```bash
conda activate law_main_road
python backend/verify/check_document_draft.py
```

확인 대상:

- manual wage complaint fixture
- manual unfair dismissal brief fixture
- answer-derived wage complaint legal basis fixture
- answer-derived unfair dismissal legal basis fixture

참고: `check_document_draft.py`는 backend verify fixture 기준 smoke이므로 answer-derived fixture 숫자(wage cited_articles=3, unfair cited_articles=5)는 발표용 `SCN-004-DEMO-FREEZE` browser dry-run fixed preset path 값(wage=2, unfair=4)과 다를 수 있다. 이 차이는 정상이며 발표 demo freeze 기준은 browser dry-run fixed preset path 값으로 확인한다.

### 4. Frontend build

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

### 5. WSL Chromium smoke

Browser QA 준비 상태는 Browser QA 섹션의 `node -e` smoke로 확인한다. expected output은 `ok`다.

### 6. Optional RAG answer smoke

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

### 7. Optional answer evidence report

집계 수치가 아니라 문항별로 왜 OK / PARTIAL / FAIL인지 확인해야 할 때만 실행한다. live LLM/API 비용과 wording 변동성이 있으므로 `scripts/demo_preflight.sh`에는 포함하지 않는다.

MVP eval sample:

```bash
conda activate law_main_road
python eval/run_answer_evidence_report.py --ids KLS-EVAL-001 KLS-EVAL-004 --top-k 5 --ef-search 100
```

Scenario smoke sample:

```bash
conda activate law_main_road
python eval/run_answer_evidence_report.py \
  --dataset eval/scenario_demo_question_sets_v1.json \
  --scenario-format \
  --ids SCN-001-Q3 SCN-004-Q1 \
  --ef-search 100
```

Full 60 evidence report는 RAG / answer 회귀가 의심될 때 선택 실행하며 발표 전 기본 preflight와 분리한다. 2026-04-20 기준 산출물은 `eval/reports/answer_evidence_2026-04-20.summary.md`와 `eval/reports/answer_evidence_2026-04-20.jsonl`이고, `scripts/demo_preflight.sh`에는 포함하지 않는다.

확인 대상:

- expected/gold citation이 retrieval top labels와 answer `cited_articles`에 hit됐는지
- `expected_points` 중 covered / missing point가 무엇인지
- answer의 explicit citation이 retrieved + grounded context 밖으로 벗어나지 않았는지
- raw / grounded context ids가 retrieved context ids 안에서 유효한지

판단 기준:

- `PASS`: citation hit, expected point coverage, grounded citation cleanliness가 모두 clean
- `PARTIAL`: citation / grounding은 clean하지만 expected point 일부가 missing
- `FAIL`: timeout/provider/schema 오류, citation miss, context id invalid, grounded citation violation 등 근거 신뢰성 문제가 있음

`scenario_demo_question_sets_v1.json`은 scenario smoke dataset이며 frontend presentation preset source of truth가 아니다. 발표용 preset은 `frontend/src/lib/scenarioPresets.ts`, fixed answer fixture는 `frontend/src/lib/scenarioPresetAnswers.json`을 기준으로 본다.

## Latest QA Result

2026-04-20 final demo preflight pass:

- `bash scripts/demo_preflight.sh` 통과, exit code `0`
- 확인 항목: `main == origin/main`, PostgreSQL readiness, conda env activation, backend import, document draft smoke, frontend build, WSL Playwright Chromium smoke
- 운영 리스크: script는 DB를 start하지 않고 PostgreSQL readiness만 확인하며, backend / frontend dev server를 자동 실행하지 않는다.
- 발표 직전 별도 터미널에서 backend / frontend를 수동 실행하고 `http://localhost:3000/after`에서 final browser rehearsal을 수행한다.

2026-04-20 final dry-run:

- code / docs 수정, `git add`, commit 없이 검증 완료
- Quick Check 통과: `pg_isready -h 127.0.0.1 -p 5432` accepting connections, backend import `import_ok`, `python backend/verify/check_document_draft.py`, `cd frontend && npm run build`, WSL Playwright Chromium smoke `ok`
- Browser dry-run: `http://localhost:3000/after`에서 WSL Playwright Chromium 실제 클릭 검증, `SCN-004-DEMO-FREEZE` fixed path는 `/api/v1/answer` 호출 0회
- `/after/result`: `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`, 문서 타입 2개 표시
- draft output: 임금체불 진정서 `document_type=labor_office_wage_complaint`, `source_context_ids=[5, 10]`, `cited_articles=2`, `missing_legal_basis=[]`, `rendered_text` 989자; 부당해고 이유서 `document_type=labor_commission_unfair_dismissal_brief`, `source_context_ids=[1, 2, 3, 4]`, `cited_articles=4`, `missing_legal_basis=[]`, `rendered_text` 1138자
- 두 draft 모두 copy 성공과 `window.print()` 호출 확인
- `다른 문서 타입으로 생성하기`는 `/after/result` 복귀와 answer state 유지를 확인했고, `SCN-001-BRIDGE-DEMO`는 fixed answer-only / `/api/v1/answer` 호출 없음 / 문서 선택 UI 없음 확인
- direct URL guard: `/after/result`, `/after/intake`, `/after/draft` state 없음 -> `/after`; Web Storage는 `localStorage.length=0`, `sessionStorage.length=0`
- cleanup 후 backend `localhost:8000`, frontend `localhost:3000` connection refused 확인. 참고: `npm run dev` 실행 시 3000에는 이미 같은 repo의 Next dev server가 떠 있어 그 서버를 QA 대상으로 사용했고 cleanup에서 종료함
- Freeze 판단: SCN-004 demo freeze 유지, 문서의 main demo 클릭 순서와 실제 화면 흐름 일치

발표 직전 주의사항:

- `npm run dev` 전에 `localhost:3000`에 stale Next server가 떠 있지 않은지 먼저 확인한다.
- headless Playwright에서는 `window.print()` 호출만 검증했으므로, 발표 브라우저에서 실제 OS print dialog 표시를 한 번 육안 확인한다.
- fixed answer path는 live LLM 흔들림을 제거하지만 문서 초안 생성은 backend `/api/v1/documents/draft`에 의존하므로 PostgreSQL / backend readiness를 계속 확인한다.

2026-04-20 presentation-local After preset fixture architecture 확인:

- static checks: `npm run build` 통과, WSL Playwright Chromium smoke 통과
- `/after` preset 버튼은 `SCN-001-BRIDGE-DEMO`, `SCN-004-DEMO-FREEZE` 2개만 표시
- `SCN-004-DEMO-FREEZE` preset unchanged:
  - fixed answer fixture 사용, `/api/v1/answer` 호출 없음
  - `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`
  - 고용노동청 임금체불 진정서 / 노동위원회 부당해고 이유서 두 문서 타입 표시
  - wage / unfair draft flow, copy, print 통과
- `SCN-004-DEMO-FREEZE` preset modified:
  - live `/api/v1/answer` 호출 확인
  - payload: `top_k=10`, `ef_search=100`
  - SCN-004 eligibility에 따라 두 문서 타입 표시 확인
- `SCN-001-BRIDGE-DEMO` preset unchanged:
  - fixed answer fixture 사용, `/api/v1/answer` 호출 없음
  - fixed answer query는 Before/Bridge 발표 연결용 presentation-local query와 일치
  - answer / key_points / cautions / cited_articles 표시
  - SCN-004 문서 초안 선택지 미표시, answer-only 안내 표시
- `SCN-001-BRIDGE-DEMO` preset modified:
  - live `/api/v1/answer` 호출 확인
  - payload: `top_k=10`, `ef_search=100`
  - answer-only 유지
- SCN-005 preset은 UI와 frontend fixed answer fixture에서 제외
- 직접 자유 입력:
  - live `/api/v1/answer` 호출 확인
  - payload: `top_k=5`, `ef_search=100`
  - SCN-004 근거가 맞으면 문서 타입 표시, 범위 밖이면 answer-only 안내 표시
- direct URL guard 유지:
  - `/after/result`, `/after/intake`, `/after/draft` state 없음 -> `/after`
- Web Storage:
  - `localStorage.length=0`, `sessionStorage.length=0`

2026-04-20 SCN-004 free-input document eligibility guard 확인:

- `/after/result`는 grounded answer / key_points / cautions / cited_articles를 계속 표시한다.
- SCN-004 범위 밖 자유 입력은 “현재 문서 초안 지원 범위 밖” 안내를 표시하고 문서 타입 선택 및 `/after/intake` 진행을 막는다.
- SCN-004 preset은 기존 2개 문서 타입 선택 범위를 유지하고, SCN-004 관련 자유 입력은 answer 근거에 맞는 문서 타입만 표시한다.
- backend API contract, retrieval / answer / document draft behavior, Web Storage 정책은 변경하지 않는다.

2026-04-20 SCN-004 draft action navigation stabilization 확인:

- static checks: frontend build 통과, `git diff --check` 통과, `frontend/src` Web Storage 사용 문자열 없음
- browser runtime: `http://localhost:3000` 기준 happy path 검증 통과, 2026-04-20 이후 browser QA는 WSL Playwright Chromium 우선
- `/after -> /after/result -> /after/intake -> /after/draft` happy path 확인
- `/after/draft`의 `다른 문서 타입으로 생성하기` 클릭 시 `/after/result` 유지, answer / cited articles 기반 문서 타입 재선택 가능 확인
- `/after/draft`의 `사건 정보 수정하기` 클릭 시 `/after/intake` 유지, selected document type과 기존 intake form state 유지 확인
- direct URL guard 유지: `/after/result`, `/after/intake`, `/after/draft` state 없음 -> `/after`
- `localStorage` / `sessionStorage` 미사용 유지 확인

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

### Main demo: SCN-004-DEMO-FREEZE

1. backend 실행
2. frontend 실행
3. browser에서 `http://localhost:3000/after` 접속
4. `SCN-004-DEMO-FREEZE` preset 클릭
5. “이 경로는 발표용 fixed answer fixture를 사용해 live LLM ordering 흔들림을 제거한다”고 설명
6. `법 조문 찾기` 클릭
7. `/after/result`에서 answer, key_points, cautions, cited_articles와 문서 타입 2개 확인
8. 강조 조문 확인:
   - `근로기준법 제23조`
   - `근로기준법 제26조`
   - `근로기준법 제27조`
   - `근로기준법 제28조`
   - `근로기준법 제36조`
   - `근로자퇴직급여 보장법 제9조`
9. `고용노동청 임금체불 진정서 초안` 선택
10. `/after/intake`에서 빈 값 또는 일부 값만 입력
11. `/after/draft`에서 rendered_text, missing_fields, cautions, evidence_checklist, cited_articles 확인
12. copy / print 확인
13. `다른 문서 타입으로 생성하기`를 눌러 `/after/result`로 돌아가는지 확인
14. `노동위원회 부당해고 구제신청 이유서 초안` 선택 후 draft 생성
15. `source_context_ids=[1, 2, 3, 4]`, `missing_legal_basis=[]` 확인
16. direct URL guard 확인:
    - `/after/result`에 state 없음 -> `/after`
    - `/after/intake`에 answer 없음 -> `/after`
    - `/after/intake`에 document_type 없음 -> `/after/result`
    - `/after/draft`에 draft 없음 -> `/after`

### Bridge handoff demo: SCN-001-BRIDGE-DEMO

1. `/after` 접속
2. `SCN-001-BRIDGE-DEMO` preset 클릭
3. `법 조문 찾기` 클릭
4. `/after/result`에서 answer, key_points, cautions, cited_articles 확인
5. 문서 초안 선택지가 표시되지 않는 것이 정상임을 확인

발표 멘트:

- “이 경로는 현재 answer-only입니다.”
- “사업장 변경 사유서/상담용 요약서는 Before/Bridge output contract 확정 후 별도 확장합니다.”
- “현재는 Bridge 연결점으로 preset id와 질문을 고정해둔 상태입니다.”

## Fallback Script

아래는 발표자가 그대로 읽을 fallback 멘트다.

1. PostgreSQL이 꺼짐
   - 멘트: “현재 retrieval DB가 내려가 있어 live answer는 중단됩니다. 제출 전 freeze smoke에서는 DB 1722 chunks / embedding 1722 기준으로 검증했습니다.”
2. Vertex/Gemini API 실패
   - 멘트: “SCN-004 fixed preset은 발표 재현성을 위해 고정 answer fixture를 사용합니다. 자유 입력 live path는 외부 API 상태에 영향을 받을 수 있습니다.”
3. frontend/backend 연결 실패
   - 멘트: “backend /health와 frontend build를 먼저 확인하고, 필요 시 `check_document_draft.py`와 고정 fixture 결과로 backend document draft를 보여줍니다.”
4. Browser/Playwright 문제
   - 멘트: “WSL Playwright Chromium을 우선 사용하고, 실패 시 원인과 필요한 사용자 조치를 확인합니다.”
5. 시간이 부족할 때
   - SCN-004 result + wage draft 하나만 보여준다.
   - SCN-001은 말로만 Bridge handoff 후보라고 설명한다.

## Scope Freeze

QA 중 아래 작업은 하지 않는다.

- `/before`, `/bridge`, Recovery 구현
- 현재 SCN-004 demo freeze 유지 작업 중 SCN-005 문서 타입 추가 작업 혼합
- 팀원 Before / Bridge contract 확인 없는 SCN-001 문서 타입 추가
- 실제 제출 / PDF 다운로드
- sessionStorage backup/restore
- backend API contract 변경
- data/legalize-kr 직접 수정
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response` Web Storage 저장
