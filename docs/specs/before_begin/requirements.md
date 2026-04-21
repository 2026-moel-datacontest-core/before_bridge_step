# Before/Begin Requirements

상태: current code-based requirements  
기준: `z_before_begin/web` 현재 코드, `docs/specs/before_begin/api_spec.md`, `docs/specs/before_begin/data_model.md`  
범위: main After/RAG 앱과 분리된 teammate Before/Begin surface

## 1. 문서 목적

이 문서는 Before/Begin 계약서 업로드 및 사전 검토 기능의 요구정의서다. 사용자가 근로계약서 또는 관련 계약 문서를 업로드하면, 현재 MVP는 OCR, 계약 항목 점검, 규칙 검증, LLM 기반 내용 검토, 쉬운 설명, 접근성 추천을 통해 서명 전 또는 근무 시작 전 위험을 이해하도록 돕는다.

이 문서는 main `frontend/` + `backend/`의 After/RAG 앱 요구정의서가 아니다. 현재 구현 기준은 팀원이 별도 surface로 만든 `z_before_begin/web`이며, `/api/v1/retrieve`, `/api/v1/answer`, `/api/v1/documents/draft`와 계약을 섞어서 해석하지 않는다.

팀 통합 전에는 이 문서를 `z_before_begin/web` 기준 Before/Begin 요구정의서로 유지한다. integrated 요구정의서는 Before/Begin, Bridge, After 코드와 payload contract가 실제 merge된 뒤 `docs/specs/integrated/`에서 별도로 확정한다.

## 2. 제품/사용자 배경

Before/Begin의 사용자는 근로계약서, 표준근로계약서, 자체 양식 계약서, 특약이 포함된 계약 문서를 업로드해 위험 조항, 누락 조항, 설명이 필요한 항목을 빠르게 확인하려는 사람이다. UI는 한국어 중심이며, 법률 용어를 그대로 노출하기보다 사용자가 이해할 수 있는 쉬운 설명과 권장 조치를 함께 제공해야 한다.

중요 사용자 맥락:

- 외국인 근로자: 표준근로계약서 사용 여부, 비자/국적/여권/외국인등록증 신호, 사업장 변경 제한, 기숙사/숙소 공제와 서면 고지 누락을 중점적으로 고려한다.
- 미성년자/청소년 및 아르바이트 사용자: 계약기간, 수습, 최저임금, 근로시간, 휴게, 휴일, 지급일을 쉽게 확인할 수 있어야 한다.
- 장애인 근로자: 계약서 자체의 위법성뿐 아니라 정당한 편의제공, 근로지원인, 보조공학기기, 지원 제도 안내처럼 정보 사각지대를 줄이는 추천을 제공한다.
- 일반 근로자: 임금, 근로시간, 휴게, 휴일, 계약기간, 필수 기재사항 누락, 비표준 특약을 사전에 확인한다.

단, Before/Begin은 최종 법률 자문이나 소송 전략 수립 도구가 아니다. 현재 MVP는 검토/설명 보조 도구이며, 실제 분쟁 대응이나 최종 판단은 전문가 상담, 공공기관 안내, 최신 법령 확인과 함께 이뤄져야 한다.

## 3. 현재 MVP 범위

현재 MVP는 `z_before_begin/web`의 FastAPI API service와 Vite React frontend를 기준으로 다음 기능을 제공한다.

