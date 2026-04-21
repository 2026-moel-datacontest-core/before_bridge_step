# Before/Begin API Spec

상태: current code-based draft  
기준: `z_before_begin/web` 현재 코드  
범위: 이 문서는 main backend의 `/api/v1/retrieve`, `/api/v1/answer`, `/api/v1/documents/draft`와 다른 별도 Before/Begin API surface를 문서화한다.

## 1. Scope

이 문서는 `z_before_begin/web/api-service`의 FastAPI 앱이 제공하는 API contract를 정리한다. 호출자는 같은 작업 디렉터리의 Vite React frontend(`z_before_begin/web/front`)이며, endpoint와 TypeScript 소비 shape는 `front/src/lib/endpoints.ts`, `front/src/lib/api-client.ts`, `front/src/types/review.ts`를 기준으로 확인한다.

Before/Begin contract review API의 현재 흐름은 다음과 같다.

1. 사용자가 계약서 이미지 또는 PDF를 업로드한다.
2. API가 업로드 파일을 검증하고 `test/runs/<timestamp>/` 아래에 저장한다.
3. OCR pipeline이 Vertex AI generative model을 호출해 `structured`, `raw_sections`, `_meta`를 생성한다.
4. 표준 계약 항목과 OCR 항목을 비교한다.
5. 임금, 근로시간, 휴게시간, 지급일 같은 수치 규칙을 local Python 로직으로 검증한다.
6. LLM content check가 `app.state.llm_client`를 통해 조항별 내용 위험을 검토한다. 기본 provider는 Vertex다.
7. deterministic explanation builder가 사용자 설명과 markdown을 생성한다.
8. 선택 확장 API로 장애 유형과 직무 특성 기반 권리/지원 추천 카드를 반환한다.

이 contract는 현재 main After/RAG API와 통합된 contract가 아니다. Before/Begin은 `z_before_begin/web` 내부의 병렬 API surface이며, After/RAG의 retrieval/answer/document draft contract와 섞어서 해석하지 않는다.

## 2. Runtime / Base URL

| 항목 | 현재 구현 기준 |
|---|---|
| Local API 기본값 | `http://127.0.0.1:8000` |
| Frontend env | `VITE_API_BASE_URL` |
| API service run command | `cd z_before_begin/web/api-service` 후 `PYTHONPATH=../domain uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |

`front/src/lib/endpoints.ts`의 base URL resolution:

| 조건 | `DEFAULT_API_BASE` |
|---|---|
| `VITE_API_BASE_URL` 존재 | trailing slash 제거 후 해당 값 사용 |
| `import.meta.env.DEV` | 빈 문자열 `""` |
| production/preview에서 browser hostname이 `localhost` 또는 `127.0.0.1` | `http://127.0.0.1:8000` |
| 그 외 | 빈 문자열 `""` |

`endpoints.review`는 `${DEFAULT_API_BASE}/api/v1/contract/review`, `endpoints.accessibility`는 `${DEFAULT_API_BASE}/api/v1/accessibility/recommendations`, `endpoints.health`는 `${DEFAULT_API_BASE}/health`로 만들어진다. Artifact URL은 `resolveArtifactUrl(path)`가 상대 경로를 `endpoints.artifactBase`와 결합한다.

## 3. Environment

| 환경변수 | 현재 코드 기준 의미 |
|---|---|
| `GCP_PROJECT_ID` | Vertex AI 초기화에 사용한다. 없으면 local service account JSON의 `project_id` fallback을 시도한다. |
| `GCP_LOCATION` | Vertex AI location. 기본값은 `us-central1`. |
| `GOOGLE_APPLICATION_CREDENTIALS` | Vertex AI SDK가 읽는 service account credential 경로. local fallback env 파일 기준 상대 경로도 절대 경로로 정규화한다. |
| `VERTEX_MODEL` | OCR 및 Vertex LLM client의 기본 model. 기본값은 `gemini-2.5-flash`. |
| `PHASE_A_VERTEX_MODEL` | `VERTEX_MODEL` fallback을 쓰는 Phase A용 model 값. API contract 자체 필드는 아니다. |
| `LLM_PROVIDER=vertex` | content check LLM provider 선택값. 기본값은 `vertex`. |
| `OLLAMA_BASE_URL` | `LLM_PROVIDER=ollama` 전환 시 Ollama endpoint. 기본값은 `http://localhost:11434`. |
| `OLLAMA_MODEL` | Ollama provider model. 기본값은 `qwen2.5:14b`. |

