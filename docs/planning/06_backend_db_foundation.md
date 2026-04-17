# Backend DB Foundation

> Historical snapshot for Task 2/3.  
> Current live status for later phases is tracked in:
> - `docs/planning/07_backend_ingestion.md`
> - `docs/planning/09_backend_embedding_plan.md`
> - `docs/planning/10_backend_retrieval_plan.md`
>
> Update (2026-04-13):
> - retrieval MVP implementation and verification are now complete
> - latest retrieval state and metrics are tracked in `docs/planning/10_backend_retrieval_plan.md`
>
> Update (2026-04-14):
> - grounded answer generation MVP와 후속 안정화까지 완료
> - latest end-to-end backend status is tracked in `docs/ops/task6_answer_generation_status.md`
> - current live corpus is `1722` chunks after scenario-driven minimal data addition for SCN-003
>
> Update (2026-04-17):
> - RAG refinement, SCN-004 document draft API, and SCN-004 frontend demo flow are complete
> - next practical step is QA consistency, not DB schema work

## Goal

- Scope: Task 2, 3 only
- Goal: PostgreSQL + pgvector 기반의 최소 backend DB 레이어 구축
- Out of scope: retrieval API, agent, frontend, embedding 생성/적재 로직

## Fixed Inputs

- Chunking is complete and frozen for backend work.
- Source of truth: `backend/data/law_chunks/all_chunks.json`
- Fixed chunking as-of date: `2026-04-11`
- Fixed chunk count at implementation time: `1713`
- `data/legalize-kr/` must remain untouched.

## Why This Doc Exists

- Earlier planning docs describe the chunking phase and still reference older counts/baselines.
- This file is the continuation point for backend Task 2, 3 so work can resume cleanly after session reset.

## Completed Work

1. Implement `backend/app/db.py`
2. Implement `backend/app/models/law_chunk.py`
3. Add Alembic config and initial migrations for `law_chunks`
4. Apply migrations to local PostgreSQL

## Data Contract Snapshot

`all_chunks.json` currently contains 36 fields per chunk.

Important type decisions confirmed from the current dataset:

- `paragraph_no`: `null | int`
- `article_ordinal`: `int`
- `tier`: `int`
- `ministry`: `list[str]`
- `structure_path`: `null | string`
- `promulgation_date`: ISO date string
- `enforcement_date`: ISO date string
- `selected_as_of`: ISO date string, fixed at `2026-04-11`

## Schema Decisions

- Table name: `law_chunks`
- Primary key: `chunk_id`
- `ministry` uses `JSONB`
- `field` stays as DB column name, Python attribute becomes `law_field`
- `structure_path` is nullable because some 시행령/시행규칙 조문 have no chapter/section path
- Dates use PostgreSQL `DATE`
- `embedding` is `vector(768)` and nullable until Task 4
- Minimal index only on `law_name`

## Files Added Or Updated

- `backend/app/db.py`
- `backend/app/models/law_chunk.py`
- `backend/app/models/__init__.py`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/20260413_000001_create_law_chunks_table.py`
- `backend/alembic/versions/20260413_000002_make_structure_path_nullable.py`

## Environment Notes

- `backend/.env` is required at runtime.
- `DATABASE_URL` must be loaded from `backend/.env` using an explicit file path, not cwd-dependent lookup.
- Runtime env: conda env `law_main_road`
- Local PostgreSQL cluster is initialized under `backend/.pgdata/`
- PostgreSQL log path: `backend/logs/postgres.log`

## Verification

Completed verification:

```bash
cd backend
python3 -m py_compile app/db.py app/models/__init__.py app/models/law_chunk.py alembic/env.py alembic/versions/20260413_000001_create_law_chunks_table.py alembic/versions/20260413_000002_make_structure_path_nullable.py
alembic upgrade head
alembic current
```

Observed state after execution:

- Alembic head: `20260413_000002`
- PostgreSQL `vector` extension enabled
- `structure_path` nullable correction applied

## Next Step After This Task

- Historical next step at Task 2/3 completion time:
  - Implement chunk ingestion script from `all_chunks.json`
  - Generate embeddings
  - Store embeddings in `law_chunks.embedding`
  - Add vector index after embeddings are populated
- Current status:
  - chunk ingestion complete
  - embeddings complete
  - HNSW index complete
  - retrieval MVP complete
  - grounded answer complete
  - SCN-004 document draft API complete
