# Demo Scenario

기준일: `2026-04-20`

## Main Demo

현재 제출 전 main demo path는 `SCN-004-DEMO-FREEZE` After document draft로 둔다.
`SCN-001-BRIDGE-DEMO`는 Before/Bridge handoff 설명용 answer-only preset이며, 신규 문서 타입 확장이 아니라 발표 연결점을 보강하는 범위다.
SCN-005는 현재 frontend preset UI에서 제외하고 후속 확장 후보로만 유지한다.

시나리오:

- 사용자가 카카오톡으로 즉시 해고 통보를 받음
- 서면 해고통지 없음
- 30일 전 해고예고 없음
- 퇴사 후 마지막 임금과 퇴직금이 14일 넘게 미지급

Preset 문구:

```text
해고를 당했는데 서면통지는 없고 30일 전에 예고도 못 받았습니다. 퇴사 후 마지막 임금과 퇴직금도 14일 넘게 지급받지 못했습니다.
```

Before/Bridge handoff 설명용 preset:

- id: `SCN-001-BRIDGE-DEMO`
- 역할: 계약서 분석에서 표준근로계약서 미사용, 기숙사 정보 누락, 숙소비 공제 위험이 표시된 뒤 After 질문으로 이어지는 연결점
- 정책: fixed/live 여부와 관계없이 answer-only, SCN-001 문서 타입 구현 없음
- query:

```text
계약서 분석에서 표준근로계약서 미사용, 기숙사 정보 누락, 숙소비 공제 위험이 있다고 나왔습니다. 실제로 일해보니 기숙사 환경이 열악하고 월급에서 숙소비가 많이 공제됐으며 외국인이라는 이유로 폭언과 차별도 받았습니다. 이런 경우 회사 잘못을 이유로 사업장 변경을 신청할 수 있나요?
```

## After Preset Operation

`/after`는 presentation-local preset 버튼 2개와 직접 자유 입력을 구분한다.

- preset exact path: 선택된 preset이 있고 textarea 값이 preset `query`와 정확히 같으면 fixed `AnswerResponse` fixture를 사용한다. 이 경우 `/api/v1/answer`를 호출하지 않는다.
- preset modified path: preset 버튼을 누른 뒤 문장을 수정하면 live `/api/v1/answer`를 호출한다. 현재 frontend preset은 모두 `recommendedTopK=10`, `ef_search=100`이다.
- free input path: preset 없이 직접 입력하면 live `/api/v1/answer`를 호출하고 `top_k=5`, `ef_search=100`을 사용한다.
- `SCN-001-BRIDGE-DEMO`는 eval `SCN-001-Q3`이 아니라 Before/Bridge 발표 연결용 query를 쓰는 presentation-local preset이다. fixed/live 여부와 관계없이 answer-only다.
- `SCN-004-DEMO-FREEZE`는 eval `SCN-004-Q1`이 아니라 document draft freeze용 query를 쓰는 presentation-local preset이다. fixed/live 여부와 관계없이 `getScn004DraftEligibility(answer)` 기준으로 기존 document draft 2종을 필터링한다.
- `SCN-004-DEMO-FREEZE` exact preset은 기존 freeze 기준을 유지한다: `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`, `retrieval_total=10`, `model_name=gemini-2.5-flash`.
- SCN-005는 현재 preset 버튼과 frontend fixed answer fixture에서 제외한다. 후속 확장 후보로만 설명한다.

## Pre-Demo Quick Check / Freeze QA

시연 전 묶음 실행은 runbook의 `scripts/demo_preflight.sh`를 우선 사용한다. 아래 smoke 목록은 수동 확인 또는 script 내용 참고용이다.

### 1. PostgreSQL readiness

```bash
pg_isready -h 127.0.0.1 -p 5432
```

### 2. Backend import

```bash
conda activate law_main_road
python -c "from backend.main import app; print('import_ok')"
```

### 3. Document draft smoke

```bash
conda activate law_main_road
python backend/verify/check_document_draft.py
```

확인 대상:

- manual wage complaint fixture
- manual unfair dismissal brief fixture
- answer-derived wage complaint legal basis fixture
- answer-derived unfair dismissal legal basis fixture

### 4. Frontend build

```bash
cd frontend
npm run build
```

확인 route:

- `/`
- `/after`
- `/after/result`
- `/after/intake`
- `/after/draft`

### 5. WSL Chromium smoke

runbook의 WSL Chromium smoke 명령을 사용한다.

```bash
cd frontend
node -e "const { chromium } = require('@playwright/test'); (async () => { const browser = await chromium.launch({ headless: true }); const page = await browser.newPage(); await page.goto('data:text/html,<h1>ok</h1>'); console.log(await page.textContent('h1')); await browser.close(); })().catch((error) => { console.error(error); process.exit(1); });"
```