- 계약서 이미지/PDF 업로드: `jpg`, `png`, `pdf` 파일을 multipart로 전송한다. PDF는 단일 파일, 이미지는 다중 페이지 업로드를 허용한다.
- 비동기 review job 생성과 polling: `POST /api/v1/contract/review/jobs`로 job을 만들고 `GET /api/v1/contract/review/jobs/{job_id}`를 1초 간격으로 조회한다.
- 동기 review endpoint: `POST /api/v1/contract/review`도 존재하며 같은 pipeline으로 즉시 `ReviewResult`를 반환한다.
- OCR 결과 기반 계약서 구조화: Vertex AI OCR 경로를 통해 `structured`, `raw_sections`, `_meta`를 생성한다.
- 필수 항목/섹션 점검: `standard_map.json`의 계약 유형별 표준 항목과 OCR section을 비교한다.
- rule check: 최저임금, 근로시간, 휴게시간, 임금 지급일 등 수치/명시 규칙을 local Python 로직으로 검증한다.
- content check: 표준 항목과 비표준/extra 항목의 법적 위험을 LLM client로 검토한다. 현재 기본 provider는 Vertex-backed LLM이다.
- risk summary: 외국인, 기숙사, 여권 보관, 이직 제한, 필수 근로조건 누락 같은 위험을 bucket별로 요약한다.
- OCR warnings: structured OCR 값과 raw parsing/rule 결과의 충돌 또는 주의가 필요한 field를 표시한다.
- 사용자 설명문 `user_explanation.md` 생성: 결과를 headline, 쉬운 요약, issue card, 권장 조치, 근거 발췌, markdown으로 정리한다.
- 접근성 추천 endpoint: 장애 유형과 선택적 직무 특성 기반 권리/지원 카드와 법령 근거를 반환한다.
- 결과 artifact 저장: 업로드 원본, `ocr_output.json`, `review_result.json`, `user_explanation.md`를 local run directory에 저장한다. run directory 생성 이후 OCR/review/explanation pipeline failure에서는 가능한 경우 `error.txt`가 남는다.
- artifact static serving: `/artifacts` route로 local test artifact를 제공한다.
- health check: `/health`에서 core asset과 LLM client loading 상태를 확인한다.

## 4. 제외 범위 / Non-goals

Before/Begin 요구정의서의 제외 범위는 다음과 같다.

- main After RAG 답변 생성, 검색, 법률 문서 초안 생성은 이 문서 범위가 아니다.
- `frontend/`의 `/after`, `/after/result`, `/after/intake`, `/after/draft` flow 요구사항은 이 문서에서 정의하지 않는다.
- Bridge 저장/전달 contract와 Before -> Bridge -> After 통합 flow는 아직 확정하지 않는다.
- DB 영속화는 현재 범위가 아니다. review job state는 `app.state.review_jobs` in-memory에만 있다.
- 사용자 계정, 권한, 인증, 세션 기반 접근 제어는 현재 구현 범위가 아니다.
- artifact TTL, access control, deletion workflow는 현재 구현되어 있지 않으며 배포 전 별도 요구사항으로 확정해야 한다.
- 완전한 법률 자문, 소송 문서 자동 작성, 대리 제출, 승소 가능성 판단은 목표가 아니다.
- Ollama provider는 교체 가능 구조일 뿐 현재 기본 경로가 아니다.
- self-hosted LLM 또는 GCP GPU 기반 로컬 추론은 현재 Before/Begin MVP 요구사항이 아니다.
- PDF page split, 대용량 파일 처리, 동시성 제한, production storage migration은 현재 MVP 필수 구현으로 보지 않는다.

## 5. 사용자 플로우

기본 사용자 플로우:

1. 사용자는 홈/업로드 화면에서 계약서 이미지 또는 PDF를 선택한다.
2. 프론트엔드는 파일 개수에 따라 `image` 또는 `images` multipart field를 구성한다.
3. 사용자가 분석 시작을 누르면 비동기 review job 생성 endpoint를 호출한다.
4. API는 validation 후 `job_id`, `status`, `steps`를 반환한다.
5. 프론트엔드는 `job_id`로 polling하여 `queued`, `running`, `completed`, `failed` 상태와 단계별 progress를 표시한다.
6. 완료 시 `ReviewResult`를 결과 화면에 표시하고, 사용자 설명과 issue card, 권장 조치, 근거 발췌, OCR warnings, 업로드 원본 preview를 보여준다.
7. 실패 시 `error` message를 표시하고 업로드 화면으로 돌아간다.
8. 사용자는 결과 화면의 보조 패널에서 장애 유형을 선택할 수 있다.
9. 프론트엔드는 accessibility recommendation endpoint를 호출하고, 실패 시 local fallback card를 표시한다.
10. 사용자는 결과 화면에서 `uploaded_files` 기반 업로드 원본 preview를 확인할 수 있다. JSON/MD 산출물은 backend local artifact로 저장되고 `/artifacts` scope에서 serving 가능하지만, 현재 UI direct link는 TODO다.

