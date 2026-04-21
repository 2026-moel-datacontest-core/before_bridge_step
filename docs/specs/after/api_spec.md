# After API Spec

- 상태: current code-based draft
- 기준: main backend/frontend 현재 코드
- 범위: main After/RAG API surface

이 문서는 `z_before_begin/`의 Before/Begin contract review API가 아니라, main `backend/` FastAPI와 main `frontend/` Next.js After/RAG flow가 사용하는 API contract를 정리한다. Before/Begin API와 endpoint, schema, Vertex 사용 경계를 섞지 않는다.

## 1. Scope

After API는 법률 질의에서 시작해 검색 근거 기반 답변과 SCN-004 문서 초안으로 이어지는 main API surface다.

```text
법률 질의
  -> POST /api/v1/answer
       -> Shared Retrieval Service
       -> Vertex query embedding
       -> PostgreSQL + pgvector law_chunks search
       -> Gemini grounded answer generation
  -> /after/result SCN-004 draft eligibility guard
  -> /after/intake case_intake collection
  -> POST /api/v1/documents/draft
       -> deterministic draft builder
       -> rendered_text / missing_fields / cautions / evidence_checklist
```

현재 API-connected main frontend 호출 범위는 `/after`, `/after/result`, `/after/intake`, `/after/draft`의 4-route flow다. 전체 frontend 구현에는 `/` static scaffold/entry route도 있지만, 이 문서의 API-connected After flow route 범위에는 포함하지 않는다. `/api/v1/retrieve`는 public retrieval endpoint로 구현되어 있지만, 현재 main frontend의 shared API client는 직접 호출하지 않는다. `/api/v1/answer`도 public `/api/v1/retrieve` endpoint를 HTTP로 재호출하지 않고 같은 retrieval service path를 직접 사용한다.

`/api/v1/documents/draft`는 request의 `case_intake`와 `legal_basis`만 사용해 deterministic draft를 만든다. **After draft path does not call Vertex AI.**

## 2. Runtime / Base URL

| 항목 | 현재 구현 기준 |
|---|---|
| Frontend API base | `NEXT_PUBLIC_API_BASE_URL` |
| Frontend default API base | `http://localhost:8000` |
| Backend local run | `uvicorn backend.main:app --reload` |
| API-connected frontend routes | `/after`, `/after/result`, `/after/intake`, `/after/draft` |
| Backend router prefix | `/api/v1` and `/api/v1/documents` |
| CORS default | `https?://(localhost|127\.0\.0\.1):30[0-9]{2}` |

## 3. Environment / Model Defaults

| 항목 | 현재 코드 |
|---|---|
| Default embedding model | `gemini-embedding-001` |
| Embedding task type | `RETRIEVAL_QUERY` |
| Embedding dimension | `768` |
| Default answer model | `gemini-2.5-flash` |
| Answer env override | `VERTEX_ANSWER_MODEL` |
| Required Vertex location env | `GCP_LOCATION` |
| Project env | `GCP_PROJECT`; 없으면 ADC project 사용 |
| Credentials | `GOOGLE_APPLICATION_CREDENTIALS` 또는 ADC |
| DB env | `DATABASE_URL` |
| Embedding hard timeout env | `VERTEX_EMBEDDING_HARD_TIMEOUT_SECONDS`, default `15.0` seconds |
| Answer hard timeout env | `VERTEX_ANSWER_HARD_TIMEOUT_SECONDS`, default `25.0` seconds |
| Shared provider retry env | `VERTEX_PROVIDER_MAX_RETRIES`, default `2` |
| Shared provider retry backoff env | `VERTEX_PROVIDER_RETRY_BASE_SECONDS`, default `1.0` seconds |

고정 presentation preset exact path는 frontend fixture를 사용한다. `SCN-004-DEMO-FREEZE` exact query와 `SCN-001-BRIDGE-DEMO` exact query는 `/api/v1/answer`를 호출하지 않으므로 Vertex query embedding이나 Gemini answer generation을 호출하지 않는다.