Expected output:

```text
ok
```

### 6. Optional RAG answer smoke

RAG / answer / retrieval behavior를 수정했거나 citation survival을 다시 확인해야 할 때만 실행한다.

```bash
conda activate law_main_road
python backend/verify/check_answer_generation.py "해고를 당했는데 서면통지는 없고 30일 전에 예고도 못 받았습니다. 부당해고 구제신청은 어디에 언제까지 할 수 있나요?" --top-k 10 --ef-search 100
```

주의:

- 일반 `/api/v1/answer` 기본값은 `top_k=5`, `ef_search=100`
- SCN demo preset은 `top_k=10`, `ef_search=100`
- RAG / answer / retrieval behavior 변경 없는 doc-only 작업에서는 broad full eval을 기본 실행하지 않는다.

## QA Rehearsal Status

2026-04-20 이후 browser rehearsal 기준:

- 기준 URL은 `http://localhost:3000`이며 WSL Playwright Chromium을 우선 사용한다.
- 기존 `http://127.0.0.1:3000`은 Next dev HMR cross-origin warning 이력이 있어 QA 기준 URL로 쓰지 않는다.
- Windows Chrome CDP는 WSL Playwright Chromium 실패 시 fallback으로만 사용한다.

2026-04-20 presentation-local After preset fixture architecture 확인 결과:

- `/after` preset 버튼은 `SCN-001-BRIDGE-DEMO`, `SCN-004-DEMO-FREEZE` 2개만 표시한다.
- `SCN-004-DEMO-FREEZE` unchanged는 fixed answer fixture를 사용하며 `/api/v1/answer`를 호출하지 않는다.
- `SCN-004-DEMO-FREEZE` fixed answer는 `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`를 유지한다.
- `SCN-004-DEMO-FREEZE` modified는 live `/api/v1/answer`를 `top_k=10`, `ef_search=100`으로 호출하고, SCN-004 eligibility에 따라 두 문서 타입을 표시한다.
- `SCN-001-BRIDGE-DEMO` unchanged는 fixed answer fixture를 사용하고, modified는 live `/api/v1/answer`를 `top_k=10`, `ef_search=100`으로 호출한다.
- `SCN-001-BRIDGE-DEMO`는 fixed/live 여부와 관계없이 answer-only이며 SCN-004 문서 초안 선택지를 표시하지 않는다.
- SCN-005는 현재 frontend preset UI에서 제외하고 후속 확장 후보로만 유지한다.
- 직접 자유 입력은 live `/api/v1/answer`를 `top_k=5`, `ef_search=100`으로 호출한다.
- SCN-004 draft flow에서 wage / unfair 문서 생성, copy, print, direct URL guard, Web Storage 미사용을 확인했다.

2026-04-20 final dry-run pass:

- code / docs 수정, `git add`, commit 없이 검증 완료
- Quick Check 통과: PostgreSQL `accepting connections`, backend import `import_ok`, `python backend/verify/check_document_draft.py`, `cd frontend && npm run build`, WSL Playwright Chromium smoke `ok`
- Browser dry-run: `http://localhost:3000/after`에서 WSL Playwright Chromium 실제 클릭 검증, `SCN-004-DEMO-FREEZE` fixed path는 `/api/v1/answer` 호출 0회
- `/after/result`: `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`, 문서 타입 2개 표시
- draft output: 임금체불 진정서 `source_context_ids=[5, 10]`, `cited_articles=2`, `missing_legal_basis=[]`, `rendered_text` 989자; 부당해고 이유서 `source_context_ids=[1, 2, 3, 4]`, `cited_articles=4`, `missing_legal_basis=[]`, `rendered_text` 1138자
- 두 draft 모두 copy 성공과 `window.print()` 호출 확인
- `다른 문서 타입으로 생성하기`는 `/after/result` 복귀와 answer state 유지를 확인했고, `SCN-001-BRIDGE-DEMO`는 fixed answer-only / `/api/v1/answer` 호출 없음 / 문서 선택 UI 없음 확인
- direct URL guard: `/after/result`, `/after/intake`, `/after/draft` state 없음 -> `/after`; Web Storage는 `localStorage.length=0`, `sessionStorage.length=0`
- cleanup 후 backend `localhost:8000`, frontend `localhost:3000` connection refused 확인
- Freeze 판단: SCN-004 demo freeze 유지, 문서의 main demo 클릭 순서와 실제 화면 흐름 일치

2026-04-20 SCN-004 free-input document eligibility guard 확인 결과:

