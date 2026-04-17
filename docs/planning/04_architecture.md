# Architecture

## Current MVP Architecture

기준일: `2026-04-17`

- data source: `data/legalize-kr/`
- processed data: `backend/data/law_chunks/all_chunks.json`
- backend: FastAPI
- database: PostgreSQL + pgvector
- frontend: Next.js SCN-004 After demo
- current DB state:
  - `law_chunks` table ready
  - `1722` rows ingested
  - `1722` embeddings populated
  - `vector` extension enabled
  - HNSW index `idx_law_chunks_embedding` ready
  - retrieval API `POST /api/v1/retrieve` ready
  - answer API `POST /api/v1/answer` ready
  - document draft API `POST /api/v1/documents/draft` ready
  - retrieval verification script ready
  - answer verification script ready
  - document draft verification script ready
  - retrieval eval runner ready
  - answer eval runner ready
- current focus:
  - RAG refinement landing 완료
  - SCN-004 document draft backend 완료
  - SCN-004 After frontend flow 완료
  - QA 정합성 검증 및 demo stability

---

## Implemented Flow

- law data load
- chunk storage
- embedding generation
- embedding persistence in `law_chunks.embedding`
- HNSW vector index
- vector / keyword retrieval
- relevant article selection
- grounded response generation
- citation grounding validation
- document draft generation from answer legal basis + case intake
- frontend SCN-004 4-route fixed flow
- bounded answer / document draft / frontend build verification

---

## Planned Expansion

- Gemini API MVP first
- later consider GCP + Ollama Local LLM
- reranker / critic are post-MVP items
- query decomposition is already limited to `SCN-001 Full` demo path under `top_k >= 8`
- next practical step is QA consistency, not model swap or broad feature expansion
