# Before/Begin Screen Plan

Status: current code-based screen plan  
Basis: `z_before_begin/web/front` implementation, `requirements.md`, `api_spec.md`, `data_model.md`  
Scope: Before/Begin contract upload/review screen only

## 1. 문서 목적

이 문서는 Before/Begin 계약서 업로드 및 사전 검토 화면 기획서다. 사용자가 근로계약서 이미지 또는 PDF를 업로드하고, 비동기 review job 진행 상태를 확인한 뒤, 결과와 업로드 원본 preview 및 장애 특화 권리/지원 추천을 확인하는 화면 흐름을 정리한다.

작성 기준은 현재 `z_before_begin/web/front` Vite React frontend 구현이다. 이 문서는 새 UI 제안서가 아니며, 현재 코드가 제공하는 화면, state, API 호출, 표시 데이터, 미구현 TODO를 있는 그대로 구분한다.

main `frontend/`의 After/RAG 4-route flow와 integrated frontend는 이 문서 범위가 아니다. main After 화면 기획과 팀 merge 이후 통합 화면 기획은 별도 문서에서 다룬다.

## 2. 화면 범위 요약

현재 Before/Begin frontend surface는 route 기반 앱이 아니라 단일 React page에서 `screenState`로 전환되는 single-page state flow다.

| 항목 | 현재 구현 기준 |
|---|---|
| App entry | `z_before_begin/web/front/src/App.tsx` |
| Routing | React Router 없음. URL route 전환 없음. |
| Screen state | `home` / `loading` / `result` |
| 항상 표시되는 영역 | `Navbar`, `Hero`, upload section |
| 조건부 표시 영역 | `LoadingPanel`, `ResultPanel`, result 우측 `AccessibilityPanel` |
| Frontend persistence | React local state only. `localStorage`, `sessionStorage`, IndexedDB 저장 없음. |

사용자가 접근하는 주요 상태:

- 초기 상태: `screenState="home"`, `selectedFiles=[]`, `review=null`, `reviewJob=null`.
- 파일 선택 상태: `selectedFiles`에 `File[]`이 쌓이고 업로드 목록에 파일명/크기가 표시된다.
- 파일 미선택 오류: `분석 시작` 클릭 시 API 호출 없이 `requestError`를 표시한다.
- 업로드/job 생성 중: `handleAnalyze()`가 `screenState="loading"`으로 전환하고 `POST /api/v1/contract/review/jobs`를 호출한다.
- job 진행 중: `reviewJob.status`가 `queued` 또는 `running`이면 1초 간격 polling을 수행하고 `LoadingPanel`에 단계별 progress를 표시한다.
- 결과 상태: `completed` + `result` 수신 시 `screenState="result"`로 전환하고 `ResultPanel`과 `AccessibilityPanel`을 표시한다.
- 실패 상태: job 생성 실패, polling 실패, `job.status="failed"`는 `requestError`를 채우고 home/upload 화면으로 돌아간다.
- accessibility recommendation 상태: result 화면 우측 패널에서 장애 유형 선택 후 loading, success, API 실패 fallback 상태를 표시한다.

## 3. 사용자 플로우

기본 사용자 플로우:

1. 사용자는 hero 또는 navbar의 `계약서 분석 시작` 버튼으로 upload section에 스크롤한다.
2. 사용자는 upload drop area를 클릭해 `jpg`, `jpeg`, `png`, `pdf` 파일을 선택한다. 이미지는 여러 장 선택할 수 있고, PDF는 backend validation 기준 단일 파일만 허용된다.
3. `UploadPanel`은 선택 파일을 append하고, 목록에서 파일명/크기를 표시하며, 개별 파일 삭제를 허용한다.
4. 사용자가 `분석 시작`을 누르면 `App.tsx`가 파일 미선택 여부만 먼저 확인한다.
5. 파일이 있으면 `startReviewJob(selectedFiles)`가 `FormData`를 만든다. 파일 1개는 `image`, 2개 이상은 `images` field로 전송한다.
6. `POST /api/v1/contract/review/jobs`가 성공하면 `ReviewJob`이 `reviewJob` state에 저장된다.
7. `useEffect`가 `GET /api/v1/contract/review/jobs/{job_id}`를 즉시 1회 호출하고, 이후 1000ms 간격으로 polling한다.
8. `LoadingPanel`은 backend가 내려주는 `steps`의 `pending` / `running` / `completed` / `failed` 상태와 `message`를 표시한다.
9. job이 `completed`이고 `result`가 있으면 `review` state에 저장하고 result section으로 이동한다.
10. 결과 화면은 `ReviewResult`의 headline, plain summary, overall result/severity, contract info, issue cards, recommended actions, evidence, summary notes, OCR warnings, `uploaded_files` 기반 업로드 원본 preview를 표시한다.
11. 사용자는 result 우측 `AccessibilityPanel`에서 장애 유형을 선택할 수 있다.
12. `POST /api/v1/accessibility/recommendations`가 성공하면 추천 overview/card/law ref를 표시한다. 실패하면 local fallback card를 표시하고 fallback 안내 error message를 함께 보여준다.
13. 사용자는 `새 분석으로 돌아가기`로 `handleReset()`을 실행해 선택 파일, review, job, accessibility state, error를 모두 초기화할 수 있다.

