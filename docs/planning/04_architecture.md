# Architecture

## Current MVP Architecture

- data source: `data/legalize-kr/`
- processed data: `backend/data/law_chunks/all_chunks.json`
- backend: FastAPI
- database: PostgreSQL + pgvector
- current DB state:
  - `law_chunks` table ready
  - `1722` rows ingested
  - `1722` embeddings populated
  - `vector` extension enabled
  - HNSW index `idx_law_chunks_embedding` ready
  - retrieval API `POST /api/v1/retrieve` ready
  - answer API `POST /api/v1/answer` ready
  - retrieval verification script ready
  - answer verification script ready
  - retrieval eval runner ready
  - answer eval runner ready
- current focus:
  - scenario expansion data coverage verified
  - clause ranking / adjacent grounded context expansion
  - retrieval-grounding-answer 품질 개선
  - frontend / agent 연결 전 기준선 유지

---

## Planned Flow

- law data load
- chunk storage
- embedding generation
- embedding persistence in `law_chunks.embedding`
- HNSW vector index
- vector / keyword retrieval
- relevant article selection
- grounded response generation
- citation grounding validation
- bounded answer eval / verification

---

## Planned Expansion

- Gemini API MVP first
- later consider GCP + Ollama Local LLM
- reranker / critic / query decomposition are post-MVP items
- next practical step is RAG refinement, not model swap