Mermaid flow:

```mermaid
flowchart TD
  A[사용자 파일 선택: jpg/png/pdf] --> B[POST /api/v1/contract/review/jobs]
  B --> C{파일 validation}
  C -- 실패 --> X[422 error 표시]
  C -- 성공 --> D[job_id 수신]
  D --> E[GET /api/v1/contract/review/jobs/{job_id} polling]
  E --> F[TEST_RUNS_DIR/<timestamp> 생성]
  F --> G[업로드 원본 저장]
  G --> H[Vertex OCR]
  H --> I[section check / rule check]
  I --> J[Vertex-backed LLM content check]
  J --> K[risk summary + user explanation]
  K --> L[review_result.json + user_explanation.md 저장]
  L --> M[completed ReviewResult 표시]
  E -- failed --> Y[error 표시 및 재시도]
  M --> N[accessibility 유형 선택]
  N --> O[POST /api/v1/accessibility/recommendations]
  O --> P[권리/지원 카드 표시]
```

`TEST_RUNS_DIR`는 `z_before_begin/web/test/runs`이며, 일반 실행 산출물은 `TEST_RUNS_DIR/<timestamp>` 또는 `test/runs/<timestamp>` 아래 저장된다. `/artifacts` static route는 `TEST_RUNS_DIR.parent`, 즉 `z_before_begin/web/test`에서 mount된다.

## 6. 기능 요구사항

