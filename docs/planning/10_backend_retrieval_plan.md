# 10. Backend Retrieval Plan (Task 5 Complete)

## 목적

Task 4 embedding 완료 상태를 바탕으로 시작한 retrieval MVP의 구현/검증 결과를 정리한 문서다.

이번 단계의 목표는:

- 자연어 질문을 임베딩하고
- pgvector HNSW 인덱스를 사용해 관련 법령 청크를 검색하고
- citation 기반 응답 생성 단계가 바로 사용할 수 있는 retrieval API를 제공하는 것

이번 문서는 retrieval MVP 결과를 기록한 문서이며, 현재는 answer generation까지 완료된 상태에서 retrieval 기준선을 보존하는 역할을 한다.

---

## 현재 상태

- source of truth: `backend/data/law_chunks/all_chunks.json`
- selected_as_of: `2026-04-11`
- total chunks: `1722`
- `law_chunks` ingestion 완료
- `law_chunks.embedding`: `1722 / 1722` populated
- vector dimension: `768`
- HNSW index: `idx_law_chunks_embedding`
- Alembic head: `20260421_000005`
- eval dataset: `eval/mvp_in_scope_eval_v1.json`
  - top-level object 안의 `items` 배열에 `60` 문항 존재

현재 backend에는 retrieval app / service / verification / eval runner까지 구현되어 있다.
이후 grounded answer generation과 후속 안정화도 완료되었다. 최신 end-to-end 상태는 `docs/ops/README.md`를 함께 본다.
시나리오 기준 현재 상태는 `docs/planning/12_scenario_expansion_plan.md`를 함께 본다.
2026-04-17 기준 RAG refinement, SCN-004 document draft API, SCN-004 frontend flow, SCN-004 QA/content rehearsal도 완료되었다.
2026-04-20 기준 presentation-local preset, SCN-004 free-input guard, demo preflight, full 60 answer evidence report까지 완료되었으며 retrieval 구조 변경은 현재 freeze 범위가 아니다.

---

## 이번 세션 실행 결과

- `backend/main.py` 구현 완료
- `backend/app/services/embedding.py` 구현 완료
  - `RETRIEVAL_QUERY`
  - `output_dimensionality=768`
  - `embed_chunks.py`와 동일한 Vertex 인증 전략 재사용
- `backend/app/services/retrieval.py` 구현 완료
  - cosine distance `<=>`
  - same-transaction `SET LOCAL hnsw.ef_search`
  - ordered unique `cited_articles`
- `POST /api/v1/retrieve` 구현 완료
- `backend/verify/check_retrieval.py` 구현 완료
- `eval/run_retrieval_eval.py` 구현 완료
- live 검증 결과:
  - query embedding direct call dimension `768`
  - sample retrieval query top-1 = `근로기준법 제17조 (근로조건의 명시)`
  - `GET /` -> `200`
  - `POST /api/v1/retrieve` -> `200`
  - blank query -> `422`
- retrieval eval 결과 (`top_k=5`, `ef_search=100`)
  - `hit@1 = 51/60 (85.00%)`
  - `hit@3 = 59/60 (98.33%)`
  - `hit@5 = 60/60 (100.00%)`
- 후속 안정화:
  - Vertex / DB 장애 시 router에서 `503` 응답으로 매핑
  - `KLS-EVAL-019` miss 원인을 query embedding normalization으로 보정

---

## 이번 단계 범위

### In Scope

- FastAPI app 최소 골격 생성
- query embedding 서비스 구현
- pgvector cosine retrieval 서비스 구현
- `POST /api/v1/retrieve` 구현
- `cited_articles` 반환 구조 고정
- 단건 retrieval 검증 스크립트
- eval runner로 `hit@1`, `hit@3`, `hit@5` 측정

### Out Of Scope

- 당시 기준 LLM answer generation
- agent integration
- frontend integration
- BM25 / hybrid retrieval
- reranker
- query decomposition
- out-of-scope abstention 정책

---

## 추천 선택안

추천안은 **Vector-only Retrieval MVP**다.

이 안을 선택하는 이유:

- 이미 `gemini-embedding-001` + `pgvector` + `HNSW`까지 준비되어 있음
- 원 retrieval MVP 구현 당시 데이터 규모 `1713` rows에서 구조가 단순하고 안정적이었음
- current live `1722` rows 기준으로도 같은 구조를 유지 중임
- retrieval 품질 문제를 먼저 측정한 뒤 hybrid/BM25를 추가해도 늦지 않음
- 구현 범위를 backend retrieval 계층으로 좁힐 수 있음