Mock flow:

- `UploadPanel`의 `Bridge pattern: 외국인 사례`, `아르바이트 사례`, `장애인 사례` 버튼은 `/mock/review_result_sen0.json`, `/mock/review_result_sen1.json`, `/mock/review_result_sen2.json`을 fetch해 result 화면으로 이동한다.
- 이 mock fetch는 Before/Begin API contract가 아니라 frontend demo 편의 경로다.

```mermaid
flowchart TD
  A[Initial home state] --> B[파일 선택: jpg/png/pdf]
  B --> C{분석 시작}
  C -- 파일 없음 --> C1[home error: 먼저 분석할 파일을 업로드해 주세요]
  C -- 파일 있음 --> D[screenState=loading]
  D --> E[POST /api/v1/contract/review/jobs]
  E -- 생성 실패/422/network --> E1[home error 표시]
  E -- ReviewJob 수신 --> F[reviewJob 저장]
  F --> G[GET /api/v1/contract/review/jobs/{job_id} polling: 1000ms]
  G --> H{job status}
  H -- queued/running --> I[LoadingPanel step progress 표시]
  I --> G
  H -- failed --> J[home error 표시]
  H -- completed + result --> K[screenState=result]
  K --> L[ResultPanel: explanation, issue cards, evidence, OCR warnings]
  K --> M[uploaded_files 기반 업로드 원본 preview]
  K --> N[AccessibilityPanel 유형 선택]
  N --> O[POST /api/v1/accessibility/recommendations]
  O -- 성공 --> P[recommendation cards 표시]
  O -- 실패 --> Q[fallback cards + accessibility error 표시]
  K --> R[새 분석으로 돌아가기]
  R --> A
```

Storage/artifact path 표기:

- `TEST_RUNS_DIR`는 `z_before_begin/web/test/runs`다.
- run directory는 `TEST_RUNS_DIR/<timestamp>` 또는 `z_before_begin/web/test/runs/<timestamp>`로 표기한다.
- backend static URL은 보통 `/artifacts/runs/<timestamp>/<filename>` 형태다.
- `/artifacts` mount scope는 `z_before_begin/web/test` 전체다.

## 4. 화면/컴포넌트 구조

### `App.tsx`

| 항목 | 내용 |
|---|---|
| 역할 | 전체 single-page state orchestration. upload, loading, result, accessibility state를 소유한다. |
| 주요 state | `screenState`, `selectedFiles`, `review`, `reviewJob`, `requestError`, `isSubmitting`, `selectedDisability`, `accessibilityData`, `accessibilityError`, `isAccessibilityLoading` |
| 호출 API | `startReviewJob()`, `getReviewJob()`, `getAccessibilityRecommendations()`, `loadMockReview()` |
| 표시 데이터 | overview card용 `overall_result`, `overall_severity`, `contract_info.type`, `reviewed_at` |
| 현재 구현 상태 | 구현됨. `home` / `loading` / `result` state 전환과 polling을 담당한다. |
| TODO/제약 | route persistence 없음. browser refresh 시 frontend state가 사라진다. polling timeout/cancel UI 없음. `reviewContract()` 동기 endpoint는 현재 App flow에서 사용하지 않는다. |

### `Navbar.tsx`

| 항목 | 내용 |
|---|---|
| 역할 | 상단 고정 nav와 primary upload 이동 버튼 표시. |
| 주요 props/state | `onPrimaryAction` |
| 호출 API | 없음 |
| 표시 데이터 | 브랜드명 `법대로`, `before pipeline web`, nav label |
| 현재 구현 상태 | primary button은 upload section으로 scroll한다. |
| TODO/제약 | `소개`, `업로드`, `분석 결과`, `권리 안내` nav button과 mobile menu button은 현재 route/section 이동 handler가 없다. |