현재 public `AnswerRequest` schema에는 `model_name` field가 없다. service 내부 `answer_question(..., model_name=None)`와 `VERTEX_ANSWER_MODEL` override는 있지만, router는 request에서 `model_name`을 받지 않는다.

## 4. Endpoint Inventory

| Method | Path | Caller | Purpose | Request schema | Response schema | Vertex 사용 여부 | Storage/state | 주요 guard/error |
|---|---|---|---|---|---|---|---|---|
| `POST` | `/api/v1/retrieve` | Public API / verification; current frontend client does not call it directly | Query embedding 후 `law_chunks` vector search 결과 반환 | `RetrievalRequest` | `RetrievalResponse` | Yes: query embedding only | Backend does not persist request/response; DB has `law_chunks.embedding` | blank `query` 422, schema 422, provider/database errors |
| `POST` | `/api/v1/answer` | `/after` modified preset/free input path | Retrieval 결과 기반 grounded legal answer 생성 | `AnswerRequest` | `AnswerResponse` | Yes: query embedding + Gemini answer generation | React Context memory state; backend does not persist request/response | blank `query` 422, retrieval/provider errors, grounded response validation 502 |
| `POST` | `/api/v1/documents/draft` | `/after/intake` | SCN-004 document draft 생성 | `DocumentDraftRequest` | `DocumentDraftResponse` | No. After draft path does not call Vertex AI. | React Context memory state; backend does not persist draft | Pydantic/FastAPI validation 422; service has deterministic fallback for non-special valid enum types |

## 5. POST /api/v1/retrieve

### Purpose

`query`를 embedding하고 PostgreSQL `law_chunks` table의 pgvector/HNSW search 결과를 반환한다. 이 endpoint는 public endpoint지만 `/api/v1/answer`는 이 endpoint를 HTTP로 호출하지 않는다. 둘 다 shared retrieval service인 `retrieve_law_chunks()` path를 사용한다.

### Request: `RetrievalRequest`

| Field | Type | Required | Default | Validation |
|---|---|---:|---|---|
| `query` | `str` | Yes | - | router에서 `.strip()` 후 blank이면 422 |
| `top_k` | `int` | No | `5` | `ge=1`, `le=10` |
| `ef_search` | `int` | No | `100` | `ge=10`, `le=500` |

`RetrievalRequest`는 `extra="forbid"`다. 현재 구현의 `top_k` 상한은 `20`이 아니라 `10`이다.

### Response: `RetrievalResponse`

| Field | Type | Note |
|---|---|---|
| `query` | `str` | original stripped query |
| `total` | `int` | returned chunk count |
| `chunks` | `ChunkResult[]` | retrieval chunks |
| `cited_articles` | `str[]` | returned chunks의 unique `citation_label` |

현재 response에는 `top_k`나 `results` field가 없다.

### `ChunkResult`

| Field | Type | Note |
|---|---|---|
| `chunk_id` | `str` | `law_chunks` primary key |
| `citation_label` | `str` | UI/answer citation label |
| `law_name` | `str` | law name |
| `article_no` | `str` | article number |
| `article_title` | `str` | article title |
| `paragraph_no` | `int | null` | paragraph if split |
| `content` | `str` | retrieved chunk body |
| `similarity` | `float` | `1.0 - cosine_distance` |
| `tier` | `int` | corpus tier |
| `structure_path` | `str | null` | part/chapter path |

주의: public `/api/v1/retrieve`의 `ChunkResult`에는 `context_id`가 없다. `context_id`는 `/api/v1/answer`의 `GroundedChunkResult`에서 1부터 부여된다. 현재 field명도 `score`가 아니라 `similarity`다.

### Model / Data Path

| Step | Code path |
|---|---|
| Query cleanup | `retrieve_law_chunks()` -> `normalize_grounding_query()` |
| Query hinting | `build_query_embedding_text()` |
| Embedding | `embed_query()` -> Vertex `gemini-embedding-001`, `RETRIEVAL_QUERY`, `768` dimensions |
| Optional selective decomposition | `SCN-001 Full` marker path, only when `top_k >= 8` |
| Vector search | `search_law_chunks()` |
| DB | PostgreSQL `law_chunks`, pgvector `Vector(768)` |
| HNSW | `SET LOCAL hnsw.ef_search = {ef_search}` after range validation |
| Ranking | `LawChunk.embedding.cosine_distance(query_vector)` ascending |