| Requirement ID | 항목 | 설명 | 현재 구현 상태 | 주요 API/데이터 | 비고/TODO |
|---|---|---|---|---|---|
| `BB-FR-001` | 계약서 업로드 입력 | 사용자는 계약서 이미지 여러 장 또는 PDF 한 장을 선택해 분석 요청을 보낼 수 있어야 한다. | 구현됨 | `UploadPanel`, `startReviewJob(files)`, multipart `image`/`images` | frontend accept는 `.jpg,.jpeg,.png,.pdf`; backend는 content type 기준으로 검증한다. |
| `BB-FR-002` | 파일 validation | 파일 없음, 빈 파일, 미지원 content type, PDF 다중 업로드, PDF+이미지 혼합 업로드를 거부해야 한다. | 구현됨 | `_collect_uploads()`, `_validate_uploads()`, `422` | 파일 크기 제한, 페이지 수 제한, 악성 파일 검사 정책은 미정이다. |
| `BB-FR-003` | async review job | 업로드 후 즉시 `job_id`를 반환하고, background task가 단계별 상태와 최종 결과를 갱신해야 한다. | 구현됨, 제한 있음 | `POST /api/v1/contract/review/jobs`, `GET /api/v1/contract/review/jobs/{job_id}`, `ReviewJob`, `app.state.review_jobs` | process restart 시 job state loss. `_create_run_dir()` early setup failure handling 보강 필요. |
| `BB-FR-004` | sync review | 동일 pipeline을 한 request 안에서 수행하고 `ReviewResult`를 반환하는 동기 endpoint를 제공한다. | 구현됨 | `POST /api/v1/contract/review`, `run_contract_review_pipeline()` | 프론트 기본 flow는 async job을 사용한다. |
| `BB-FR-005` | OCR | 업로드 파일을 OCR하여 `structured`, `raw_sections`, `_meta`를 생성해야 한다. | 구현됨 | `run_ocr()`, `ocr_pipeline.py`, `ocr_output.json` | Current path uses Vertex AI OCR. OCR 결과에는 개인정보와 계약 민감정보가 포함될 수 있다. |
| `BB-FR-006` | section check | OCR section과 표준 계약 항목을 비교해 missing, extra, mismatches를 생성해야 한다. | 구현됨 | `compare_sections()`, `standard_map.json`, `section_check` | `role_mapping`은 internal 계산에 쓰이고 response에는 직접 노출하지 않는다. |
| `BB-FR-007` | rule check | 임금, 근로시간, 휴게시간, 지급일 등 수치/명시 규칙을 local logic으로 검증해야 한다. | 구현됨 | `validate_all()`, `minimum_wage.yaml`, `rule_check` | 숫자 계산은 LLM에 위임하지 않는다. 연도별 정책과 source sync는 후속 확인 필요. |
| `BB-FR-008` | content check | 표준 항목과 extra 항목의 위험 문구, 비표준 조항, 외국인/기숙사/권리 제한 위험을 LLM으로 검토해야 한다. | 구현됨 | `check_all_sections()`, `app.state.llm_client`, `law_chunks/all_chunks.json`, `content_check` | 기본 provider는 Vertex-backed LLM. nested dict schema는 Pydantic/TS alignment 필요. |
| `BB-FR-009` | risk summary | 핵심 위험을 `immediate_illegal`, `mandatory_missing`, `deduction_risk`, `enforceability_risk` 등 bucket으로 요약해야 한다. | 구현됨 | `_build_risk_summary()`, `risk_summary`, `scenario_tags` | frontend TS type에 일부 명시되지 않은 runtime field가 있다. |
| `BB-FR-010` | OCR warnings | structured OCR 값과 raw parsing/rule result가 충돌하면 사용자에게 확인 필요 warning을 보여야 한다. | 구현됨, type mismatch 있음 | `build_ocr_warnings()`, `ReviewResult.ocr_warnings`, `ResultPanel` | `ocr_warnings.corrected`는 optional일 수 있으나 TS type은 required다. |
| `BB-FR-011` | user explanation | 결과를 법률가가 아닌 사용자도 이해할 수 있게 headline, 쉬운 요약, 이슈, 권장 조치, 근거, markdown으로 생성해야 한다. | 구현됨 | `build_user_explanation()`, `user_explanation`, `user_explanation.md` | `important_points.law_ref` nullable/optional 및 `issue_type`/`risk_bucket` extra field 정합성 필요. |
| `BB-FR-012` | artifact storage | 업로드 원본과 OCR/review/explanation 산출물을 local run directory에 저장해야 한다. run directory 생성 이후 pipeline failure에서는 가능한 경우 `error.txt`를 남긴다. | 구현됨 | `TEST_RUNS_DIR`, `ocr_output.json`, `review_result.json`, `user_explanation.md`, `error.txt` | validation failure나 `_create_run_dir()` early setup failure에서는 `error.txt`가 없을 수 있다. local `test/runs` 저장은 demo/dev 기준이다. production retention/삭제 정책 필요. |
| `BB-FR-013` | artifact static serving | backend는 local artifact를 제공하는 `/artifacts` route를 제공한다. 현재 결과 화면은 `uploaded_files` 기반 업로드 원본 preview만 surface한다. | 구현됨, UI 제한 있음 | `app.mount("/artifacts", StaticFiles(directory=str(TEST_RUNS_DIR.parent)))`, `resolveArtifactUrl()` | JSON/MD 산출물은 backend local artifact로 저장되고 `/artifacts` scope에서 serving 가능하지만, UI direct link는 TODO다. `/artifacts` access control/TTL 없음. mount scope가 `z_before_begin/web/test` 전체다. |
| `BB-FR-014` | accessibility recommendations | 장애 유형과 선택적 직무 특성에 따라 권리/지원/질문/법 카드와 legal basis를 추천해야 한다. | 구현됨 | `POST /api/v1/accessibility/recommendations`, `build_accessibility_recommendation()`, accessibility YAML catalog | Vertex를 호출하지 않는 local catalog/rule 기반 path. `action_hint` nullable/optional alignment 필요. |
| `BB-FR-015` | health check | service가 핵심 asset과 LLM client를 로드했는지 확인할 수 있어야 한다. | 구현됨 | `GET /health`, `standard_map_loaded`, `all_chunks_loaded`, `llm_provider` | health는 인증 없이 노출되는 상태 endpoint이므로 production 노출 범위 검토 필요. |

## 7. 비기능 요구사항