현재 기본 provider는 `vertex`이며, Before/Begin contract upload path currently uses Vertex AI for OCR and LLM-based content review. `OllamaClient`는 provider 교체 가능 구조로 구현되어 있지만 현재 기본 provider가 아니다.

로컬 개발에서는 `z_before_begin/web/.secrets/vertex-phase-a.env`를 fallback으로 읽을 수 있다. 문서나 로그에 secret 값을 남기지 않는다.

## 4. Endpoint Inventory

| Method | Path | Caller | Purpose | Request type | Response type | Vertex 사용 여부 | Storage / Artifact |
|---|---|---|---|---|---|---|---|
| `POST` | `/api/v1/contract/review/jobs` | `startReviewJob(files)` | 비동기 계약서 리뷰 job 생성 | `multipart/form-data` | `ReviewJob` | background pipeline에서 OCR + LLM content check 사용 | job state는 process memory, upload/result artifacts는 local `test/runs` |
| `GET` | `/api/v1/contract/review/jobs/{job_id}` | `getReviewJob(jobId)` | job 진행 상태 polling | path param | `ReviewJob` | 직접 호출 없음. 완료/실패 상태와 background 결과 조회 | job state는 process memory |
| `POST` | `/api/v1/contract/review` | `reviewContract(files)` | 동기 계약서 리뷰 | `multipart/form-data` | `ReviewResult` | OCR + LLM content check 사용 | upload/result artifacts는 local `test/runs` |
| `POST` | `/api/v1/accessibility/recommendations` | `getAccessibilityRecommendations(disabilityType, jobTraits)` | 장애 유형/직무 특성 기반 권리/지원 카드 추천 | `application/json` | `AccessibilityRecommendation` | 사용하지 않음 | local recommendation catalog 기반, artifact 없음 |
| `GET` | `/health` | health check client / operator | 서비스 상태 확인 | none | health object | 직접 호출 없음. loaded `llm_client` class name 노출 | artifact 없음 |

## 5. POST /api/v1/contract/review/jobs

목적: 비동기 계약서 리뷰 작업을 생성하고, 진행 상태 조회용 `job_id`를 반환한다.

| 항목 | 값 |
|---|---|
| Content-Type | `multipart/form-data` |
| Response | `ReviewJob` |
| Background task | `asyncio.create_task(_run_review_job(...))` |

### Request Fields

| Field | Type | Required | 설명 |
|---|---|---|---|
| `image` | 단일 `UploadFile` | optional | 단일 파일 업로드용 field |
| `images` | `list[UploadFile]` | optional | 여러 이미지 페이지 업로드용 field |

`front/src/lib/api-client.ts`의 `startReviewJob(files)` 동작:

| `files.length` | form field |
|---|---|
| `1` | `image`에 파일 1개 append |
| `2+` | 각 파일을 `images`에 append |

### Allowed Content Types

| `content_type` | 저장 suffix |
|---|---|
| `image/jpeg` | `.jpg` |
| `image/png` | `.png` |
| `application/pdf` | `.pdf` |

### Validation

| 조건 | Status | 현재 코드 기준 detail 성격 |
|---|---|---|
| 파일 없음 | `422` | 업로드된 파일 없음 |
| 빈 파일 | `422` | 빈 파일명 포함 가능 |
| 지원하지 않는 `content_type` | `422` | jpg/png/pdf만 허용 |
| PDF 여러 개 업로드 | `422` | PDF는 단일 파일만 가능 |
| PDF와 이미지 혼합 업로드 | `422` | 혼합 업로드 불가. 현재 검증 순서상 "PDF는 단일 파일" 메시지가 먼저 반환될 수 있음 |

### Response Shape

`create_review_job`는 `_create_review_job()` 후 `app.state.review_jobs[job_id]`에 저장하고 `_build_job_response(job)`를 반환한다.