### `Hero.tsx`

| 항목 | 내용 |
|---|---|
| 역할 | 첫 viewport hero. Before/Begin 업로드/분석/설명/권리 안내 흐름을 소개하고 upload section으로 이동시킨다. |
| 주요 props/state | `onPrimaryAction` |
| 호출 API | 없음 |
| 표시 데이터 | feature card 3개: 다중 이미지 업로드, OCR snapshot, 권리/지원 안내 |
| 현재 구현 상태 | `계약서 분석 시작`은 upload section으로 scroll한다. |
| TODO/제약 | `UI 설계 확인` 버튼은 현재 click handler가 없다. |

### `UploadPanel.tsx`

| 항목 | 내용 |
|---|---|
| 역할 | 계약서 파일 선택, 선택 파일 목록, 삭제, 분석 시작, mock 결과 로드 버튼을 제공한다. |
| 주요 props/state | `files`, `isSubmitting`, `errorMessage`, `onFilesChange`, `onAnalyze`, `onLoadMock` |
| 호출 API | 직접 호출 없음. `onAnalyze`를 통해 `App.tsx`가 async job API를 호출한다. `onLoadMock`을 통해 mock JSON fetch가 실행된다. |
| 표시 데이터 | 선택된 파일명, 파일 크기 KB, 선택 개수, upload 안내, error message |
| 현재 구현 상태 | `input type="file" multiple accept=".jpg,.jpeg,.png,.pdf"`를 사용한다. 선택 파일은 기존 목록에 append된다. 개별 삭제 가능하다. |
| TODO/제약 | frontend validation은 파일 미선택 수준이다. content type, 빈 파일, PDF 다중/혼합 업로드 validation은 backend가 수행한다. 파일 size/page count 제한, drag hover 세부 상태, 순서 재정렬, 업로드 전 thumbnail preview는 없다. |

### `LoadingPanel.tsx`

| 항목 | 내용 |
|---|---|
| 역할 | async review job의 진행 상태와 단계별 progress를 표시한다. |
| 주요 props/state | `fileCount`, `job` |
| 호출 API | 없음. polling은 `App.tsx`가 수행한다. |
| 표시 데이터 | `job.status`, running step label/order/message, `job.steps[]` |
| 현재 구현 상태 | backend progress step의 `pending` / `running` / `completed` / `failed`에 따라 icon을 표시한다. |
| TODO/제약 | `job`이 아직 null인 초기 loading에서는 단계 목록이 비어 있다. progress percent, 예상 시간, 사용자 cancel, timeout 안내는 없다. |

### `ResultPanel.tsx`

| 항목 | 내용 |
|---|---|
| 역할 | 완료된 `ReviewResult`를 사용자용 결과 화면으로 표시한다. |
| 주요 props/state | `review`, `overviewCards`, `onReset`; local state `openEvidenceIndex` |
| 호출 API | 없음. `resolveArtifactUrl()`로 uploaded file URL만 조립한다. |
| 표시 데이터 | `user_explanation.headline`, `plain_language_summary`, `overall_result`, `overall_severity`, `contract_info`, `summary`, issue cards, recommended actions, `uploaded_files`, evidence, overall assessment, `ocr_warnings` |
| 현재 구현 상태 | result 핵심 UI 구현됨. `uploaded_files` 기반 업로드 원본 preview를 surface한다. |
| TODO/제약 | JSON/MD artifact direct link list 미구현. `review_result.json`, `ocr_output.json`, `user_explanation.md` direct link UI 없음. `section_check`, `content_check`, `risk_summary` raw object는 직접 화면에 표시하지 않는다. PDF uploaded file도 `<img>`로 preview를 시도하므로 별도 PDF renderer는 없다. |

ResultPanel의 issue card 구성:

- 우선 `review.user_explanation.important_points`를 그대로 표시한다.
- `important_points`가 비어 있으면 `review.rule_check`에서 `status !== "PASS"`인 항목을 fallback issue card로 만든다.
- 따라서 section check, content check, risk summary의 세부 raw data는 직접 table/list로 표시되지 않고, explanation builder가 만든 issue/evidence/action에 반영된 범위만 사용자에게 노출된다.

### `AccessibilityPanel.tsx`

