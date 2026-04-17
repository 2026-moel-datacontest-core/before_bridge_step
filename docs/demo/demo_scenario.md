# Demo Scenario

기준일: `2026-04-17`

## Main Demo

현재 제출 전 main demo path는 `SCN-004 After document draft`로 둔다.
신규 기능 확장이 아니라 QA 정합성 검증과 demo freeze 상태를 보여주는 시연이다.

시나리오:

- 사용자가 카카오톡으로 즉시 해고 통보를 받음
- 서면 해고통지 없음
- 30일 전 해고예고 없음
- 퇴사 후 마지막 임금과 퇴직금이 14일 넘게 미지급

Preset 문구:

```text
해고를 당했는데 서면통지는 없고 30일 전에 예고도 못 받았습니다. 퇴사 후 마지막 임금과 퇴직금도 14일 넘게 지급받지 못했습니다.
```

## Pre-Demo Freeze QA

시연 전 README/runbook과 같은 순서로 아래 smoke를 통과시킨다.

### 1. Backend import

```bash
conda activate law_main_road
python -c "from backend.main import app; print('import_ok')"
```

### 2. Document draft smoke

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

확인 route:

- `/`
- `/after`
- `/after/result`
- `/after/intake`
- `/after/draft`

### 4. Optional RAG answer smoke

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

2026-04-17 확인 결과:

- backend import smoke 통과
- document draft verifier 통과
- frontend build 통과
- backend/frontend dev server route smoke 통과
- SCN-004 preset `/api/v1/answer` live smoke 통과
- `/api/v1/answer -> /api/v1/documents/draft` legal basis 전달 smoke 통과
- schema / guard / copy / print code path 확인

실제 DOM click smoke는 미수행했다. 현재 환경에 Playwright / Cypress / Puppeteer 및 Chrome / Chromium이 없어 `/after -> /after/result -> /after/intake -> /after/draft`를 브라우저 자동화로 클릭 검증하지 못했다. direct URL guard도 client-side `router.replace` 방식이라 HTTP GET만으로 redirect를 검증하지 않는다.

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

## Live Demo Flow

1. `/after` 접속
2. `SCN-004 프리셋 입력` 클릭
3. `법 조문 찾기` 클릭
   - preset path는 `top_k=10`, `ef_search=100`
4. `/after/result`에서 answer, key_points, cautions, cited_articles 확인
   - `cited_articles` 또는 `grounded_context_ids`가 없으면 문서 초안 flow로 진행하지 않음
5. 문서 타입 선택
   - 임금체불 demo: 고용노동청 임금체불 진정서 초안
   - 부당해고 demo: 노동위원회 부당해고 구제신청 이유서 초안
6. `/after/intake`에서 일부 필드만 입력하거나 빈 값으로 진행
   - 빈 field는 submit을 막지 않고 draft response의 `missing_fields`에서 확인
7. `/after/draft`에서 rendered_text, missing_fields, cautions, evidence_checklist, cited_articles 확인
8. copy / print 동작 확인
9. direct URL guard 확인:
   - `/after/result`에 state 없음 -> `/after`
   - `/after/intake`에 answer 없음 -> `/after`
   - `/after/intake`에 document_type 없음 -> `/after/result`
   - `/after/draft`에 draft 없음 -> `/after`

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

## Backup

- backend만 시연해야 할 경우:
  - `/api/v1/answer`
  - `/api/v1/documents/draft`
  - `python backend/verify/check_document_draft.py`
- frontend가 backend 연결에 실패하면 API error notification과 retry UI를 보여주고 backend 상태를 확인한다.
- frontend build만 통과하고 live backend가 불안정하면 `/after` error / retry state와 `check_document_draft.py` 결과를 fallback으로 보여준다.

## Out Of Demo Scope

- `/before`
- `/bridge`
- Recovery
- SCN-005 문서 타입은 현재 SCN-004 live demo path 밖이며 SCN-004 QA/freeze 확인 후 확장 후보
- SCN-001 문서 타입은 팀원 Before / Bridge contract 확인 후 확장
- sessionStorage backup/restore
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response` Web Storage 저장
- 실제 제출 / PDF 다운로드