| Field | Type | 설명 |
|---|---|---|
| `job_id` | string | UUID 문자열 |
| `status` | `queued` \| `running` \| `completed` \| `failed` | job lifecycle |
| `created_at` | string | UTC ISO timestamp |
| `updated_at` | string | UTC ISO timestamp |
| `run_directory` | string \| null | background task가 run dir 생성 후 `test/runs/<timestamp>` 형태로 채움 |
| `error` | string \| null | 실패 시 error message |
| `steps` | `ReviewJobStep[]` | progress step list |
| `result` | `ReviewResult` \| null | 완료 시 review result |

### Status Lifecycle

| Status | 의미 |
|---|---|
| `queued` | job 생성 직후, background task 실행 전 |
| `running` | 특정 progress step 실행 중 |
| `completed` | 모든 pipeline 완료, `result` 포함 가능 |
| `failed` | run directory 생성 이후의 일반 background pipeline 실패, `error` 포함 가능 |

### Progress Steps

| key | label | order |
|---|---|---|
| `file_validation` | `파일 확인` | 1 |
| `ocr` | `OCR 추출` | 2 |
| `section_compare` | `계약 항목 비교` | 3 |
| `rule_validation` | `수치 검증` | 4 |
| `explanation` | `설명 생성` | 5 |

각 step status는 `pending`, `running`, `completed`, `failed` 중 하나다. `message`는 단계별 한국어 설명 문자열 또는 `null`이다.

### Storage / Artifact

- job state는 `app.state.review_jobs` process memory에만 저장된다.
- 서버 재시작 시 job state persistence는 없다.
- background task는 run directory를 만들고 업로드 원본과 산출물을 `z_before_begin/web/test/runs/<timestamp>/` 아래 저장한다.
- create endpoint 자체는 job을 만든 뒤 즉시 response를 반환한다. run directory 생성 이후의 일반 OCR/review pipeline 실패는 HTTP 500이 아니라 이후 `GET /jobs/{job_id}`의 `status=failed`, `error`로 확인한다.
- 현재 `_run_review_job()`에서 `_create_run_dir()`와 `job["run_directory"]` 설정은 try 블록 밖에 있어, run directory 생성 같은 early setup failure가 polling response의 `failed` 상태로 항상 반영된다고 보장하기 어렵다.

## 6. GET /api/v1/contract/review/jobs/{job_id}

목적: 비동기 계약서 리뷰 job의 현재 진행 상태를 polling한다.

| 항목 | 값 |
|---|---|
| Path param | `job_id: string` |
| Response | create job과 같은 `ReviewJob` shape |
| Not found | `404`, detail: `리뷰 작업을 찾을 수 없습니다.` |

`front/src/App.tsx`는 `reviewJob.status`가 `completed` 또는 `failed`가 될 때까지 `getReviewJob(reviewJob.job_id)`를 호출한다. polling interval은 `1000ms`다.

| 상태 | Frontend 동작 |
|---|---|
| `completed` + `result` 존재 | `review` state에 result 저장 후 result screen으로 이동 |
| `failed` | `error`를 표시하고 home/upload 화면으로 복귀 |
| polling 실패 | 상태 조회 실패 message를 표시하고 home/upload 화면으로 복귀 |

## 7. POST /api/v1/contract/review

목적: 계약서 업로드 후 동일 request 안에서 동기 review를 수행하고 `ReviewResult`를 반환한다.

| 항목 | 값 |
|---|---|
| Content-Type | `multipart/form-data` |
| Request fields | async job API와 동일한 `image`, `images` |
| Validation | async job API와 동일 |
| Response | `ReviewResult` |

### Pipeline

`review_contract()`는 validation 후 `run_contract_review_pipeline(app, page_files)`를 호출한다.

1. `_collect_uploads`
2. `_validate_uploads`
3. 업로드 byte 읽기 및 빈 파일 검사
4. `_create_run_dir`
5. `_persist_uploaded_files`
6. `run_ocr`
7. `_build_section_result`
8. `_build_rule_result`
9. `_build_content_result`
10. `aggregate_results`
11. response에 `run_directory`, `uploaded_files` 추가
12. `_save_run_artifacts`

### Failure

| 실패 지점 | Status | detail |
|---|---|---|
| OCR 실패 | `500` | `OCR 실패: ...` |
| 리뷰 생성 실패 | `500` | `리뷰 생성 실패: ...` |

