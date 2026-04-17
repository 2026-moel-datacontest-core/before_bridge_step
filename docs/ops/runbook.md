# Runbook

기준일: `2026-04-17`

## 목적

SCN-004 After document draft demo와 QA 정합성 검증을 실행하기 위한 최소 운영 절차다.

현재 기준:

- RAG refinement landing 완료
- SCN-004 document draft backend 완료
- SCN-004 After frontend 4-route flow 완료
- QA 중심은 신규 기능 확장이 아니라 demo freeze 전 정합성 확인
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
- SCN-005 / SCN-001 문서 타입 추가
- sessionStorage backup/restore
- backend API contract 변경
- data/legalize-kr 직접 수정
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response` Web Storage 저장