이번 단계에서는 hybrid retrieval을 옵션 메모로만 남기고 구현하지 않는다.
현재도 retrieval baseline 자체는 유지 중이며, 다음 개선 포인트는 retrieval 교체보다 clause ranking과 answer-side selection이다.
복합 시나리오 질의(`SCN-001` 등)에서는 data gap보다 retrieval ranking이 병목으로 확인되어, query decomposition / sub-query union은 후속 개선 후보로 남긴다.

---

## 구현 원칙

- 검색 결과에 없는 조문 인용 금지
- `cited_articles`는 반드시 검색 결과 `citation_label`에서만 파생
- 기존 migration `000001`, `000002`, `000003` 수정 금지
- 기존 DB schema / ingestion 동작 변경 금지
- SQLAlchemy 2.0 스타일 유지
- Vertex query embedding 구현은 현재 `embed_chunks.py`와 동일한 인증 전략을 따라야 함
  - ADC (`gcloud auth application-default login`)
  - 또는 `GOOGLE_APPLICATION_CREDENTIALS`

---

## 목표 아키텍처

```text
User query
  -> embed_query(query, task_type="RETRIEVAL_QUERY", output_dimensionality=768)
  -> search_law_chunks(query_vector, top_k=5, ef_search=100)
  -> RetrievalResponse
       - chunks
       - cited_articles
       - total
```

RetrievalResponse의 `cited_articles`만 다음 단계 LLM이 인용 가능하다.
현재는 이 원칙 위에 grounded answer route가 구현되어 있다.

---

## 구현 대상 파일

### 신규 파일

- `backend/main.py`
  - FastAPI app 생성
  - router 등록
  - health check endpoint 제공
- `backend/app/routers/__init__.py`
- `backend/app/routers/retrieval.py`
  - `POST /api/v1/retrieve`
- `backend/app/services/__init__.py`
- `backend/app/services/embedding.py`
  - query embedding 전용 Vertex 클라이언트
- `backend/app/services/retrieval.py`
  - pgvector 검색 로직
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/retrieval.py`
  - request / response Pydantic 모델
- `backend/verify/check_retrieval.py`
  - 단건 CLI 검증
- `eval/run_retrieval_eval.py`
  - eval dataset 기준 hit rate 계산

### 수정 파일

- `backend/requirements.txt`
  - `fastapi`
  - `uvicorn[standard]`

`httpx`는 이번 단계에서 추가하지 않았다. API smoke test는 로컬 HTTP 호출로 확인했고, eval runner는 service layer 직접 호출 기준으로 구현했다.

---

## API 설계

### Route

- `POST /api/v1/retrieve`

### Request

```python
class RetrievalRequest(BaseModel):
    query: str
    top_k: int = Field(5, ge=1, le=10)
    ef_search: int = Field(100, ge=10, le=500)
```

추가 규칙:

- `query.strip()` 결과가 비어 있으면 422

### Response

```python
class ChunkResult(BaseModel):
    chunk_id: str
    citation_label: str
    law_name: str
    article_no: str
    article_title: str
    paragraph_no: int | None
    content: str
    similarity: float
    tier: int
    structure_path: str | None


class RetrievalResponse(BaseModel):
    query: str
    total: int
    chunks: list[ChunkResult]
    cited_articles: list[str]