| 항목 | 내용 |
|---|---|
| 역할 | result 화면 우측 보조 패널에서 장애 유형별 권리/지원 recommendation cards를 표시한다. |
| 주요 props/state | `selectedDisability`, `recommendation`, `isLoading`, `errorMessage`, `onSelectDisability` |
| 호출 API | 직접 호출 없음. `onSelectDisability`를 통해 `App.tsx`가 `POST /api/v1/accessibility/recommendations`를 호출한다. |
| 표시 데이터 | disability option, recommendation overview, cards, `action_hint`, `law_refs`, fallback/error message |
| 현재 구현 상태 | `visual`, `hearing`, `mobility`, `cognitive`, `mental`, `complex` 6개 option을 제공한다. |
| TODO/제약 | `job_traits` 입력 UI 없음. 현재 API 호출은 항상 `job_traits=[]`다. `action_hint`는 truthy일 때만 표시하므로 nullable/optional 값은 자연스럽게 숨겨진다. |

### Shared UI / utils

| 파일 | 역할 | 현재 구현 상태 / 제약 |
|---|---|---|
| `SectionCard.tsx` | 카드형 wrapper | 화면 섹션 내부 card 스타일을 공통 적용한다. |
| `StatusBadge.tsx` | `ReviewStatus`, `Severity` badge | known enum value에 대한 style map만 있다. runtime enum 확장 시 표시 정합성 확인 필요. |
| `api-client.ts` | API fetch wrapper | `assertOk()`가 HTTP status만 포함한 generic error를 던진다. backend `detail` message는 현재 화면에 직접 노출되지 않는다. |
| `endpoints.ts` | API/artifact URL resolution | `VITE_API_BASE_URL`, dev/prod hostname 기준 base URL을 만든다. `health` endpoint는 정의되어 있으나 현재 UI caller가 없다. |
| `types/review.ts` | frontend TS type | runtime `ReviewResult`보다 좁은 부분이 있어 alignment TODO가 있다. |

## 5. Screen State 정의

### `home`

| 항목 | 내용 |
|---|---|
| 진입 조건 | 앱 최초 진입, `handleReset()`, job 생성 실패, polling 실패, job failed |
| 표시 UI | `Navbar`, `Hero`, upload section, `UploadPanel` |
| 사용자 액션 | 파일 선택, 파일 삭제, 분석 시작, mock scenario 로드 |
| 다음 상태 | 파일이 있으면 `loading`; mock load 성공 시 `result`; 파일 미선택/요청 실패 시 `home` 유지 |
| 실패/예외 처리 | `requestError`가 `UploadPanel` 하단 rose alert로 표시된다. 선택 파일은 reset 전까지 유지된다. |

Home sub-states:

| 상태 | 조건 | 표시 |
|---|---|---|
| initial empty | `selectedFiles.length === 0`, `requestError === null` | "아직 선택된 파일이 없습니다." |
| file selected | `selectedFiles.length > 0` | 파일명/크기/삭제 버튼, 선택 개수 |
| empty error | 파일 없이 `분석 시작` | "먼저 분석할 파일을 업로드해 주세요." |
| request error | job 생성, polling, job failed error | generic fetch error 또는 job error message |

### `loading`

| 항목 | 내용 |
|---|---|
| 진입 조건 | `handleAnalyze()`에서 파일 존재 확인 후 `setScreenState("loading")` |
| 표시 UI | upload section 아래 black loading section, `LoadingPanel` |
| 사용자 액션 | 현재 loading 중 취소/재시도 버튼 없음 |
| 다음 상태 | job `completed` + `result`이면 `result`; job `failed` 또는 polling error면 `home` |
| 실패/예외 처리 | create job 실패는 catch 후 `home`; polling 실패도 catch 후 `home`; run directory 생성 전 early setup failure는 dedicated UI가 없다. |

Loading sub-states:

| 상태 | 조건 | 표시 |
|---|---|---|
| job creation pending | `screenState="loading"`, `reviewJob === null` | 단계 목록 없이 기본 loading copy |
| queued/running | `reviewJob.status`가 `queued` 또는 `running` | backend steps와 active step 표시 |
| completed transient | polling result가 completed | `review` 저장 후 result로 이동 |
| failed transient | polling result가 failed | `requestError` 저장 후 home으로 이동 |

### `result`

