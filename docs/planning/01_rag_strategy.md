# RAG Strategy

## Data Source
- source: `data/legalize-kr/`
- processed: `backend/data/law_chunks/all_chunks.json`

## Retrieval Direction
- 법령 본문 중심
- 이후 embedding + vector search 준비
- citations 기반 응답 강제

## Current Phase
- chunking complete
- next: embedding and indexing