```

### Citation 규칙

- `cited_articles`는 `chunks[*].citation_label`의 ordered unique list
- retrieval 결과에 없는 citation은 생성 금지

---

## Query Embedding 설계

모델:

- `gemini-embedding-001`
- `task_type="RETRIEVAL_QUERY"`
- `output_dimensionality=768`

구현 원칙:

- 현재 runtime / batch embedding path와 동일하게 `google.genai` 경로 사용
- 인증 초기화 로직도 동일한 전략 사용
- 쿼리 벡터 길이 `768` 검증 필수

---

## Vector Retrieval 설계

### 검색 방식

- pgvector cosine distance operator: `<=>`
- index와 동일하게 cosine 기반 유지

### 런타임 파라미터

- `top_k`: 기본 `5`
- `ef_search`: 기본 `100`
- threshold는 이번 MVP에서 두지 않음

### SQL 레벨 원칙

동일 트랜잭션 안에서:

```sql
SET LOCAL hnsw.ef_search = 100;
SELECT ...
FROM law_chunks
ORDER BY embedding <=> :query_vector
LIMIT :top_k;
```

주의:

- `SET LOCAL`은 같은 트랜잭션 안에서만 유효
- 구현 시 `Session.begin()` 또는 동일 세션의 명시적 트랜잭션 범위를 보장해야 함

### SQLAlchemy 원칙

기존 코드베이스와 맞추기 위해 `db.query(...)`보다 `select(...)` + `session.execute(...)`를 우선한다.

예상 반환 필드:

- `chunk_id`
- `citation_label`
- `law_name`
- `article_no`
- `article_title`
- `paragraph_no`
- `content`
- `tier`
- `structure_path`
- `similarity = 1 - (embedding <=> query_vector)`

---

## Eval 설계

평가 입력:

- `eval/mvp_in_scope_eval_v1.json`
- 주의: top-level list가 아니라 object이며, 실제 문항은 `items` 아래에 있음

측정 지표:

- `hit@1`
- `hit@3`
- `hit@5`
- `question_type`별 breakdown
- 실패 케이스 목록

matching 기준:

- `gold_citations` 중 하나라도 top-k의 `citation_label`에 포함되면 hit

---

## Phase 계획

### Phase 1. App Skeleton

목적:

- FastAPI 앱 골격 생성

수정 파일:

- `backend/main.py`
- `backend/app/routers/__init__.py`
- `backend/app/routers/retrieval.py`
- `backend/requirements.txt`

검증:

- 구현 완료
- `GET /` 200 확인 완료

### Phase 2. Query Embedding Service

목적:

- query -> 768-dim vector

수정 파일:

- `backend/app/services/__init__.py`
- `backend/app/services/embedding.py`

검증:

- 직접 함수 호출로 vector length `768` 확인 완료

### Phase 3. Retrieval Service

목적:

- vector search 동작 확인

수정 파일:

- `backend/app/services/retrieval.py`
- `backend/verify/check_retrieval.py`

검증:

- CLI query top-5 결과와 citation 출력 확인 완료

### Phase 4. API Completion

목적:

- retrieval API 완성

수정 파일:

- `backend/app/schemas/__init__.py`
- `backend/app/schemas/retrieval.py`
- `backend/app/routers/retrieval.py`

검증:

- 로컬 HTTP 호출로 `POST /api/v1/retrieve` 검증 완료
- `chunks`, `cited_articles`, `total` 확인 완료

### Phase 5. Eval Runner

목적:

- retrieval 품질 정량 확인

수정 파일:

- `eval/run_retrieval_eval.py`

검증:

- `60` items 실행 완료
- `hit@1`, `hit@3`, `hit@5` 출력 완료
- 최종 `hit@5_failures = 0`

---

## 리스크

### 1. GCP 인증 미설정

영향:

- query embedding 호출 실패

대응:

- `embed_chunks.py`와 동일한 인증 경로 재사용

### 2. `SET LOCAL` 적용 범위 실수

영향:

- `ef_search`가 의도대로 반영되지 않을 수 있음

대응:

- retrieval search 함수 내부에서 동일 트랜잭션 보장

### 3. similarity 값 해석 혼동

영향:

- 디버깅 시 값 해석 혼란

대응:

- 응답에는 `similarity`를 노출하되, 내부 정렬 기준은 distance 그대로 유지

### 4. eval runner가 dataset 구조를 잘못 읽는 문제

영향:

- eval script 초기 실패

대응:

- 반드시 `payload["items"]`를 읽도록 구현

### 5. retrieval 품질 부족

영향:

- top-1 품질은 여전히 추가 개선 여지가 있음

대응:

- 현재 baseline은 `ef_search=100`, `top_k=5`
- 현재 `hit@5`는 `60/60`, `hit@1`은 `51/60`
- hybrid/BM25는 다음 단계 옵션으로 보류

---

## Historical 다음 세션 체크리스트

아래 목록은 retrieval MVP 완료 시점의 handoff 메모다. 현재는 answer generation, RAG refinement, SCN-004 document draft, frontend demo까지 완료되었으므로 그대로 실행하지 않는다.

1. citation-grounded answer generation 연결
2. retrieval 결과를 agent / frontend에서 소비하도록 연결
3. top-1 개선 필요 시 query hint normalization 확장 여부 측정
4. out-of-scope / abstention eval 분리
5. Vertex SDK deprecation 대응 계획 수립

Current live next step note:

- answer generation MVP와 후속 안정화는 이미 완료되었다.
- RAG refinement도 landing 완료 상태다.
- 현재 실제 다음 단계는 SCN-004 demo freeze 유지와 제출 전 재현성 확인이다.
- retrieval 구조는 QA에서 regression이 재현될 때만 좁게 수정한다.

---

## Historical 추천 구현 순서

`Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5`

특히:

- Phase 3 단건 검색 검증 전에는 API 완성 단계로 넘어가지 말 것
- Eval은 retrieval API가 아니라 service layer 기준으로 먼저 통과시키는 것이 안전함