### Error / Status Codes

| Condition | Status | Detail |
|---|---:|---|
| Blank query | `422` | `query must not be blank` |
| `ValueError` from params/query | `422` | `str(exc)`; e.g. `top_k must be between 1 and 10.` |
| `DefaultCredentialsError`, `FileNotFoundError`, `GoogleAPICallError`, `GenAIAPIError`, `RequestException`, `RetryError`, `TransportError`, `VertexEmbeddingError` | `503` | `query embedding is currently unavailable` |
| `VertexProviderTimeoutError` | `503` | `query embedding provider timed out` |
| `VertexProviderRuntimeError` | `503` | `query embedding is currently unavailable` |
| `SQLAlchemyError` | `503` | `retrieval database is currently unavailable` |
| unexpected exception | `500` | `internal retrieval error` |

현재 router는 retrieval provider timeout을 `504`가 아니라 `503`으로 반환한다.

## 6. POST /api/v1/answer

### Purpose

검색된 법령 chunk만 근거로 grounded legal answer를 생성한다. 답변에는 `cited_articles`, `grounded_context_ids`, `retrieved_chunks`가 포함되어야 하며, frontend는 이 값을 이용해 SCN-004 draft eligibility와 `legal_basis`를 만든다.

### Request: `AnswerRequest`

| Field | Type | Required | Default | Validation |
|---|---|---:|---|---|
| `query` | `str` | Yes | - | router에서 `.strip()` 후 blank이면 422 |
| `top_k` | `int` | No | `5` | `ge=1`, `le=10` |
| `ef_search` | `int` | No | `100` | `ge=10`, `le=500` |

`AnswerRequest`는 `extra="forbid"`다. 현재 public request schema에는 `model_name` field가 없다.

### Response: `AnswerResponse`

| Field | Type | Note |
|---|---|---|
| `query` | `str` | original stripped query |
| `answer` | `str` | 1-2 sentence grounded answer target |
| `key_points` | `str[]` | grounded key points |
| `cautions` | `str[]` | limitations/cautions |
| `cited_articles` | `str[]` | `grounded_context_ids`에서 만든 unique citation labels |
| `grounded_context_ids` | `int[]` | answer가 실제 사용한 retrieved context IDs |
| `retrieved_chunks` | `GroundedChunkResult[]` | retrieval result chunks with `context_id`; cited subset은 `grounded_context_ids`로 구분 |
| `retrieval_total` | `int` | retrieval returned chunk count |
| `model_name` | `str` | resolved answer model name |

`GroundedChunkResult`는 `ChunkResult`에 `context_id: int`를 추가한 shape다.

### Shared Retrieval Service

`/api/v1/answer` call path는 다음과 같다.

```text
answer router
  -> answer_question(query, top_k, ef_search)
       -> retrieve_law_chunks(query, top_k, ef_search)
            -> embed_query()
            -> PostgreSQL/pgvector search
       -> generate_grounded_answer()
            -> Gemini generate_content()
```

중요: `/api/v1/answer`는 public `/api/v1/retrieve` endpoint를 HTTP로 재호출하지 않는다. shared retrieval service를 직접 호출한다.

### Model / Grounding Path

| Step | Code path / rule |
|---|---|
| Retrieval | `retrieve_law_chunks()` direct service call |
| Query embedding | Vertex `gemini-embedding-001` |
| DB search | PostgreSQL + pgvector `law_chunks` |
| Answer model | default `gemini-2.5-flash`, override via `VERTEX_ANSWER_MODEL` |
| Prompt | retrieved contexts are enumerated as `[context_id=N]` |
| Model output schema | JSON with `cited_context_ids`, `answer`, `key_points`, `cautions` |
| Context ID validation | `normalize_grounded_context_ids()` rejects unknown/empty IDs |
| Citation postprocess | targeted family-care, foreign-worker, and SCN-004 citation expansions may add valid retrieved context IDs |
| Citation build | `build_cited_articles_from_context_ids()` |
| Final validation | `validate_explicit_citation_grounding()` prevents outside retrieved/grounded citation use |