현재 동기 API도 `z_before_begin/web/test/runs/<timestamp>/`에 업로드 원본과 산출물을 저장한다. OCR 이후 리뷰 생성 실패 시 `ocr_output.json`과 `error.txt`를 남긴다.

## 8. POST /api/v1/accessibility/recommendations

목적: 장애 유형과 직무 특성 기반 권리/지원 카드 추천을 반환한다.

이 API는 contract upload/OCR/LLM review pipeline과 분리된 선택 확장 API다. Vertex OCR/LLM pipeline을 호출하지 않고, domain accessibility catalog와 recommendation rule을 사용한다.

| 항목 | 값 |
|---|---|
| Content-Type | `application/json` |
| Caller | `getAccessibilityRecommendations(disabilityType, jobTraits)` |
| Response | `AccessibilityRecommendation` |

### Request Body

| Field | Type | Required | 설명 |
|---|---|---|---|
| `disability_type` | string | yes | 지원할 장애 유형 key 또는 alias |
| `job_traits` | string[] | no, default `[]` | 직무 특성 tag 목록 |

현재 `front/src/App.tsx`의 `handleSelectDisability`는 `getAccessibilityRecommendations(disabilityType, [])`로 호출하므로, frontend에서는 `job_traits`가 빈 배열일 수 있다.

### Response

| Field | Type | 설명 |
|---|---|---|
| `disability_type` | string | normalize된 장애 유형 key |
| `disability_label` | string | 화면 표시 label |
| `overview` | string | 요약 설명 |
| `cards` | `AccessibilityCard[]` | 권리/지원/질문/법 카드 |
| `legal_basis` | string[] | card들의 `law_refs` dedupe 목록 |

`cards[]`:

| Field | Type | 설명 |
|---|---|---|
| `id` | string | card id |
| `kind` | `right` \| `support` \| `question` \| `law` | card 종류 |
| `title` | string | card 제목 |
| `description` | string | 설명 |
| `law_refs` | string[] | 법령 근거 label 목록 |
| `action_hint` | string \| null \| undefined | 선택적 행동 힌트. catalog 기반 card는 key가 존재하되 값이 `null`일 수 있다. |

### Failure

`build_accessibility_recommendation()`에서 지원하지 않는 장애 유형 등으로 `ValueError`가 발생하면 API는 `400`을 반환한다. JSON body 자체가 Pydantic validation에 실패하면 FastAPI 기본 `422`가 가능하다.

## 9. GET /health

목적: API service 상태를 확인한다.

Response:

| Field | Type | 설명 |
|---|---|---|
| `status` | string | 현재 코드에서는 `ok` |
| `standard_map_loaded` | boolean | `app.state.standard_map` 존재 여부 |
| `all_chunks_loaded` | boolean | `app.state.all_chunks` 존재 여부 |
| `llm_provider` | string \| null | `type(app.state.llm_client).__name__` 기준 class name. 예: `VertexAIClient`, `OllamaClient` |

## 10. Shared Response Shapes

이 섹션은 `front/src/types/review.ts`와 `api-service/app/api/app.py`에서 확인되는 필드를 중심으로 정리한다. 내부 nested dict는 일부 runtime dict 기반이므로, 정확히 고정되지 않은 세부 구조는 `object / map`으로 둔다.

### ReviewJob

| Field | Type | Source | 설명 |
|---|---|---|---|
| `job_id` | string | app.py / TS | UUID |
| `status` | `queued` \| `running` \| `completed` \| `failed` | app.py / TS | job 상태 |
| `created_at` | string | app.py / TS | UTC ISO timestamp |
| `updated_at` | string | app.py / TS | UTC ISO timestamp |
| `run_directory` | string \| null | app.py / TS | `test/runs/<timestamp>` 또는 null |
| `steps` | `ReviewJobStep[]` | app.py / TS | 진행 단계 |
| `error` | string \| null | app.py / TS | 실패 message |
| `result` | `ReviewResult` \| null | app.py / TS | 완료 결과 |

### ReviewJobStep

| Field | Type | 설명 |
|---|---|---|
| `key` | string | progress key |
| `label` | string | 한국어 label |
| `order` | number | 표시 순서 |
| `status` | `pending` \| `running` \| `completed` \| `failed` | step 상태 |
| `message` | string \| null | 단계별 message |