| Requirement ID | 영역 | 요구사항 | 현재 기준 / 배포 전 조치 |
|---|---|---|---|
| `BB-NFR-001` | 개인정보/민감정보 보호 | 업로드 계약서와 OCR/review 산출물은 personal, workplace, wage, visa, dormitory, contract-sensitive information을 포함할 수 있으므로 최소 수집, 최소 노출, 보관 제한이 필요하다. | 현재 local artifact에 원본과 전체 JSON이 저장된다. production 전 privacy notice, consent, masking, logging 제한, 삭제 workflow가 필요하다. |
| `BB-NFR-002` | Vertex AI 사용 경계 | Before/Begin review path는 기본적으로 Vertex AI OCR과 Vertex-backed LLM content review를 사용한다. | 이 문서는 프로젝트 전체 개인정보가 Vertex AI를 피한다고 주장하면 안 된다. After deterministic draft boundary와 분리 설명해야 한다. |
| `BB-NFR-003` | artifact 보관/노출 경계 | artifact는 `z_before_begin/web/test/runs/<timestamp>`에 저장되고 `/artifacts`에서 제공된다. | `/artifacts`는 `TEST_RUNS_DIR.parent`인 `z_before_begin/web/test`를 mount한다. access control, TTL, retention, URL 보호가 필요하다. |
| `BB-NFR-004` | 응답 시간/비동기 처리 | OCR/LLM review는 시간이 걸릴 수 있으므로 기본 UI flow는 async job과 polling으로 진행 상태를 제공해야 한다. | polling interval은 frontend 기준 1000ms. timeout, queue size, cancellation, concurrency limit은 미정이다. |
| `BB-NFR-005` | 장애 처리 | validation 실패는 명확한 422 error, accessibility domain error는 400, unknown job은 404, sync pipeline 실패는 500 또는 async failed state로 표현해야 한다. | async early setup failure와 run directory 생성 실패는 현재 failed polling 보장이 약하므로 보강 필요하다. |
| `BB-NFR-006` | 재현성 | local demo에서는 같은 code/assets/env 기준으로 업로드 -> OCR -> review -> artifact 생성 흐름을 재현할 수 있어야 한다. | Vertex OCR/LLM 출력은 temperature 0.0이지만 외부 provider 의존성이 있으므로 완전 결정적이라고 주장하지 않는다. artifact timestamp는 run마다 달라진다. |
| `BB-NFR-007` | frontend/backend schema 정합성 | `ReviewResult`, `ReviewJob`, `AccessibilityRecommendation` runtime dict와 frontend TS type은 표시 화면에서 깨지지 않도록 정렬되어야 한다. | `content_check`, `risk_summary`, `scenario_tags`, `ocr_snapshot`, `ocr_conflicts`, `ocr_warnings.corrected`, `important_points.law_ref`, `accessibility.action_hint` 정합성 TODO가 있다. |
| `BB-NFR-008` | 운영 배포 전 보안 | 운영 배포 전 인증, 접근 제어, secret 관리, provider disclosure, request/body logging 금지, artifact cleanup, audit 정책이 필요하다. | 현재 MVP는 local/demo surface다. production-ready security posture로 간주하지 않는다. |

## 8. Privacy / Vertex / Artifact Boundary

Before/Begin privacy, Vertex, artifact 경계는 발표와 문서에서 아래처럼 설명해야 한다.

- Before/Begin upload/review path can include personal, workplace, wage, visa, dormitory, and contract-sensitive information. 즉 계약서 업로드 경로에는 성명, 주소, 연락처, 사업장, 임금, 근로시간, 비자/국적/여권/외국인등록증, 기숙사/숙소, 특약과 같은 개인정보 및 민감한 근로계약 정보가 포함될 수 있다.
- Current Before/Begin review path uses Vertex AI OCR and Vertex-backed LLM content review by default. 현재 Before/Begin review path는 기본적으로 Vertex AI OCR과 Vertex-backed LLM content review를 사용한다.
- Therefore, this document must not claim that all project personal data avoids Vertex AI. 따라서 이 문서는 "프로젝트 전체의 개인정보가 Vertex AI로 가지 않는다"고 주장하면 안 된다.
- `/artifacts` is mounted from `TEST_RUNS_DIR.parent`, which is `z_before_begin/web/test`, while run outputs are stored under `z_before_begin/web/test/runs/<timestamp>`.
- Access control, retention, and request/body logging policy are required before production deployment.