법률 답변에는 `cited_articles`와 `grounded_context_ids`가 필요하다. answer model은 retrieved `context_id`를 cite해야 하며, unknown context ID나 빈 citation set은 validation error로 처리된다.

### Frontend Defaults

| Path | Current frontend behavior |
|---|---|
| `SCN-004-DEMO-FREEZE` exact preset | fixed `AnswerResponse` fixture from `scenarioPresetAnswers.json`; `/api/v1/answer` not called |
| `SCN-001-BRIDGE-DEMO` exact preset | fixed answer-only fixture; `/api/v1/answer` not called; draft unsupported |
| presentation preset modified path | `top_k=10`, `ef_search=100`, calls `/api/v1/answer` |
| free input path | `top_k=5`, `ef_search=100`, calls `/api/v1/answer` |

Modified/free input query는 Vertex query embedding 및 Gemini answer generation으로 전달될 수 있다.

### Error / Status Codes

| Condition | Status | Detail |
|---|---:|---|
| Blank query | `422` | `query must not be blank` |
| `ValueError` from params/query | `422` | `str(exc)` |
| `GroundedAnswerGenerationError` with invalid JSON/payload/empty/unknown context/cited context message | `502` | `answer model returned an invalid grounded response` |
| other `GroundedAnswerGenerationError` | `502` | `grounded answer generation failed validation` |
| `DefaultCredentialsError`, `FileNotFoundError`, `GoogleAPICallError`, `GenAIAPIError`, `RequestException`, `RetryError`, `TransportError`, `VertexEmbeddingError` | `503` | `answer generation is currently unavailable` |
| `VertexProviderTimeoutError` | `503` | `answer generation provider timed out` |
| `VertexProviderRuntimeError` | `503` | `answer generation is currently unavailable` |
| `SQLAlchemyError` | `503` | `retrieval database is currently unavailable` |
| unexpected exception | `500` | `internal answer generation error` |

현재 answer router도 provider timeout을 `504`가 아니라 `503`으로 반환한다.

## 7. POST /api/v1/documents/draft

### Purpose

SCN-004 문서 초안을 생성한다. request의 `case_intake`와 `legal_basis`를 deterministic template/service로 결합해 `DocumentDraftResponse`를 반환한다.

**After draft path does not call Vertex AI.**

### Request: `DocumentDraftRequest`

| Field | Type | Required | Note |
|---|---|---:|---|
| `case_intake` | `CaseIntake` | Yes | user-provided or placeholder case facts |
| `legal_basis` | `LegalBasisInput` | Yes | previous answer-derived legal basis |

`StrictSchema` 기반 nested schema는 `extra="forbid"`, `str_strip_whitespace=True`, `str_min_length=1`을 사용한다. 일부 string field는 `null`을 허용한다.

### Response: `DocumentDraftResponse`

| Field | Type | Note |
|---|---|---|
| `document_type` | `DocumentType` | generated document type |
| `title` | `str` | document title |
| `recipient` | `str` | submit/recipient target |
| `language` | `DraftLanguage` | current frontend sends `ko` |
| `parties` | `DraftPartySection` | worker/employer display values |
| `facts` | `str[]` | deterministic facts from intake |
| `legal_basis` | `DraftLegalBasisSection[]` | filtered legal basis sections |
| `request` | `str[]` | request items |
| `evidence_checklist` | `str[]` | provided + default checklist |
| `missing_fields` | `str[]` | missing user facts or missing answer grounding fields |
| `cautions` | `str[]` | base cautions + answer cautions + deterministic cautions |
| `cited_articles` | `str[]` | citations included in generated legal basis sections |
| `source_context_ids` | `int[]` | response-level context ID list aggregated from legal basis sections, with fallback semantics below |
| `missing_legal_basis` | `str[]` | required citations absent from request `legal_basis` |
| `rendered_text` | `str` | assembled draft body for display/copy/print |

### Core Boundary

