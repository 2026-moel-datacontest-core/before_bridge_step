# Backend Ingestion

## Goal

- Scope: DB migration 이후 바로 사용할 수 있는 chunk ingestion 준비
- Input: `backend/data/law_chunks/all_chunks.json`
- Output: `law_chunks` 테이블에 upsert 가능한 적재 스크립트

## Current Environment Status

- `backend/.env` configured
- conda env `law_main_road` has required backend packages
- local PostgreSQL + pgvector configured and running on `localhost:5432`
- `law_chunks` migration applied through Alembic head `20260413_000003`

## Implemented Path

- script path: `backend/scripts/ingest_chunks.py`
- strategy: PostgreSQL upsert on `chunk_id`
- date fields are parsed from ISO string to `date`
- `field` JSON key is mapped to DB column `field`
- rerunnable by design
- `embedding` column is excluded from update set
- unknown and missing key validation both enabled

## Runtime Expectations

Required before execution:

1. `backend/.env` exists with a valid `DATABASE_URL`
2. backend Python dependencies are installed
3. `alembic upgrade head` has already created `law_chunks`

## Recommended Run Order

```bash
cd backend
alembic upgrade head
python3 scripts/ingest_chunks.py
```

Optional:

```bash
cd backend
python3 scripts/ingest_chunks.py --batch-size 200
python3 scripts/ingest_chunks.py --dry-run
```

## Notes

- The script is intentionally limited to chunk ingestion only.
- Embedding generation and vector index creation were completed in Task 4.
- If the chunk file changes later, rerunning the script updates rows by `chunk_id`.
- **`embedding` column is excluded from `on_conflict_do_update`.** Re-running ingestion after Task 4 embeddings are stored will not overwrite them.
- **`EXPECTED_KEYS` validates both unknown and missing keys.** If a chunk is missing a required field, the script raises `ValueError` before any DB writes occur.
- **Migration note:** Always run `alembic upgrade head` (not just 000001) before ingestion. Migration 000001 creates `structure_path` as NOT NULL; migration 000002 corrects it to nullable. Applying only 000001 will cause NOT NULL violations on ingestion.

## Completed Result

- dry-run validation passed for `1713` chunks
- actual ingestion completed
- `law_chunks` row count: `1713`
- `DISTINCT chunk_id`: `1713`

## Next Step

- Historical next step at ingestion completion time:
  - embedding generation script implemented
  - `law_chunks.embedding` populated for all `1713` rows
  - sample vector dimension verified at `768`
  - HNSW vector index added through Alembic `20260413_000003`
  - retrieval 단계로 진행 예정이었음
- Current status (2026-04-13):
  - retrieval MVP 구현 및 검증 완료
  - latest retrieval details live in `docs/planning/10_backend_retrieval_plan.md`
- Current status (2026-04-14):
  - answer generation MVP 및 안정화 완료
  - latest end-to-end backend baseline lives in `docs/ops/task6_answer_generation_status.md`
  - scenario expansion update:
    - `SCN-003` 대응으로 장애인 관련 조문 9개를 최소 범위로 추가
    - current live `law_chunks` row count: `1722`
    - current live `embedding` populated: `1722 / 1722`