### ReviewResult

| Field | Type | Source | 설명 |
|---|---|---|---|
| `review_id` | string | app.py / TS | UUID |
| `reviewed_at` | string | app.py / TS | UTC ISO timestamp |
| `run_directory` | string | app.py / TS optional | `test/runs/<timestamp>` |
| `uploaded_files` | `UploadedFile[]` | app.py / TS optional | 저장된 업로드 원본 목록 |
| `contract_info` | object | app.py / TS | `type`, `employer`, `employee`, `start_date` |
| `scenario_tags` | string[] | app.py | 외국인/자체양식/기숙사 등 tag. TODO: TS type 반영 필요 |
| `ocr_snapshot` | object | app.py | 리뷰에 사용된 OCR 핵심 필드 snapshot |
| `ocr_conflicts` | object[] | app.py | structured와 raw parsing 결과 충돌 목록 |
| `ocr_warnings` | object[] / partially structured object[] | app.py / TS mismatch | OCR known issue/warning 목록. runtime response와 frontend TS type 사이 mismatch가 있으며, `corrected`는 runtime에서 항상 존재한다고 확정하지 않는다. |
| `overall_result` | `PASS` \| `WARNING` \| `VIOLATION` | app.py / TS | 통합 판정 |
| `overall_severity` | `NONE` \| `LOW` \| `MEDIUM` \| `HIGH` \| `CRITICAL` | app.py / TS | 통합 심각도 |
| `section_check` | object | app.py / TS | `missing`, `extra`, `mismatches` |
| `rule_check` | `Record<string, object>` | app.py / TS | `minimum_wage`, `working_hours`, `break_time`, `payment_day` 중심 |
| `content_check` | `Record<string, object>` | app.py | 조항 번호별 LLM content check result. TODO: TS type 반영 필요 |
| `risk_summary` | object / map | app.py | risk bucket별 요약. TODO: 세부 schema 확정 필요 |
| `summary` | string | app.py / TS | 한 줄 요약 |
| `user_explanation` | `UserExplanation` | app.py / TS | 사용자용 설명 |

`UploadedFile`:

| Field | Type | 설명 |
|---|---|---|
| `name` | string | 저장된 파일명. 예: `01_contract.jpg` |
| `path` | string | 서버 local filesystem path |
| `url` | string | `/artifacts/runs/<timestamp>/<filename>` 형태의 정적 URL |

`ocr_warnings[]` runtime item:

| Field | Type | 설명 |
|---|---|---|
| `field` | string | warning 대상 field |
| `structured` | unknown | structured extraction 값 |
| `corrected` | unknown \| optional | 근무시간 재계산 warning에는 존재할 수 있으나, 이름 불일치 warning 등에서는 없을 수 있다. |
| `raw` | unknown \| optional | 이름 불일치 warning 등에서 원문 기반 값으로 들어갈 수 있다. |
| `note` | string | warning 설명 |

### UserExplanation

| Field | Type | 설명 |
|---|---|---|
| `headline` | string | 상단 headline |
| `plain_language_summary` | string | 쉬운 요약 |
| `overall_assessment` | string[] | 전체 평가 bullet |
| `important_points` | object[] | 주요 쟁점. TS는 `title`, `status`, `severity`, `law_ref`, `description` 중심이지만 runtime builder output은 `issue_type`, `risk_bucket` 같은 extra fields를 포함할 수 있고, content point의 `law_ref`는 string \| null 또는 optional/nullable일 수 있다. |
| `recommended_actions` | string[] | 권장 조치 |
| `evidence` | object[] | 근거 발췌. TS는 `title`, `excerpt` |
| `markdown` | string | 사용자 설명 markdown |

### AccessibilityRecommendation

| Field | Type | 설명 |
|---|---|---|
| `disability_type` | string | normalize된 장애 유형 |
| `disability_label` | string | label |
| `overview` | string | 요약 |
| `cards` | `AccessibilityCard[]` | 추천 카드 |
| `legal_basis` | string[] | 법령 근거 dedupe 목록 |

## 11. Artifact / Static Serving

`TEST_RUNS_DIR`는 `z_before_begin/web/test/runs`다. FastAPI 앱은 다음 코드로 artifact static route를 mount한다.