구현 경계:

- OCR 단계는 image/pdf bytes를 Vertex AI `Part`로 전달한다.
- content check 단계는 `app.state.llm_client`를 사용하며 기본 `LLM_PROVIDER=vertex`에서는 Vertex AI generative model을 호출한다.
- section compare, rule validation, risk summary 일부, user explanation markdown, accessibility recommendation은 local asset/rule/deterministic 로직 성격이 강하다.
- Ollama provider는 `LLM_PROVIDER=ollama` 전환 구조로 존재하지만 현재 기본 path가 아니며, self-hosted LLM/GCP GPU는 현 Before/Begin MVP 요구사항이 아니다.
- artifact에는 업로드 원본, OCR text, review result, legal risk description, user explanation이 포함될 수 있으므로 local demo 외 배포에는 보호 장치가 필요하다.

## 9. API 요구사항 요약

상세 endpoint schema, request/response field, status code, validation detail은 `docs/specs/before_begin/api_spec.md`를 source of truth로 삼는다. 이 요구정의서는 endpoint의 목적과 제품 요구만 요약한다.

| Method | Path | 요구사항 요약 |
|---|---|---|
| `POST` | `/api/v1/contract/review/jobs` | 계약서 업로드를 받아 async review job을 생성하고 `ReviewJob`을 반환한다. |
| `GET` | `/api/v1/contract/review/jobs/{job_id}` | job 진행 상태, 단계별 progress, 실패 error, 완료 result를 polling으로 반환한다. |
| `POST` | `/api/v1/contract/review` | 계약서 업로드를 받아 동기 review pipeline을 수행하고 `ReviewResult`를 반환한다. |
| `POST` | `/api/v1/accessibility/recommendations` | 장애 유형과 직무 특성 기반 accessibility 권리/지원 카드를 반환한다. |
| `GET` | `/health` | API service의 asset loading과 LLM provider 상태를 확인한다. |

API 상세 schema는 `api_spec.md`로 위임한다. 요구사항 문서에서 response field를 새로 확정하거나 endpoint contract를 확장하지 않는다.

## 10. 데이터/저장 요구사항 요약

상세 field 정의, runtime dict shape, artifact layout, frontend TS alignment TODO는 `docs/specs/before_begin/data_model.md`를 source of truth로 삼는다.

핵심 데이터/저장 요구:

- async job state는 `app.state.review_jobs` in-memory dict에 저장된다.
- 서버 재시작 또는 process 교체 시 `review_jobs` 상태는 보존되지 않는다.
- run output directory는 `TEST_RUNS_DIR = z_before_begin/web/test/runs`이다.
- 성공 run은 업로드 원본, `ocr_output.json`, `review_result.json`, `user_explanation.md`를 생성한다.
- run directory 생성 이후 OCR/review/explanation pipeline failure에서는 가능한 경우 업로드 원본, `ocr_output.json`, `error.txt`를 남긴다.
- validation failure나 `_create_run_dir()` early setup failure에서는 run directory, `error.txt`, failed status polling response가 없을 수 있다.
- backend static URL은 보통 `/artifacts/runs/<timestamp>/<filename>` 형태다.
- frontend state는 React local state이며, 현재 inspected code 기준 raw 계약서 payload나 review payload를 Web Storage에 저장하지 않는다.
- runtime dict와 frontend TS type alignment는 아직 완전히 고정되지 않았다.

데이터 상세 필드와 artifact/data-flow diagram은 `data_model.md`로 위임한다.

## 11. 현재 알려진 제약/TODO

