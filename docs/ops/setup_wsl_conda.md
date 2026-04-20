# WSL Conda Setup

기준일: `2026-04-20`

## Environment

- OS: WSL Ubuntu
- Python env: conda `law_main_road`
- Backend: FastAPI
- DB: PostgreSQL + pgvector
- Frontend: Next.js

## Backend Env

```bash
conda activate law_main_road
python --version
```

Backend runtime expects `backend/.env`.

주요 값:

- `DATABASE_URL`
- `GCP_PROJECT`
- `GCP_LOCATION`
- `GOOGLE_APPLICATION_CREDENTIALS` 또는 ADC

## DB

현재 기준:

- `law_chunks` rows: `1722`
- embedding: `1722 / 1722`
- HNSW index: `idx_law_chunks_embedding`
- alembic head: `20260413_000003`

확인:

```bash
(cd backend && alembic current)
python backend/verify/check_embeddings.py --require-complete --require-index
```

## Frontend Env

```bash
cd frontend
npm install
npm run build
npm run dev
```

기본 API 주소는 `http://localhost:8000`이다. 다른 주소를 쓸 때만 설정한다.

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Current QA Target

현재 설정 확인의 목적은 SCN-004 frontend/backend 정합성 검증이다.

확인 대상:

- `/api/v1/answer`
- `/api/v1/documents/draft`
- `/after` 4-route frontend flow
- copy / print
- direct URL guard

발표 전 기본 확인은 repo root에서 아래 script를 우선 사용한다.

```bash
bash scripts/demo_preflight.sh
```

이 script는 DB를 start/stop하지 않고 readiness만 확인하며, backend/frontend dev server도 자동 실행하지 않는다. WSL browser QA는 `frontend`의 Playwright Chromium을 우선 사용한다.