| 항목 | 내용 |
|---|---|
| 진입 조건 | mock load 성공 또는 async job completed + `ReviewResult` 존재 |
| 표시 UI | `ResultPanel`, 우측 `AccessibilityPanel` |
| 사용자 액션 | evidence toggle 열기/닫기, 새 분석으로 돌아가기, 장애 유형 선택 |
| 다음 상태 | `새 분석으로 돌아가기`는 `home`; accessibility 선택은 result 내 sub-state만 변경 |
| 실패/예외 처리 | accessibility API 실패는 result 화면을 유지하고 fallback recommendation + 안내 message를 표시한다. |

Result sub-states:

| 상태 | 조건 | 표시 |
|---|---|---|
| result ready | `review !== null` | result summary, issue/action/evidence/OCR warning/upload preview |
| accessibility empty | `selectedDisability === null`, `recommendation === null` | "아직 선택된 유형이 없습니다." |
| accessibility loading | `isAccessibilityLoading === true` | "선택한 유형에 맞는 안내 카드를 불러오는 중입니다." |
| accessibility success | API response 저장 | overview, cards, law ref chips |
| accessibility fallback | API 실패 | fallback cards + "API 응답을 받지 못해 로컬 카드 데이터를 대신 표시합니다." |

## 6. API 연동 화면 요구사항

상세 request/response schema는 `api_spec.md`로 위임한다. 이 섹션은 현재 화면에서 어떤 상태가 어떤 API를 호출하는지만 정리한다.

| API | 현재 UI 호출 여부 | 호출 위치/상태 | 화면 요구사항 |
|---|---:|---|---|
| `POST /api/v1/contract/review/jobs` | 사용함 | `App.tsx` `handleAnalyze()` -> `startReviewJob(files)` | 파일 선택 후 `분석 시작`에서 호출. 성공 시 `ReviewJob` 저장, 실패 시 home error 표시. |
| `GET /api/v1/contract/review/jobs/{job_id}` | 사용함 | `App.tsx` polling `useEffect` -> `getReviewJob(job_id)` | `completed` 또는 `failed`까지 1000ms 간격 조회. steps를 `LoadingPanel`에 표시. |
| `POST /api/v1/contract/review` | 현재 기본 화면 flow에서 미사용 | `api-client.ts`에 `reviewContract(files)` 유틸만 존재 | 동기 review endpoint는 API로 존재하지만 App 화면은 async job path를 사용한다. UI에서 direct sync review 버튼/상태는 없다. |
| `POST /api/v1/accessibility/recommendations` | 사용함 | result 우측 `AccessibilityPanel` option 선택 -> `handleSelectDisability()` | `disability_type`과 `job_traits=[]`를 전송. 성공 시 cards 표시, 실패 시 fallback cards 표시. |
| `GET /health` | 현재 UI에서 미사용 | `endpoints.ts`에 `health` URL만 정의 | 화면 health indicator, preflight banner, server status UI는 없다. 운영자/테스트용 endpoint로만 문서화한다. |

Upload request mapping:

| 선택 파일 수 | FormData field | 현재 구현 |
|---:|---|---|
| 1 | `image` | `formData.append("image", files[0])` |
| 2+ | `images` | 각 파일을 `images`로 append |

Error response display:

- `assertOk()`는 `response.ok`가 아니면 `계약서 분석 작업 생성에 실패했습니다 (422)`처럼 fallback message와 HTTP status만 포함한다.
- backend `detail`의 구체 문구는 현재 UI에 직접 표시하지 않는다.

## 7. Result 화면 기획

현재 result 화면은 `ReviewResult`를 사용자용 설명 중심으로 재구성한다. backend artifact 전체를 파일 목록으로 보여주는 화면은 아니다.

### 현재 표시되는 영역

| UI 영역 | Source field | 표시 내용 |
|---|---|---|
| Review Result hero | `user_explanation.headline`, `plain_language_summary` | 결과 headline과 쉬운 요약 |
| Status badges | `overall_result`, `overall_severity` | PASS/WARNING/VIOLATION, severity badge |
| Overview cards | `overall_result`, `overall_severity`, `contract_info.type`, `reviewed_at` | 판정, 심각도, 계약 유형, 리뷰 시각 |
| Contract Info | `contract_info.employer`, `employee`, `start_date`, `summary` | 사업주, 근로자, 시작일, 요약 |
| Issue Cards | `user_explanation.important_points` | title, law_ref, status, severity, description |
| Issue fallback | `rule_check` non-PASS | important_points가 비어 있을 때만 rule check 기반 fallback |
| Recommended Actions | `user_explanation.recommended_actions` | 권장 조치 목록 |
| Uploaded Images | `uploaded_files[]` | `resolveArtifactUrl(file.url)` 기반 업로드 원본 preview와 저장 파일명 |
| Evidence Toggle | `user_explanation.evidence[]` | title과 excerpt toggle |
| Summary Notes | `user_explanation.overall_assessment[]` | 전체 평가 bullet |
| OCR Warnings | `ocr_warnings[]` | field, note, structured, corrected 표시 |