| Boundary | Current code |
|---|---|
| Router call | `draft_document(payload)` returns `build_document_draft(payload)` |
| Vertex | Not called |
| Retrieval service | Not imported/called by document draft service |
| Answer generation service | Not imported/called by document draft service |
| Legal basis source | request `legal_basis.cited_articles`, `source_context_ids`, `retrieved_chunks` only |
| Missing facts | placeholders or `missing_fields`; user-unprovided facts are not asserted |

### `DocumentType`

Backend enum currently includes more values than the frontend exposes.

| Value | Backend enum | Current special draft handling | Current frontend exposure |
|---|---:|---:|---:|
| `labor_office_wage_complaint` | Yes | Yes, SCN-004 wage complaint | Yes |
| `labor_commission_unfair_dismissal_brief` | Yes | Yes, SCN-004 unfair dismissal brief | Yes |
| `family_leave_reapplication` | Yes | Generic fallback metadata | No |
| `written_reason_request` | Yes | Generic fallback metadata | No |
| `certified_letter` | Yes | Generic fallback metadata | No |
| `workplace_change_reason_summary` | Yes | Generic fallback metadata | No |
| `consultation_case_summary` | Yes | Generic fallback metadata | No |

Valid non-SCN-004 enum values are not rejected by the backend service, but they use generic metadata (`사건 정리 문서 초안`, `제출처 확인 필요`) and broad article filtering. Main frontend currently sends only the two SCN-004 values.

### Legal Basis Filtering

| Document type | Allowed article keys | Required article keys |
|---|---|---|
| `labor_office_wage_complaint` | `lsa_36`, `retirement_9`, `lsa_37` | `lsa_36`, `retirement_9` |
| `labor_commission_unfair_dismissal_brief` | `lsa_23`, `lsa_26`, `lsa_27`, `lsa_28`, `lsa_rule_5` | `lsa_23`, `lsa_26`, `lsa_27`, `lsa_28` |
| Other valid backend enum values | all known `ARTICLE_LABELS` | none |

Article key labels:

| Key | Citation label |
|---|---|
| `lsa_23` | `근로기준법 제23조 (해고 등의 제한)` |
| `lsa_26` | `근로기준법 제26조 (해고의 예고)` |
| `lsa_27` | `근로기준법 제27조 (해고사유 등의 서면통지)` |
| `lsa_28` | `근로기준법 제28조 (부당해고등의 구제신청)` |
| `lsa_36` | `근로기준법 제36조 (금품 청산)` |
| `lsa_37` | `근로기준법 제37조 (미지급 임금에 대한 지연이자)` |
| `retirement_9` | `근로자퇴직급여 보장법 제9조 (퇴직금의 지급 등)` |
| `lsa_rule_5` | `근로기준법 시행규칙 제5조 (부당해고등의 구제신청)` |

`missing_legal_basis`는 required article keys 중 request `legal_basis.cited_articles`에 matching citation이 없는 항목이다.

`source_context_ids` semantics는 다음 순서다.

1. 우선 `legal_basis.retrieved_chunks` 기반으로 citation별 context id mapping을 만든다. 같은 article key로 matching되는 retrieved chunk의 `context_id`가 section별 `source_context_ids`에 들어간다.
2. retrieved chunk mapping이 전혀 없고 `legal_basis_input.cited_articles.length === legal_basis_input.source_context_ids.length`이면 citation/source_context_ids zip fallback으로 section별 `source_context_ids`를 채울 수 있다.
3. `legal_basis` section은 있는데 모든 section별 `source_context_ids`가 비어 있으면 response-level `source_context_ids`는 전체 `legal_basis_input.source_context_ids`로 fallback할 수 있다.

3번은 grounding evidence를 보존하기 위한 response-level fallback이다. 이 값을 citation별 retrieved chunk mapping과 동일하다고 단정하면 안 된다.

### Deterministic Output Assembly

| Output area | Builder behavior |
|---|---|
| `parties` | missing worker/employer values use placeholders |
| `facts` | document type별 deterministic fact list; timeline events included |
| `request` | document type별 fixed request items + user amounts/actions |
| `evidence_checklist` | user evidence descriptions + document type default checklist |
| `missing_fields` | document type별 required fact checks + legal basis presence checks |
| `cautions` | base cautions + prior answer cautions + deterministic cautions |
| `rendered_text` | title, recipient, parties, facts, legal basis, request, evidence, missing fields, cautions를 section text로 조립 |