```python
app.mount("/artifacts", StaticFiles(directory=str(TEST_RUNS_DIR.parent)), name="artifacts")
```

즉 `/artifacts` mount scope는 `TEST_RUNS_DIR.parent`, 다시 말해 `z_before_begin/web/test` 전체다. 일반 run output은 `z_before_begin/web/test/runs/<timestamp>/` 아래 저장된다.

저장되는 파일:

| 파일 | 생성 조건 |
|---|---|
| 업로드 원본 | validation 후 persist 단계 |
| `ocr_output.json` | OCR 성공 후 또는 리뷰 생성 실패 시 |
| `review_result.json` | review response 생성 성공 시 |
| `user_explanation.md` | `response.user_explanation.markdown` 존재 시 |
| `error.txt` | OCR 실패 또는 리뷰 생성 실패, async job failure |

Artifact URL은 `_build_artifact_url(path)`에서 `path.relative_to(TEST_RUNS_DIR.parent)`를 사용하므로 run output은 `/artifacts/runs/<timestamp>/<filename>` 형태가 된다.

계약서 원본과 OCR/review artifacts에는 개인정보, 사업장 정보, 임금 정보, 주소, 연락처 등이 포함될 수 있다. 배포 전에는 access control, retention, masking, storage policy가 필요하다.

## 12. Pipeline Detail

API contract 관점에서 contract review pipeline은 다음 함수 경계로 나뉜다.

| 단계 | 함수 | API contract 관점 |
|---|---|---|
| 업로드 정규화 | `_collect_uploads` | `image`, `images`를 `UploadFile[]`로 합친다. |
| 업로드 검증 | `_validate_uploads` | 파일 존재, content type, PDF 조합을 검증하고 suffix를 결정한다. |
| 업로드 저장 | `_persist_uploaded_files` | local run dir에 원본을 저장하고 `name`, `path`, `url`을 만든다. |
| OCR | `run_ocr` | 단일 파일이면 `_run_ocr_pipeline`, 여러 파일이면 `_run_ocr_pipeline_pages`를 호출한다. |
| 섹션 비교 | `_build_section_result` | `compare_sections(output, standard_map)`를 thread로 실행한다. |
| 수치 검증 | `_build_rule_result` | `validate_all(output, role_mapping, min_wage)`를 thread로 실행한다. |
| 내용 검토 | `_build_content_result` | extra law map 구성 후 `check_all_sections(..., llm_client, ...)`를 호출한다. |
| 결과 통합 | `aggregate_results` | `ReviewResult` core fields와 `user_explanation`을 만든다. |
| 산출물 저장 | `_save_run_artifacts` | `ocr_output.json`, `review_result.json`, `user_explanation.md`를 저장한다. |

### Vertex Boundary

- OCR pipeline은 `domain.contract_analysis.ocr_pipeline`의 Vertex AI generative model을 사용한다. 문서에서는 이를 Vertex AI OCR boundary로 취급한다.
- OCR은 image/pdf bytes를 Vertex AI `Part`로 전달하고, Layer 1 structured extraction과 Layer 2 raw section extraction을 수행한다.
- content check는 `app.state.llm_client`를 사용한다. 기본 `LLM_PROVIDER=vertex`에서는 `VertexAIClient`가 Vertex AI generative model을 호출한다.
- `LLM_PROVIDER=ollama`로 교체 가능한 구조는 있으나 현재 기본값은 아니다.
- section compare, rule validation, explanation builder, accessibility recommendation은 deterministic/local asset 기반 성격이 강하다.
- 다만 전체 contract review path는 OCR 및 content check 단계에서 Vertex를 사용하므로, "Before/Begin 업로드 경로가 Vertex로 가지 않는다"고 말하면 안 된다.

## 13. Error / Status Codes

현재 코드 기준으로 확인되는 status code:

| Status | Endpoint | 조건 |
|---|---|---|
| `200` | all success endpoints | FastAPI default success / `JSONResponse` |
| `400` | `POST /api/v1/accessibility/recommendations` | recommendation engine `ValueError` |
| `404` | `GET /api/v1/contract/review/jobs/{job_id}` | `job_id` 없음 |
| `422` | contract review upload endpoints | 파일 없음, 빈 파일, unsupported content type, PDF 조합 오류 |
| `422` | JSON body endpoints | FastAPI/Pydantic 기본 validation 가능 |
| `500` | `POST /api/v1/contract/review` | OCR 실패 |
| `500` | `POST /api/v1/contract/review` | 리뷰 생성 실패 |