### 현재 직접 표시되지 않는 데이터

| 데이터 | 현재 화면 상태 |
|---|---|
| `ocr_output.json` direct link | TODO. backend local artifact로 저장되지만 UI link list 없음. |
| `review_result.json` direct link | TODO. backend local artifact로 저장되지만 UI link list 없음. |
| `user_explanation.md` direct link | TODO. backend local artifact로 저장되지만 UI link list 없음. |
| `section_check` raw list | 직접 표시하지 않음. explanation/evidence에 반영된 범위만 노출된다. |
| `content_check` raw map | 직접 표시하지 않음. issue/action/evidence에 반영된 범위만 노출된다. |
| `risk_summary` raw buckets | 직접 표시하지 않음. issue/action/evidence에 반영된 범위만 노출된다. |
| `ocr_snapshot`, `ocr_conflicts`, `scenario_tags` | 현재 TS type에도 명시되지 않았고 UI 직접 표시 없음. |
| `user_explanation.markdown` raw body | direct markdown preview/link 없음. |

### Uploaded original preview boundary

현재 frontend result 화면은 `uploaded_files` 기반 업로드 원본 preview를 surface한다. 이 preview는 backend가 저장한 업로드 원본의 `/artifacts/runs/<timestamp>/<filename>` URL을 사용한다.

주의할 점:

- backend는 `ocr_output.json`, `review_result.json`, `user_explanation.md`를 local artifact로 저장하고 `/artifacts` scope에서 serving 가능하게 만들 수 있다.
- 그러나 현재 UI에 JSON/MD 산출물 direct link list가 구현되어 있다고 쓰면 안 된다.
- JSON/MD artifact direct link UI는 TODO다.
- 현재 preview label은 `Uploaded Images`이고 `<img>` tag를 사용한다. PDF 원본에 대한 별도 PDF viewer/renderer는 구현되어 있지 않다.

## 8. Error / Empty / Loading State

| 상태 | 발생 조건 | 현재 UI 처리 | 다시 시도 가능 여부 / TODO |
|---|---|---|---|
| 파일 미선택 | `selectedFiles.length === 0`에서 분석 시작 | API 호출 없이 `requestError` 표시 | 파일 선택 후 다시 분석 가능 |
| frontend validation 부족 | accept attribute 외 타입/조합 사전 검증 없음 | 선택 목록에는 추가됨 | backend validation에 의존. 사전 안내/차단은 TODO |
| validation failure | backend 422: 파일 없음, 빈 파일, 미지원 content type, PDF 다중/혼합 등 | `assertOk()` generic error + status를 home error로 표시 | 파일 삭제/재선택 후 다시 분석 가능. backend detail 노출은 TODO |
| upload/review job 생성 실패 | network error, server down, non-2xx | loading에서 home으로 복귀, `requestError` 표시 | 선택 파일 유지. server 확인 후 다시 분석 가능 |
| polling 실패 | `GET /jobs/{job_id}` fetch 실패 또는 non-2xx | home으로 복귀, 상태 조회 실패 message 표시 | 선택 파일 유지. 다시 분석은 가능하나 기존 job 복구 UI 없음 |
| job failed | polling response `status="failed"` | `job.error` 또는 fallback message를 home error로 표시 | 선택 파일 유지. 재분석 가능 |
| run directory 생성 전 early setup failure | `_run_review_job()`의 `_create_run_dir()`가 try block 밖에서 실패할 가능성 | dedicated error UI 없음. job이 queued/running에 머물 수 있고 timeout이 없다. | early setup failure를 `failed`로 반영하고 timeout UI를 추가해야 함 |
| OCR failure | run directory 생성 후 OCR exception | backend async job failed + `error.txt` 가능 | frontend는 partial artifact를 보여주지 않고 home error만 표시 |
| review/explanation pipeline failure | section/rule/content/explanation/artifact 저장 중 exception | backend async job failed + 가능한 경우 `ocr_output.json`, `error.txt` | frontend는 partial artifact를 보여주지 않고 home error만 표시 |
| accessibility recommendation 실패 | accessibility API 400/422/network | result 유지, local fallback card 표시, `accessibilityError` 표시 | 장애 유형 재선택으로 재시도 가능 |
| 네트워크 오류 | API fetch 자체 실패 | 해당 handler의 fallback error 표시 | server/base URL 확인 후 다시 시도 |
| loading empty steps | job 생성 직후 `reviewJob === null` | LoadingPanel 기본 문구만 표시, steps 없음 | skeleton/progress placeholder TODO |