### Error Handling

`document_draft` router는 별도 `HTTPException`을 던지지 않는다. 현재 확인되는 error surface는 Pydantic/FastAPI validation이다.

| Condition | Status | Note |
|---|---:|---|
| invalid JSON/body/schema | `422` | FastAPI/Pydantic validation |
| blank string in non-null `Text` field | `422` | `str_min_length=1` / `Text` |
| unknown extra field | `422` | `extra="forbid"` |
| invalid enum value | `422` | e.g. unknown `document_type` |

### Frontend Guard

| Route | Guard |
|---|---|
| `/after/result` | `hasDraftGrounding()` checks `cited_articles.length > 0` and `grounded_context_ids.length > 0`; `getScn004DraftEligibility()` filters SCN-004 document types |
| `/after/result` | `SCN-001-BRIDGE-DEMO` has `supportsDraft=false`, so answer-only |
| `/after/result` | supported SCN-004 document type is shown only when wage or dismissal evidence pattern matches query/citations/grounded chunks |
| `/after/intake` | answer missing -> `/after`; no grounding, no document type, or selected type not eligible -> `/after/result` |
| `/after/intake` submit | re-runs `getScn004DraftEligibility(answer)` before `fetchDraft()` |
| `/after/draft` | draft missing -> `/after` |

Grounded free input이라도 SCN-004 wage complaint / unfair dismissal evidence pattern이 없으면 answer-only로 남는다.

Draft request에는 `case_intake` 개인/사건 정보가 포함될 수 있지만 draft endpoint 자체는 Vertex를 호출하지 않는다.

## 8. Shared Frontend API Client

`frontend/src/lib/api.ts`는 answer/draft만 호출한다. 현재 shared client에는 `/api/v1/retrieve` 호출 함수가 없다.

| Function | Role |
|---|---|
| `fetchAnswer(request)` | `POST /api/v1/answer` |
| `fetchDraft(request)` | `POST /api/v1/documents/draft` |
| `buildLegalBasis(response)` | `AnswerResponse`에서 `LegalBasisInput` 생성; `grounded_context_ids`에 포함된 `retrieved_chunks`만 전달 |
| `buildCaseIntake(input)` | form/timeline/evidence input을 `CaseIntake`로 정리; empty row 제거 |
| `hasDraftGrounding(response)` | `cited_articles`와 `grounded_context_ids` non-empty check |
| `postJson()` | fetch wrapper with timeout and status mapping |

| Timeout / Error | Current code |
|---|---|
| `ANSWER_TIMEOUT_MS` | `30_000` ms |
| `DRAFT_TIMEOUT_MS` | `60_000` ms |
| Timeout mechanism | `AbortController` |
| Network/abort error | `ApiError(0, '연결을 확인하고 다시 시도해주세요.', true)` |
| `ApiError` shape | `status`, `message`, `retryable` |
| Answer `503` frontend message | `서버가 일시적으로 응답하지 않습니다. 잠시 후 다시 시도해주세요.` |
| Answer `4xx` frontend message | `입력 내용을 확인한 후 다시 시도해주세요.` |
| Answer `502` or `500` frontend message | `요청 처리 중 오류가 발생했습니다. 다시 시도해주세요.` |
| Draft `422` frontend message | `입력 값에 오류가 있습니다. 내용을 확인해주세요.` |
| Draft `>=500` frontend message | `문서 초안 생성에 실패했습니다. 다시 시도해주세요.` |

후속 screen_plan/data_model에서 user-facing error state를 다룰 때는 위 `createHttpError()` mapping을 기준으로 삼는다.

Fixed fixture path는 `frontend/src/lib/scenarioPresetAnswers.json`과 `SCENARIO_PRESETS`를 사용한다. State는 React Context + `useReducer` memory state다.

## 9. Shared Response / Data Shapes

### Retrieval