- SCN-004 범위 밖 자유 입력은 answer / key_points / cautions / cited_articles는 표시하되 문서 초안 선택지는 제공하지 않는다.
- result 화면은 “현재 문서 초안 지원 범위 밖” 안내를 표시하고 `/after/intake` 진행을 막는다.
- SCN-004 preset path는 기존 문서 타입 2종 선택 흐름을 유지하고, SCN-004 관련 자유 입력은 answer 근거에 맞는 문서 타입만 표시한다.
- 이 변경은 SCN-005 문서 타입 구현이 아니라 SCN-004 free-input document eligibility guard다.

2026-04-20 SCN-004 draft action navigation stabilization 확인 결과:

- frontend build, `git diff --check`, Web Storage string scan 통과
- `http://localhost:3000` 기준 browser runtime happy path 통과
- `다른 문서 타입으로 생성하기` -> `/after/result` 유지 및 answer / cited articles 기반 문서 타입 재선택 가능 확인
- `사건 정보 수정하기` -> `/after/intake` 유지 및 selected document type / intake form state 유지 확인
- direct URL guard와 `localStorage` / `sessionStorage` 미사용 유지 확인

2026-04-17 확인 결과:

- backend import smoke 통과
- document draft verifier 통과
- frontend build 통과
- backend/frontend dev server route smoke 통과
- SCN-004 preset `/api/v1/answer` live smoke 통과
  - `cited_articles=6`
  - `grounded_context_ids=[1, 2, 3, 5, 10, 4]`
  - `key_points`에 노동위원회와 3개월 이내 구제신청 내용 표시
- `/api/v1/answer -> /api/v1/documents/draft` legal basis 전달 smoke 통과
  - 임금체불 진정서: `cited_articles=2`, `missing_legal_basis=[]`
  - 부당해고 이유서: `cited_articles=4`, `missing_legal_basis=[]`
- schema / guard / copy / print code path 확인
- manual browser rehearsal 통과
  - `/after -> /after/result -> /after/intake -> /after/draft` runtime flow 확인
  - SCN-004 preset, result 표시, 문서 타입 선택, 빈 값 또는 일부 값 intake submit 확인
  - draft 표시, copy, print, direct URL guard 확인

2026-04-17 자동 DOM click smoke는 미수행했다. 당시 manual browser rehearsal로 `/after -> /after/result -> /after/intake -> /after/draft` 흐름과 direct URL guard를 확인했다. direct URL guard는 client-side `router.replace` 방식이라 HTTP GET만으로 redirect를 검증하지 않는다.

## Demo Startup

Backend:

```bash
conda activate law_main_road
uvicorn backend.main:app --reload
```

Frontend:

```bash
cd frontend
npm run dev
```

기본 주소:

- backend: `http://localhost:8000`
- frontend: `http://localhost:3000`
- browser QA 기준 URL은 `http://localhost:3000`이다. `http://127.0.0.1:3000`은 QA 기준 URL로 쓰지 않는다.

## Main Demo Script: SCN-004-DEMO-FREEZE

1. `/after` 접속
   - 말할 포인트: “After flow는 사용자의 상황 진술을 법령 근거와 연결하고, 근거가 충분할 때만 문서 초안으로 이어집니다.”
2. `SCN-004-DEMO-FREEZE` preset 클릭
   - 말할 포인트: “이 경로는 발표용 fixed answer fixture를 사용해 live LLM ordering 흔들림을 제거합니다.”
3. `법 조문 찾기` 클릭
   - unchanged preset exact path는 fixed answer fixture를 사용하므로 `/api/v1/answer`를 호출하지 않음
   - preset 문장을 수정하면 live `/api/v1/answer`를 `top_k=10`, `ef_search=100`으로 호출
4. `/after/result`에서 answer, key_points, cautions, cited_articles 확인
   - `cited_articles` 또는 `grounded_context_ids`가 없으면 문서 초안 flow로 진행하지 않음
   - SCN-004 범위 밖 자유 입력은 answer만 확인하고 문서 초안 flow로 진행하지 않음
   - SCN-004 관련 자유 입력은 answer 근거에 맞는 문서 타입만 표시
   - 문서 타입 2개가 표시되는지 확인: 고용노동청 임금체불 진정서 초안, 노동위원회 부당해고 구제신청 이유서 초안
5. 강조할 조문:
   - `근로기준법 제23조`
   - `근로기준법 제26조`
   - `근로기준법 제27조`
   - `근로기준법 제28조`
   - `근로기준법 제36조`
   - `근로자퇴직급여 보장법 제9조`