## 9. Accessibility / UX 고려사항

이 문서에서 말하는 accessibility는 두 층위를 구분한다.

1. 접근성 추천 기능: 사용자가 장애 유형을 선택하면 권리/지원/질문/법 카드와 법령 근거 chip을 보여주는 product feature.
2. UI 자체의 접근성 구현: keyboard navigation, aria label, focus style, contrast, screen reader semantics 등 화면 품질.

### 접근성 추천 기능

| 항목 | 현재 구현 |
|---|---|
| 입력 | `disability_type`, `job_traits` |
| 현재 UI 입력값 | `disability_type`만 버튼으로 선택. `job_traits`는 항상 `[]` |
| 지원 key | `visual`, `hearing`, `mobility`, `cognitive`, `mental`, `complex` |
| 표시 card | `kind`, `title`, `description`, `law_refs`, optional/nullable `action_hint` |
| fallback | API 실패 시 `fallbackAccessibilityRecommendation(disabilityType)` 사용 |
| loading | "선택한 유형에 맞는 안내 카드를 불러오는 중입니다." 표시 |

`action_hint`는 backend/catalog에서 `null`이거나 생략될 수 있고, frontend TS type도 optional로 되어 있다. 현재 UI는 `card.action_hint`가 truthy인 경우에만 action hint box를 렌더링한다.

### UI 자체 접근성 현황 / 제약

- file input은 hidden input + clickable label 구조로 동작한다.
- result evidence는 button으로 toggle되지만 expanded state ARIA는 없다.
- icon-only remove button, mobile menu button에는 명시적 `aria-label`이 없다.
- mobile menu button은 현재 menu open 동작이 없다.
- loading progress는 visual icon 중심이며 progressbar ARIA가 없다.
- 따라서 현재 구현은 "장애 특화 추천 기능"을 제공하지만, UI 자체가 접근성 감사까지 완료되었다고 설명하면 안 된다.

## 10. Privacy / Artifact UI Boundary

Before/Begin 화면은 업로드 계약서와 결과를 다루므로 개인정보 및 계약 민감정보 경계를 명확히 설명해야 한다.

필수 boundary:

- 업로드 계약서와 OCR/review 결과에는 개인정보, 사업장, 임금, 비자, 기숙사, 계약 특약 등 민감정보가 포함될 수 있다.
- 현재 기본 Before/Begin review path는 Vertex AI OCR 및 Vertex-backed LLM content review를 사용한다.
- UI와 문서가 프로젝트 전체 개인정보가 Vertex를 피한다고 설명하면 안 된다.
- `/artifacts` mount scope는 `z_before_begin/web/test` 전체이고, run output은 `z_before_begin/web/test/runs/<timestamp>` 아래 저장된다.
- 현재 UI direct link는 `uploaded_files` 기반 업로드 원본 preview 중심이다.
- JSON/MD artifact direct link UI는 TODO다.
- production 전 access control, retention/TTL, request/body logging 제한, artifact exposure, provider disclosure 정책이 필요하다.

Artifact UI boundary:

| 항목 | 현재 상태 |
|---|---|
| 업로드 원본 | result 화면에서 `uploaded_files[].url` preview로 표시 |
| `ocr_output.json` | local artifact 저장 가능. UI direct link 없음 |
| `review_result.json` | local artifact 저장 가능. UI direct link 없음 |
| `user_explanation.md` | local artifact 저장 가능. UI direct link 없음 |
| `/artifacts` 접근 제어 | 없음 |
| retention/TTL | 없음 |
| request/body logging policy | 문서상 필요 정책, 현재 화면 구현 아님 |

## 11. Current Limitations / TODO