- `app.state.review_jobs` is in-memory라 process restart 시 job state loss가 발생한다.
- artifact storage는 local `z_before_begin/web/test/runs` 기준이며 production storage가 아니다.
- `/artifacts` access control/TTL이 없다.
- `/artifacts` mount scope가 `TEST_RUNS_DIR.parent`, 즉 `z_before_begin/web/test` 전체라 production boundary 재검토가 필요하다.
- `ReviewResult` runtime shape와 frontend TS type mismatch 가능성이 있다.
- `scenario_tags`, `ocr_snapshot`, `ocr_conflicts`, `content_check`, `risk_summary`는 runtime response에 있으나 현재 frontend TS `ReviewResult` 명시 interface는 일부 narrower하다.
- `ocr_warnings.corrected` optional mismatch가 있다. runtime warning은 `raw`만 있고 `corrected`가 없을 수 있다.
- `UserExplanation.important_points`의 `law_ref`는 nullable/optional일 수 있고, `issue_type`, `risk_bucket` extra field가 포함될 수 있다.
- `_create_run_dir()` early setup failure handling이 약하다. async job에서 run directory 생성이 try block 밖에 있어 polling response의 `failed` 보장이 약하다.
- accessibility `action_hint` nullable/optional alignment가 필요하다.
- Before/Begin `law_chunks` asset과 main backend corpus sync 확인이 필요하다.
- `contract_info.start_date`는 현재 `structured.start_date` 중심이며 fixed-term/foreign `contract_start_date` fallback policy 확인이 필요하다.
- file size limit, page count limit, concurrency limit, timeout, cancellation, artifact cleanup policy가 명시적으로 고정되어 있지 않다.
- request/body logging policy가 없다. multipart body, OCR text, review JSON, prompt text logging 제한 정책이 필요하다.
- Vertex provider disclosure와 사용자 동의/고지가 production 전 필요하다.
- integrated docs는 팀 merge 후 재작성/확정한다.

## 12. Acceptance Criteria

demo/local 기준 Acceptance Criteria:

- [ ] 사용자는 `jpg`, `png`, `pdf` 계약서 파일을 선택하고 업로드 검토 job을 생성할 수 있다.
- [ ] `POST /api/v1/contract/review/jobs`는 `job_id`, `status`, `steps`를 포함한 `ReviewJob`을 반환한다.
- [ ] frontend는 `GET /api/v1/contract/review/jobs/{job_id}` polling으로 `completed` 또는 `failed`까지 상태를 확인할 수 있다.
- [ ] 완료된 job은 `ReviewResult`를 포함하고 결과 화면에 overall result, severity, contract info, issue cards, recommended actions, evidence를 표시한다.
- [ ] OCR 성공 시 `ocr_output.json` artifact가 생성된다.
- [ ] review 성공 시 `review_result.json` artifact가 생성된다.
- [ ] 사용자 설명 markdown이 존재하면 `user_explanation.md` artifact가 생성된다.
- [ ] run directory 생성 이후 pipeline failure에서는 가능한 범위에서 `error.txt`와 사용자에게 보여줄 error message가 남는다.
- [ ] validation failure나 `_create_run_dir()` early setup failure에서는 `error.txt`가 없을 수 있음을 문서와 발표에서 같은 caveat으로 설명한다.
- [ ] 결과 화면은 `uploaded_files` 기반 업로드 원본 preview를 표시한다.
- [ ] JSON/MD 산출물은 backend local artifact로 저장되고 `/artifacts/runs/<timestamp>/...` scope에서 serving 가능하지만, UI direct link는 TODO로 남아 있다.
- [ ] `POST /api/v1/accessibility/recommendations`는 지원하는 장애 유형에 대해 `AccessibilityRecommendation` response를 반환한다.
- [ ] `GET /health`는 핵심 asset loading과 LLM provider 상태를 확인할 수 있다.
- [ ] 개인정보/Vertex/artifact boundary가 발표와 문서에서 과장 없이 설명된다.
- [ ] main After 앱의 RAG answer/document draft 기능과 Before/Begin upload/review 범위가 혼동되지 않는다.
- [ ] Ollama/self-hosted LLM은 기본 구현 경로가 아니라 교체 가능 구조 또는 후속 후보로만 설명된다.
- [ ] integrated 요구정의서는 팀 merge 이후 별도 확정 대상으로 남아 있다.