| Shape | Current backend fields |
|---|---|
| `RetrievalRequest` | `query`, `top_k=5`, `ef_search=100`; `top_k le=10`, `ef_search le=500` |
| `RetrievalResponse` | `query`, `total`, `chunks`, `cited_articles` |
| `ChunkResult` | `chunk_id`, `citation_label`, `law_name`, `article_no`, `article_title`, `paragraph_no`, `content`, `similarity`, `tier`, `structure_path` |

TODO: frontend has no current `RetrievalRequest` / `RetrievalResponse` mirror because it does not call `/api/v1/retrieve` directly.

### Answer

| Shape | Current fields |
|---|---|
| `AnswerRequest` | `query`, `top_k`, `ef_search` |
| `GroundedChunkResult` | `ChunkResult` + `context_id` |
| `AnswerResponse` | `query`, `answer`, `key_points`, `cautions`, `cited_articles`, `grounded_context_ids`, `retrieved_chunks`, `retrieval_total`, `model_name` |

### Document Draft

| Shape | Current fields / values |
|---|---|
| `DocumentDraftRequest` | `case_intake`, `legal_basis` |
| `DocumentDraftResponse` | `document_type`, `title`, `recipient`, `language`, `parties`, `facts`, `legal_basis`, `request`, `evidence_checklist`, `missing_fields`, `cautions`, `cited_articles`, `source_context_ids`, `missing_legal_basis`, `rendered_text` |
| `LegalBasisInput` | `answer_query`, `answer`, `key_points`, `cautions`, `cited_articles`, `source_context_ids`, `retrieved_chunks` |
| `CaseIntake` | `scenario_id`, `document_type`, `language`, `worker_info`, `employer_info`, `employment_info`, `dismissal_info`, `unpaid_wage_info`, `incident_timeline`, `claims`, `evidence_items`, `requested_actions`, `intake_notes` |
| `DocumentType` backend | `labor_office_wage_complaint`, `labor_commission_unfair_dismissal_brief`, `family_leave_reapplication`, `written_reason_request`, `certified_letter`, `workplace_change_reason_summary`, `consultation_case_summary` |
| `DocumentType` frontend | `labor_office_wage_complaint`, `labor_commission_unfair_dismissal_brief` |
| `DraftLanguage` | `ko`, `en`; frontend sends `ko` |
| `NoticeMethod` | `written`, `kakaotalk`, `sms`, `email`, `verbal`, `phone`, `unknown` |

### Nested Draft Shapes

| Shape | Key fields |
|---|---|
| `WorkerInfo` | `name_or_placeholder`, `nationality`, `preferred_language` |
| `EmployerInfo` | `company_name_or_placeholder`, `representative_name`, `workplace_address`, `employee_count`, `employee_count_over_5`, `workplace_jurisdiction` |
| `EmploymentInfo` | `start_date`, `last_work_date`, `job_title`, `wage_terms`, `wage_type`, `wage_payment_day`, `employment_contract_exists`, `continuous_service_over_1_year` |
| `DismissalInfo` | `dismissal_notice_date`, `dismissal_effective_date`, `notice_method`, `written_notice_received`, `dismissal_reason_provided`, `dismissal_reason`, `advance_notice_30_days`, `reinstatement_requested`, `monetary_compensation_requested`, `opportunity_to_explain`, `prior_disciplinary_action` |
| `UnpaidWageInfo` | `final_wage_paid`, `unpaid_wage_amount`, `unpaid_period_start`, `unpaid_period_end`, `severance_paid`, `unpaid_severance_amount`, `days_since_separation_over_14` |
| `EvidenceItem` | `type`, `description`, `status` |
| `TimelineEvent` | `date`, `event`, `evidence_refs` |
| `DraftPartySection` | `worker`, `employer`, `representative_name`, `workplace_address` |
| `DraftLegalBasisSection` | `citation_label`, `summary`, `source_context_ids` |

Backend `ScenarioId` enum includes `SCN-001`, `SCN-004`, `SCN-005`; current frontend `CaseIntake` type only sends `SCN-004`.

## 10. Storage / State Boundary