비동기 job의 일반 OCR/review background pipeline 실패는 create endpoint의 HTTP status로 드러나지 않는다. run directory 생성 이후 발생한 pipeline failure는 이후 polling response가 `status=failed`, `error=<message>`를 담는다. 다만 `_run_review_job()`의 early setup failure는 현재 code path상 `failed` response 보장이 약하다.

## 14. Privacy / Security Boundary

계약서 업로드에는 개인정보/사업장 정보가 포함될 수 있다. 예: 근로자 성명, 사업주 상호, 주소, 연락처, 임금, 근무시간, 기숙사/숙소 정보, 외국인등록/여권 관련 문구 등이 OCR 입력과 local artifact에 들어갈 수 있다.

현재 Before/Begin contract upload path uses Vertex AI for OCR and LLM-based content review. 따라서 프로젝트 전체를 두고 "개인정보가 Vertex로 가지 않는다"고 설명하면 안 된다. 이 boundary는 main After deterministic document draft boundary와 분리해서 설명해야 한다.

현재 local artifact storage에는 민감정보가 남을 수 있다. 배포 전 필요한 정책:

| 영역 | 필요 정책 |
|---|---|
| Artifact access control | `/artifacts` URL 접근 제어, operator 접근 범위 |
| Retention | run artifact 보관 기간, 삭제 workflow |
| Request/body logging | multipart body, OCR text, review result logging 제한 |
| Provider disclosure | Vertex OCR/LLM provider 사용 고지 |
| Secrets management | service account key 파일 대신 managed secret/IAM 사용 |
| Cloud Storage / DB 전환 | IAM, TTL, bucket/object policy, audit logging |
| Masking | filename, OCR text, review JSON의 개인정보 masking 기준 |

## 15. Current Limitations / TODO

현재 구현 기준 limitation:

- job state is in-memory only: `app.state.review_jobs`는 process memory에만 존재한다.
- artifact storage is local `z_before_begin/web/test/runs`.
- `/artifacts` mount scope가 `z_before_begin/web/test` 전체라 배포 전 접근 범위를 재설계해야 한다.
- request/response schema는 runtime dict 기반 부분이 있어 추가 Pydantic schema 정리가 필요하다.
- `ReviewResult`의 `scenario_tags`, `ocr_snapshot`, `ocr_conflicts`, `content_check`, `risk_summary`는 `app.py` response에 있으나 현재 `front/src/types/review.ts`의 명시 interface는 일부 narrower하다. TODO: frontend/backend schema 정합성 정리.
- `ocr_warnings`는 runtime response와 frontend type 사이 mismatch가 있다. TODO: frontend type에서 corrected optional 처리 또는 backend warning shape 정규화 필요.
- `UserExplanation.important_points`는 runtime builder output이 `issue_type`, `risk_bucket`, nullable `law_ref`를 포함할 수 있으나 frontend type은 더 좁다. TODO: frontend UserExplanation type과 builder output 정합성 확인 필요.
- `AccessibilityRecommendation.action_hint`는 runtime에서 optional/nullable일 수 있으므로 frontend type/API schema alignment를 유지해야 한다.
- `_run_review_job()`의 run directory 생성 등 early setup failure는 현재 polling에서 `failed`로 관찰된다고 보장하기 어렵다. TODO: _run_review_job early setup failure handling 보강 필요.
- detailed integrated API는 팀원 통합 후 확정해야 한다.
- Before/Begin API가 참조하는 `law_chunks`/법령 asset과 main After backend corpus의 동기화 여부는 팀 통합 후 확인해야 한다.
- accessibility `job_traits`는 현재 frontend에서 빈 배열로 호출될 수 있다.
- Ollama provider는 교체 가능 구조지만 현재 기본 provider가 아니다.
- PDF page split, file size limit, concurrency limit, artifact cleanup policy는 현재 API contract로 명시된 별도 구현을 확인하지 못했다. TODO: 배포 전 별도 schema/ops 정책으로 확정.