- JSON/MD artifact direct link UI 미구현. `ocr_output.json`, `review_result.json`, `user_explanation.md` link list는 result 화면에 없다.
- `app.state.review_jobs`가 in-memory라 backend restart에 취약하다. browser refresh도 `reviewJob`/`review` frontend state를 잃어 기존 job을 복구하지 못한다.
- frontend/backend `ReviewResult` type mismatch가 있다. runtime response의 `scenario_tags`, `ocr_snapshot`, `ocr_conflicts`, `content_check`, `risk_summary`는 현재 TS `ReviewResult`에 명시되어 있지 않다.
- `ocr_warnings.corrected` optional mismatch가 있다. runtime warning은 `raw`만 있고 `corrected`가 없을 수 있으나 TS type은 `corrected` required다.
- `UserExplanation.important_points.law_ref`는 nullable/optional 또는 extra fields(`issue_type`, `risk_bucket`)를 포함할 수 있으나 frontend type은 더 좁다.
- accessibility `action_hint` nullable/optional alignment가 필요하다. 현재 UI는 truthy 값만 표시한다.
- run directory 생성 전 early setup failure 표시 한계가 있다. `_create_run_dir()` 실패가 polling `failed` 상태로 보장되지 않고, frontend timeout UI가 없다.
- `/artifacts` access control/TTL이 없다. mount scope도 `z_before_begin/web/test` 전체다.
- JSON/MD direct link를 추가하더라도 개인정보/민감정보 노출 경계, 권한, retention 정책 없이는 production 노출로 간주하면 안 된다.
- `POST /api/v1/contract/review` 동기 endpoint는 API client 유틸은 있으나 현재 화면 flow에서 호출하지 않는다.
- `GET /health`는 endpoint constant만 있고 현재 UI health 상태 표시에 쓰이지 않는다.
- PDF uploaded original은 `<img>` preview에 적합하지 않으므로 별도 PDF preview/다운로드 UX가 필요하다.
- frontend validation은 파일 미선택 외에는 backend에 의존한다. 파일 size/page count/concurrency/timeout/cancel 정책은 미정이다.
- navbar 일부 버튼과 hero secondary button은 현재 동작이 없는 visual affordance다.
- UI 직접 사항은 아니지만, 팀 통합/integrated review에서 Before/Begin `law_chunks` asset과 main backend corpus sync 확인이 필요하다.
- 팀 merge 후 Before/Begin, Bridge, After integrated screen plan을 재작성해야 한다.

## 12. Acceptance Criteria

현재 화면 기준 acceptance checklist:

- [ ] Before/Begin 문서임이 명확하고 main After 화면과 혼동되지 않는다.
- [ ] 현재 `z_before_begin/web/front`가 route 기반이 아니라 `screenState` 기반 single-page flow임을 설명한다.
- [ ] 사용자는 파일을 선택하고 업로드 목록에서 확인할 수 있다.
- [ ] 파일 미선택 상태에서 분석 시작 시 화면 error가 표시된다.
- [ ] 선택 파일로 async review job 생성이 가능하다.
- [ ] `POST /api/v1/contract/review/jobs` 호출 위치와 실패 표시가 문서화되어 있다.
- [ ] `GET /api/v1/contract/review/jobs/{job_id}` polling progress 표시가 문서화되어 있다.
- [ ] 완료 결과 표시가 가능하며 `ResultPanel`이 실제 표시하는 field만 기획에 포함되어 있다.
- [ ] `uploaded_files` 기반 업로드 원본 preview가 현재 구현된 UI로 설명되어 있다.
- [ ] JSON/MD artifact direct link는 TODO로 분리되어 있다.
- [ ] OCR warning 표시와 `ocr_warnings.corrected` mismatch가 설명되어 있다.
- [ ] section/rule/content/risk summary raw data의 직접 표시 여부가 실제 구현 기준으로 구분되어 있다.
- [ ] 실패 상태 표시와 다시 시도/초기화 방식이 설명되어 있다.
- [ ] accessibility recommendation 표시와 fallback behavior가 설명되어 있다.
- [ ] `action_hint` nullable/optional 가능성이 반영되어 있다.
- [ ] `GET /health`가 현재 UI에서 쓰이지 않는다는 점이 명시되어 있다.
- [ ] privacy/Vertex/artifact boundary가 과장 없이 설명되어 있다.
- [ ] `/artifacts` mount scope와 run output path가 정확히 표기되어 있다.
- [ ] integrated screen plan은 팀 merge 이후 별도 재작성 대상으로 남아 있다.