| Area | Current boundary |
|---|---|
| Frontend state | React Context + `useReducer` memory state only |
| Web Storage | raw `user_statement`, `answer_response`, `case_intake`, `draft_response` are not stored in Web Storage |
| Frontend persistence | no `localStorage`, `sessionStorage`, or IndexedDB usage found in `frontend/src` |
| Backend API persistence | retrieve/answer/draft do not store request/response payloads in a separate DB table |
| Backend DB | `law_chunks` table and `embedding` vectors exist |
| Draft output | frontend memory/render/copy/print centered |
| Logging | routers log `query_hash`, latency, params, counts, and failure reason; raw payload logging policy remains TODO |

TODO: local/server/access log policy for raw payloads should be reviewed before deployment. Current app-level retrieval/answer logs use query hashes, but this doc does not prove every runtime layer avoids raw request logging.

## 11. Privacy / Vertex Boundary

| Flow | Vertex boundary |
|---|---|
| `/api/v1/retrieve` | user `query` can be sent to Vertex query embedding (`gemini-embedding-001`) |
| `/api/v1/answer` modified/free input | user `query` can be sent to Vertex query embedding and Gemini answer generation (`gemini-2.5-flash` by default) |
| `SCN-004-DEMO-FREEZE` exact preset | fixed fixture; `/api/v1/answer` not called; Vertex not used |
| `SCN-001-BRIDGE-DEMO` exact preset | fixed fixture; answer-only; Vertex not used |
| `/after/intake` -> `/api/v1/documents/draft` | draft request may contain case facts, but draft endpoint itself does not call Vertex |

**After draft path does not call Vertex AI.** z_before_begin Before/Begin과 달리 After draft는 deterministic backend layer다. 단, draft의 `legal_basis`는 이전 `/api/v1/answer` 결과에 의존할 수 있으므로, modified/free input answer path에서 이미 Vertex를 사용했을 수 있다.

## 12. Error / Status Codes

코드에서 확인되는 status만 정리한다.

| Status | Endpoint | Meaning |
|---:|---|---|
| `200` | all three endpoints | success |
| `422` | `/api/v1/retrieve`, `/api/v1/answer` | blank query; `top_k` / `ef_search` constraints; request schema/extra field validation |
| `422` | `/api/v1/documents/draft` | Pydantic/FastAPI nested payload validation, including enum/schema/date/decimal validation, blank non-null text fields, and extra fields |
| `502` | `/api/v1/answer` | answer model returned invalid grounded response or failed grounding validation |
| `503` | `/api/v1/retrieve` | query embedding/provider/database unavailable |
| `503` | `/api/v1/answer` | answer generation/provider/database unavailable; current provider timeout also maps to 503 |
| `500` | `/api/v1/retrieve`, `/api/v1/answer` | unexpected internal error |

현재 코드 기준으로 provider timeout은 `504`가 아니라 `503`이다. 이 문서는 router 구현을 기준으로 한다.

## 13. Current Limitations / TODO

- TODO: local raw payload logging policy 점검 필요. app-level logs use query hashes, but access logs/proxy/runtime/provider logging policy is not fully specified here.
- TODO: `/api/v1/answer` model output drift 가능성 유지. `gemini-2.5-flash` output can change, and grounding validation mitigates but does not make answer wording fixed.
- TODO: fixed fixture와 live answer 결과 차이 가능성 유지. `SCN-004-DEMO-FREEZE` exact path is frozen fixture; modified/free input calls live model path.
- TODO: SCN-004 draft eligibility guard 유지 필요. `hasDraftGrounding()` alone is not enough; keep `getScn004DraftEligibility()` route and submit guards.
- TODO: integrated API는 팀원 Before/Begin and Bridge integration 후 확정한다.
- TODO: local/self-hosted LLM은 현재 After MVP API에 포함되지 않는다.
- TODO: public `AnswerRequest`에 `model_name`을 노출할지 여부는 backend/schema review 후에만 결정한다. 현재 public schema는 `model_name`을 받지 않는다.
- TODO: frontend direct `/api/v1/retrieve` client/type mirror가 필요하면 별도 contract review 후 추가한다.