6. 임금체불 진정서 flow
   - `고용노동청 임금체불 진정서 초안` 선택
   - `/after/intake`에서 일부 필드만 입력하거나 빈 값으로 제출
   - 말할 포인트: “빈 필드는 제출을 막지 않고, 초안의 missing_fields에서 확인 필요 항목으로 남깁니다.”
   - `/after/draft`에서 rendered_text, missing_fields, cautions, evidence_checklist, cited_articles 확인
   - copy / print 확인
7. 부당해고 이유서 flow
   - `다른 문서 타입으로 생성하기` 클릭 후 `/after/result`로 돌아가는지 확인
   - `노동위원회 부당해고 구제신청 이유서 초안` 선택
   - `/after/intake`에서 초안 생성
   - `/after/draft`에서 `source_context_ids=[1, 2, 3, 4]`, `missing_legal_basis=[]` 확인
   - 말할 포인트: “문서 초안은 answer의 legal basis 안에 있는 근거만 사용합니다.”
8. direct URL guard는 시간이 있으면 보여주고, 시간이 없으면 말로만 설명한다.
   - `/after/result`에 state 없음 -> `/after`
   - `/after/intake`에 answer 없음 -> `/after`
   - `/after/intake`에 document_type 없음 -> `/after/result`
   - `/after/draft`에 draft 없음 -> `/after`

## Bridge Handoff Demo: SCN-001-BRIDGE-DEMO

목적:

- Before/Bridge가 넘겨줄 위험 신호가 After 질문으로 이어지는 흐름을 설명한다.
- 현재는 Bridge 연결점으로 preset id와 질문을 고정해둔 상태다.

클릭 순서:

1. `/after` 접속
2. `SCN-001-BRIDGE-DEMO` preset 클릭
3. `법 조문 찾기` 클릭
4. `/after/result`에서 answer, key_points, cautions, cited_articles 확인
5. 문서 초안 선택지가 표시되지 않는 것이 정상임을 확인

발표 멘트:

- “이 경로는 현재 answer-only입니다.”
- “사업장 변경 사유서/상담용 요약서는 Before/Bridge output contract 확정 후 별도 확장합니다.”
- “현재는 Bridge 연결점으로 preset id와 질문을 고정해둔 상태입니다.”

## Modified Preset / Free Input

- preset 문장을 수정하면 fixed answer fixture가 아니라 live `/api/v1/answer`를 호출한다.
- preset modified는 `top_k=10`, `ef_search=100`이다.
- 완전 자유 입력은 `top_k=5`, `ef_search=100`이다.
- free input이 SCN-004 범위면 근거에 맞는 문서 타입만 표시한다.
- free input이 SCN-004 범위 밖이면 answer-only로 처리한다.

## Expected Legal Basis

부당해고 이유서:

- `근로기준법 제23조 (해고 등의 제한)`
- `근로기준법 제26조 (해고의 예고)`
- `근로기준법 제27조 (해고사유 등의 서면통지)`
- `근로기준법 제28조 (부당해고등의 구제신청)`

임금체불 진정서:

- `근로기준법 제36조 (금품 청산)`
- `근로자퇴직급여 보장법 제9조 (퇴직금의 지급 등)`
- 필요 시 `근로기준법 제37조 (미지급 임금에 대한 지연이자)`

현재 SCN-004 preset answer와 answer-derived draft output은 위 기대 근거를 충족한다. 부당해고 이유서 draft는 `근로기준법 제23조`, `제26조`, `제27조`, `제28조`를 포함하고, 임금체불 진정서 draft는 `근로기준법 제36조`, `근로자퇴직급여 보장법 제9조`를 포함한다.

## Fallback Script

발표 직전 주의사항:

- `npm run dev` 전에 `localhost:3000`에 stale Next server가 떠 있지 않은지 먼저 확인한다.
- headless Playwright에서는 `window.print()` 호출만 검증했으므로, 발표 브라우저에서 실제 OS print dialog 표시를 한 번 육안 확인한다.
- fixed answer path는 live LLM 흔들림을 제거하지만 문서 초안 생성은 backend `/api/v1/documents/draft`에 의존하므로 PostgreSQL / backend readiness를 계속 확인한다.

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

## Out Of Demo Scope

- `/before`
- `/bridge`
- Recovery
- SCN-005 문서 타입은 현재 SCN-004 live demo path 밖이며 freeze 기준을 유지한 별도 확장 후보
- SCN-005 preset UI는 현재 제외
- SCN-001 문서 타입은 구현하지 않음. 팀원 Before / Bridge contract 확인 후 별도 확장 후보로만 검토
- sessionStorage backup/restore
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response` Web Storage 저장
- 실제 제출 / PDF 다운로드
