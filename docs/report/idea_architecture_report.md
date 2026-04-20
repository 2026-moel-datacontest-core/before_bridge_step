# K-Labor Shield 아이디어·아키텍처 보고서

작성일: `2026-04-17`

업데이트 메모: 이 보고서는 2026-04-17 아이디어/아키텍처 보고서 초안으로 보존한다. 2026-04-20 기준 최신 MVP 상태는 SCN-004-DEMO-FREEZE main path, SCN-001-BRIDGE-DEMO answer-only handoff, demo preflight pass, full 60 answer evidence `PASS=44 / PARTIAL=16 / FAIL=0`까지 반영된 상태다. 최신 운영 기준은 `docs/ops/runbook.md`, 최신 발표 script는 `docs/demo/demo_scenario.md`, 최신 eval 근거는 `eval/reports/answer_evidence_2026-04-20.summary.md`를 우선한다.

기준선:

- 서비스 corpus 기준일: `selected_as_of = 2026-04-11`
- RAG 및 시나리오 상태 기준일: `2026-04-17` (초안 작성 당시)
- frontend 구현 상태 기준일: `2026-04-17` (초안 작성 당시)
- 문서 작성일: `2026-04-17`

## 1. 프로젝트 개요

`law-main-road`는 계약 단계 위험 탐지와 분쟁 발생 후 대응 가이드를 하나의 흐름으로 연결하는 근거 기반 노동권 보호 AI입니다. 이 프로젝트는 단순한 법령 Q&A 챗봇이 아니라, 사용자의 실제 상황을 입력으로 받아 관련 법 조문을 검색하고, 검색된 근거 위에서만 답변과 다음 행동 가이드를 생성하는 구조를 목표로 합니다.

본 서비스는 일반 사용자도 사용할 수 있는 범용 노동권 보조 도구이지만, 외국인 근로자, 장애인 근로자, 사회초년생, 비정형 노동자처럼 정보 접근성이 낮은 사용자에게 더 직접적인 보호 효과를 제공할 수 있도록 시나리오와 데이터 범위를 설계했습니다.

전체 서비스 흐름은 `Before`, `Bridge`, `After`, `Recovery`의 네 단계로 구성됩니다. `Before`는 계약 단계의 위험을 탐지하고, `Bridge`는 계약 단계에서 발견된 위험을 이후 분쟁 상황과 연결하며, `After`는 실제 피해가 발생한 뒤 권리와 대응 순서를 안내합니다. `Recovery`는 후속 문서 작성이나 회복 지원 단계로 두고 있으나, 현재 MVP의 핵심 구현 범위는 아닙니다.

## 2. 문제 정의

많은 사용자가 근로계약, 해고, 임금 체불, 육아휴직, 가족돌봄휴가 같은 노동 문제를 겪어도 관련 법과 절차를 바로 이해하기 어렵습니다. 사용자 입장에서 필요한 것은 법 조문 원문 자체보다, 지금 자신의 상황에서 어떤 권리가 있고 무엇을 먼저 해야 하는지에 대한 빠르고 실행 가능한 설명입니다.

이 문제는 일반 근로자에게도 발생하지만, 외국인 근로자, 장애인 근로자, 사회초년생, 비정형 노동자처럼 정보 접근성이 낮은 사용자에게 더 크게 나타납니다. 즉, 이 프로젝트는 일반 사용자도 사용할 수 있는 범용 서비스이면서, 정보 취약 사용자를 더 잘 돕는 구조를 지향합니다.

동시에 일반적인 생성형 AI는 실제 검색 결과에 없는 조문을 자연스럽게 섞어 말할 위험이 있습니다. 노동권 안내 서비스에서는 이 환각 문제가 곧 신뢰 문제로 이어질 수 있으므로, 본 프로젝트는 검색 근거를 기반으로만 답변하는 구조를 핵심 과제로 삼고 있습니다.

## 3. 해결 방식 및 서비스 구조

이 프로젝트의 기본 구조는 `Before -> Bridge -> After` 흐름을 하나의 서비스 안에서 연결하는 것입니다.

### Before

계약서 원문 또는 OCR 결과를 입력받아 주요 항목을 읽고, 누락, 불명확, 주의 필요, 위법 가능성 신호를 분류하며 관련 조문을 함께 제시합니다. 즉, 사용자가 계약서에 서명하기 전에 위험을 인지할 수 있도록 돕는 단계입니다.

### Bridge

계약 단계에서 발견된 위험 태그와 요약을 저장해 두고, 이후 분쟁이 발생했을 때 “계약 단계에서 이미 예견 가능했던 위험”으로 연결합니다. 이 단계는 `Before`와 `After`를 단절된 기능이 아니라 하나의 서비스 경험으로 이어주는 역할을 합니다.

### After

사용자가 해고, 체불, 휴직 거절, 분쟁 상황 등을 자유롭게 서술하면 사건을 구조화하고 관련 조문을 검색한 뒤, 근거에 기반한 대응 순서와 증거 수집 방향을 안내합니다. 현재 저장소 구현의 중심도 이 `After` 흐름에 맞춰져 있습니다.

### Recovery

회복 및 후속 문서 작성 지원 단계입니다. 현재 MVP 핵심 범위는 아니며, 발표에서는 확장 가능성으로 설명하는 수준으로 두고 있습니다.

### 구조적 차별점

이 프로젝트의 차별점은 다음과 같습니다.

- 일반 사용자도 사용할 수 있지만, 외국인 근로자, 장애인 근로자, 돌봄 상황 사용자처럼 정보 취약성이 큰 경우까지 포괄하는 구조
- 계약 단계와 분쟁 단계를 분리하지 않고 하나의 흐름으로 연결하는 구조
- 외국인 계약 문제, 최저임금/수습, 장애인 편의제공, 부당해고/체불, 육아휴직/가족돌봄휴가까지 아우르는 시나리오 범위
- 검색 결과와 grounded context에 없는 조문을 명시적으로 인용하면 검증 단계에서 실패 처리되도록 설계한 grounded answer 구조
- 실제 시나리오 문안을 먼저 만들고, 현재 corpus로 가능한지 검증해 범위를 조정하는 운영 방식

## 4. 현재 구현 수준

현재 구현 수준은 `공통 기반`, `After 단계`, `Before 단계`로 나누어 정리할 수 있습니다.

### 4-1. 공통 기반

| 영역 | 현재 상태 |
|---|---|
| 데이터 | `backend/data/law_chunks/all_chunks.json` 기준 `1722` chunks 고정 |
| DB | PostgreSQL `law_chunks` `1722`건, embedding `1722 / 1722` 완료 |
| Retrieval | `POST /api/v1/retrieve` 구현 완료, `hit@5 = 60/60 (100.00%)` |
| 검증 기반 | eval runner, scenario smoke, citation 검증 구조 확보 |

이 공통 기반 위에서 `Before`와 `After` 기능을 각각 붙이는 구조로 개발 중입니다.

### 4-2. After 단계 구현 수준

| 영역 | 현재 상태 |
|---|---|
| Answer | `POST /api/v1/answer` 구현 완료, `citation_grounding_clean = 60/60` |
| 응답 구조 | 검색 결과에 없는 조문 인용 금지, `cited_articles` 포함 응답 고정 |
| 평가 | baseline answer eval `137/153`, partial/failure `16` |
| 시나리오 검증 | `SCN-001`, `SCN-004`, `SCN-005` After 핵심 데모 안정화 |
| 문서 초안 | `POST /api/v1/documents/draft` 구현 완료, SCN-004 진정서/이유서 초안 지원 |
| Frontend | Next.js `/after` 4-route flow 구현 완료, copy/print 포함 |

현재 저장소 기준으로는 `After` 단계의 핵심 backend 로직과 검증 자산이 먼저 구현된 상태입니다.

### 4-3. Before 단계 구현 수준

| 영역 | 현재 상태 |
|---|---|
| 파이프라인 아키텍처 | Phase A(표준 항목 매핑) 및 Phase B(OCR→비교→검증→LLM) 구조 설계 및 코드 초안 작성 완료 |
| OCR 및 구조화 | API 연동을 통한 계약서 이미지 2-Layer OCR 테스트 완료 및 JSON 구조화 포맷(`structured`, `raw_sections`) 치환 확인 |
| 법령 검색(Retrieval) | OCR로 추출·구조화된 JSON 데이터를 기반으로 관련 법 조항 및 청크(`law_chunks`) 추출 테스트 완료 |
| 단위 로직 구현 | LLM 환각 통제를 위한 수치 검증 로직(`rule_validator.py`) 및 표준 항목 대조 로직(`section_comparator.py`) 초안 확보 |
| 테스트 파이프라인 | T-0(상수/출력 검증)부터 T-7(SCN-002 시나리오 검증)까지 단계별 단위/통합 테스트 환경 구축 완료 |

현재 구현된 코드 초안과 API 테스트 결과를 바탕으로, 구축해 둔 T-0 ~ T-7 테스트 파이프라인을 따라 모듈별 단위 테스트와 전체 통합 테스트를 이어서 진행하는 방향입니다.

## 5. 대표 시나리오와 데모 전략

데모 시나리오는 corpus와 retrieval/answer 품질이 검증된 범위 안에서 선정했으며, 발표 안정성과 메시지 명확성을 함께 고려했습니다.

| 시나리오 | 유형 | 현재 상태 | 발표 활용도 |
|---|---|---|---|
| `SCN-001` 외국인 계약서·기숙사·차별·사업장 변경 | `Full` | 커버됨, `top_k=10` 데모 경로에서 안정화 | 제품 스토리 대표 후보 |
| `SCN-004` 카톡 해고 및 임금·퇴직금 체불 | `After` | frontend demo 구현 완료 | 실제 frontend main demo |
| `SCN-005` 육아휴직 및 가족돌봄휴가 거절 | `After` | 커버됨 | 사회적 공감도가 높은 보조 시연 후보 |
| `SCN-003` 장애인 편의제공 및 지원 제도 안내 | `Before` | 최소 데이터 보강 후 커버됨 | 확장성 설명용 후보 |
| `SCN-002` 최저임금/수습 꼼수 | `Before` | `Partial` | 설명형 데모까지만 권장 |

제품 스토리의 메인 시나리오는 `SCN-001`입니다. 이 시나리오는 정보 취약 사용자 문제를 설명하면서 `Before -> Bridge -> After` 전체 흐름을 한 번에 보여줄 수 있어 프로젝트 메시지를 가장 잘 전달합니다.

다만 현재 실제 frontend main demo는 `SCN-004`입니다. `SCN-004`는 `/after`에서 권리 안내와 노동청 진정서/노동위원회 이유서 초안까지 end-to-end로 보여줄 수 있습니다. `SCN-001 Full`은 `top_k=10`, `ef_search=100` 데모 경로에서 제품 스토리와 API smoke 후보로 유지하고, `SCN-005`를 backup answer scenario로 준비하는 것이 안전합니다. `SCN-003`은 확장성 설명용으로 적합하며, `SCN-002`는 자동 숫자 판정이 현재 범위를 벗어나므로 설명형 데모로 제한하는 것이 맞습니다.

## 6. 제출 전 실행 계획

현재 프로젝트는 아이디어 검토 단계가 아니라 이미 동작하는 RAG MVP와 SCN-004 frontend demo를 확보했고 QA/content/frontend rehearsal도 통과한 상태입니다. 따라서 제출 전 계획의 핵심은 신규 기능을 크게 넓히는 것이 아니라, 현재 시스템의 QA 정합성과 시연 안정성을 유지하는 것입니다.

### 6-1. 현재 기준선

- 법령 corpus 고정 완료: `1722` chunks
- retrieval MVP 완료: `hit@5 = 60/60`
- grounded answer MVP 완료: `citation_grounding_clean = 60/60`
- SCN-004 document draft API 완료
- SCN-004 frontend flow 완료
- scenario audit 완료: 주요 데모 시나리오 5개 검토
- 남은 핵심 이슈: 기능 확장보다 backend/frontend contract QA 통과 상태와 demo path 안정성 유지

### 6-2. 공통 계획

- 청킹 결과와 corpus 기준선 유지
- PostgreSQL + pgvector + embedding 상태 유지
- 발표용 메인 시나리오 1개와 백업 시나리오 1~2개 확정
- 질문 문안, 기대 citation, 시연 순서 최종 고정
- 발표 자료에서 “현재 구현 완료”와 “후속 확장”을 명확히 분리

### 6-3. After / Frontend QA 계획

- Step 0: `/api/v1/answer`와 frontend `AnswerResponse` type 정합성 확인
- Step 1: `/api/v1/documents/draft`와 frontend `DocumentDraftResponse` type 정합성 확인
- Step 2: `buildLegalBasis()`가 grounded_context_ids 기준 retrieved_chunks만 전달하는지 확인
- Step 3: `buildCaseIntake()`가 빈 row 제거, 기본 object/list 채움, 개인정보 최소 수집 원칙을 지키는지 확인
- Step 4: `/after` happy path, API error, direct URL guard, citation 없음 상태, copy/print, mobile layout smoke
- Step 5: QA에서 RAG regression이 재현될 때만 좁게 answer/retrieval을 수정

핵심은 새 화면이나 새 문서 타입을 추가하지 않고, 이미 구현한 SCN-004 path를 안정화하는 것입니다.

### 6-4. Before 계획

`Before` 단계는 계약서 서명 전 위협 요소를 탐지하는 핵심 파이프라인으로 현재 아키텍처 설계와 단위 API 테스트를 마친 후 본격적인 기능 테스트 및 통합 테스트 단계에 있습니다.

- Step 0: 파이프라인 안정화 및 JSON 스키마 확정
  - Phase A(표준 항목 매핑)와 Phase B(실시간 검토) 간의 데이터 규격 고정
  - OCR 결과물(`raw_text`)을 `structured`, `sections` 등 분석 가능한 JSON 포맷으로 치환하는 로직 안정화
- Step 1: 2-Layer OCR 및 항목 분류(Classification) 고도화
  - 단순 텍스트 추출을 넘어 계약서 내 '임금', '근로시간' 등 핵심 항목을 `standard_map.json`의 표준 ID와 매칭하는 정합성 확보
  - 비표준 조항(독소 조항) 및 필수 항목 누락 여부를 판단하기 위한 `section_comparator.py` 구현 완료
- Step 2: LLM 환각 방지를 위한 Deterministic Logic 강화
  - 최저임금, 소정근로시간 등 수치 계산이 필요한 영역은 LLM에 맡기지 않고 `rule_validator.py`(Python 로직)를 통해 1차 검증 수행
  - 법령 검색(Retrieval) 시 추출된 `law_chunks`가 실제 해당 계약 조항과 법적으로 관련이 있는지에 대한 Re-ranking 로직 검토
- Step 3: Before 특화 시나리오(SCN-002, 003) 검증
  - `SCN-002`: 단시간 근로자(알바)의 수습 감액 등 위법 수치 탐지 집중 테스트
  - `SCN-003`: 장애인 근로자 등 취약 계층을 위한 '정당한 편의제공' 항목 누락 탐지 로직 확인
- Step 4: Bridge 인터페이스 정의
  - Before 단계에서 탐지된 위반 사항을 After(권리 구제) 단계로 자연스럽게 넘기기 위한 핵심 필드 및 요약(Summary) 구조 확정

### 6-5. 범위 고정

| 구분 | 항목 |
|---|---|
| 이번 제출 범위 안 | 법령 retrieval, grounded answer, cited articles 표시, SCN-004 문서 초안 API, SCN-004 frontend demo, `Before` / `After` / `Bridge` 흐름 설명 |
| 이번 제출 범위 밖 | Recovery 본격 구현, 연도별 최저임금 자동 비교, 단순노무 직종 자동 판정, 대규모 hybrid retrieval 전환, Local LLM 운영 전환, SCN-001 문서 타입 확장, sessionStorage backup/restore |

SCN-005 After 문서 타입 확장은 SCN-004 freeze 기준을 유지한 다음 구현 후보로 진행 가능하다.
SCN-001 문서 타입과 Before-Bridge-After frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 검토한다.

### 6-6. 리스크와 대응

1. `SCN-001` Full 단일 질의 운영 조건
   - 일반 API default `top_k=5`가 아니라 demo payload `top_k=10`, `ef_search=100`으로 호출해야 selective decomposition이 발동한다.
2. snapshot 혼합 위험
   - raw source HEAD가 더 최신이어도 발표와 검증은 frozen corpus(`2026-04-11`) 기준으로만 정리
3. 범위 확장 욕심
   - OCR, Recovery, 추가 문서 타입을 한 번에 모두 보여주지 않고 SCN-004 end-to-end 안정성에 집중
4. frontend 확장보다 QA가 더 중요
   - 새 화면보다 backend/frontend schema 정합성과 demo smoke를 우선

## 7. 팀 구성 및 역할 분담

본 프로젝트는 2인 팀으로 운영되며, 역할은 기능 단계 기준으로 나누고 있습니다.

| 담당자 | 담당 범위 | 현재 상태 |
|---|---|---|
| 김종원 | `After` 단계 전체, 데이터 전처리 및 split 작업, 현재 저장소의 구현 코드 | 진행 및 구현 완료 범위 다수 존재 |
| 김민수 | `Before` 단계 전체 | 별도 진행 예정 / 담당 범위 고정 |

김종원은 사용자의 분쟁·사후대응 상황 입력 처리, 관련 조문 retrieval, grounded answer generation, citation grounding 구조, `After` 시나리오 검증과 데모 흐름 설계를 담당합니다. 또한 법령 데이터를 실제 서비스에서 사용할 수 있는 형태로 나누는 데이터 split 및 전처리 작업도 함께 진행했습니다. 따라서 현재 저장소 안의 핵심 backend 로직과 corpus 기반은 김종원이 진행한 결과물입니다.

김민수는 계약서 입력 및 분석 흐름, 계약 단계 위험 탐지, `Before` 결과 구조화, 계약서 기반 데모 시나리오 정리, 이후 `Bridge` 연결에 필요한 `Before` 결과 준비를 전담합니다.

저장소만 보면 구현이 한쪽으로 치우쳐 보일 수 있지만, 이는 분담의 결과입니다. 김종원이 데이터 전처리와 backend 로직을 먼저 진행했기 때문에 현재 저장소 기준으로는 `After` 흐름이 먼저 구체화된 상태이며, 이후 `Before` 모듈이 붙으면서 `Before -> Bridge -> After`의 전체 흐름으로 통합되는 구조입니다. 초기 MVP 앱도 로직을 먼저 완성한 쪽이 우선 진행하는 방식으로 보고 있습니다.

## 8. 인프라 확장성과 클라우드 아키텍처 방향

### 8-1. 현재 인프라 기준선

현재 프로젝트는 기능 검증 중심 MVP 단계이며, 인프라는 아직 로컬 개발 기준에 가깝습니다.

- backend: FastAPI
- database: PostgreSQL + pgvector
- retrieval / answer API 구현 완료
- embedding model: `gemini-embedding-001`
- answer model: `gemini-2.5-flash`
- 개발 환경: WSL + conda

즉, 현재는 Vertex AI 기반 MVP로 동작 검증을 완료한 상태이고, 이후 단계에서 GCP 위에 실제 서비스형 인프라를 구성하는 것이 다음 확장 포인트입니다.

### 8-2. 왜 GCP인가

GCP 선택은 AWS가 불가능해서가 아닙니다. AWS도 Amazon Bedrock, SageMaker, EC2 GPU, RDS PostgreSQL 등으로 유사한 구성이 가능합니다.

그럼에도 우리 팀이 GCP를 선택한 이유는 다음과 같습니다.

- 이 프로젝트는 단순 웹 배포보다 생성형 AI, 임베딩, RAG, 이후 GPU 기반 Local LLM 확장까지 포함하는 AI 중심 프로젝트입니다.
- `Vertex AI 기반 MVP -> GCP GPU 기반 Local LLM 확장`이라는 흐름이 더 단순하고 일관된 AI-first 확장 스토리라고 판단했습니다.
- 즉, GCP 선택의 핵심 이유는 프로젝트의 학습 목표와 인프라 확장 방향을 더 자연스럽게 설명할 수 있기 때문입니다.

### 8-3. 왜 멀티클라우드를 지양하는가

멀티클라우드 구성이 항상 나쁜 것은 아닙니다. 실제로 대규모 조직에서는 규제, 장애 대비, 특정 서비스 선택, 벤더 종속 완화 같은 이유로 GCP와 AWS를 함께 쓰기도 합니다.

하지만 현재 프로젝트 단계에서는 두 클라우드를 섞는 것보다 하나의 클라우드로 통일하는 편이 더 적절합니다.

- RAG API, PostgreSQL, 모델 호출, 이후 GPU 기반 Local LLM 확장까지 서비스 간 연결이 긴밀함
- 클라우드를 혼합하면 네트워크 홉이 늘고 지연 가능성이 커짐
- 인증, 권한, 비밀값, 로그, 모니터링 관리 포인트가 늘어남
- 교육과정 프로젝트와 포트폴리오 관점에서 아키텍처 설명이 불필요하게 복잡해짐

따라서 이 프로젝트는 멀티클라우드 실험보다, 단일 클라우드 기반의 일관된 AI 서비스 아키텍처를 우선합니다.

### 8-4. 기본 방향: serverless-first

강사님 방향과 연결했을 때, 현재 프로젝트와 가장 잘 맞는 선택지는 Cloud Run 중심의 serverless-first 아키텍처입니다.

| 영역 | 권장 구성 |
|---|---|
| API 서버 | `Cloud Run` |
| 배치 작업 | `Cloud Run Jobs` |
| DB | `Cloud SQL for PostgreSQL` |
| 비밀값 | `Secret Manager` |
| 파일/산출물 | `Cloud Storage` |
| 오케스트레이션 | `Workflows` |
| 로그/모니터링 | `Cloud Logging`, `Cloud Monitoring` |
| managed AI | `Vertex AI` |

이 구조는 현재 FastAPI 컨테이너 구조를 거의 그대로 살릴 수 있고, 서버 운영보다 서비스 연결과 아키텍처 설계에 집중할 수 있다는 장점이 있습니다.

다만 예외는 GPU 기반 Local LLM 확장입니다. `Ollama + Qwen` 같은 self-hosted Local LLM을 상시 구동하려면 완전한 서버리스보다 `Compute Engine GPU VM`이 더 현실적일 수 있습니다. 따라서 현재 프로젝트의 권장 방향은 다음과 같습니다.

- 기본 방향: serverless-first (`Cloud Run` 중심)
- 예외적 확장: Local LLM이 꼭 필요할 때만 GPU VM 추가

### 8-5. 권장 확장 로드맵

1. `Cloud Run + Cloud SQL + Secret Manager + Artifact Registry + Cloud Build`로 기본 배포 구조 완성
2. `Compute Engine GPU + Ollama + Qwen` 기반 Local LLM 추론 서비스 추가
3. `Cloud Storage + Cloud Run Jobs + Workflows + Pub/Sub`로 데이터 파이프라인 자동화
4. `Terraform`, 최소 권한 IAM, 모니터링/알림으로 운영성과 재현성 보강

이 로드맵은 현재 구현 완료 범위가 아니라, 클라우드 교육과정 프로젝트로 확장할 때의 다음 방향입니다.

## 9. 기대 효과 및 강사님 검토 요청 사항

### 9-1. 기대 효과

- 일반 사용자도 계약 전 위험과 사후 대응 방향을 더 빠르게 이해할 수 있음
- 정보 취약성이 큰 사용자에게는 더 직접적인 보호 효과를 줄 수 있음
- 분쟁 발생 후에도 법 조문 근거와 함께 대응 순서를 정리받을 수 있음
- 공공기관, 상담 보조 인력, 지원 활동가에게도 보조 도구로 확장 가능
- 단순 Q&A가 아니라 “근거 제시 + 다음 행동 안내” 구조를 보여줄 수 있음

### 9-2. 강사님께 검토받고 싶은 포인트

프로젝트 포지셔닝 관련:

- 문제 정의가 충분히 선명한지
- “일반 사용자도 쓰는 범용 서비스”와 “취약 노동자에게 더 유용한 서비스” 사이의 포지셔닝이 적절한지
- 현재 MVP 설명에서 Recovery 같은 확장 기능을 어느 수준까지 언급하는 것이 적절한지

시연 및 실행 계획 관련:

- 발표 메인 시나리오를 `SCN-001`로 두는 것이 설득력 있는지
- 메인 시나리오를 하나로 고정하는 전략이 적절한지
- `SCN-002`를 과감히 제외하고 안정적 시나리오 중심으로 가는 판단이 맞는지
- “실제 구현 완료”와 “후속 확장”의 경계를 발표 자료에서 어떻게 설명하는 것이 좋은지

팀 구성 관련:

- 2인 팀 기준에서 현재 역할 분담이 적절한지
- `After`를 먼저 구현하고 `Before`를 후속 연결하는 진행 방식이 괜찮은지
- 데이터 전처리와 backend 로직을 한 사람이 맡고, 다른 한 사람이 `Before`를 맡는 구조가 현실적인지
- 발표 때 현재 저장소가 `After` 중심으로 보이는 점을 어떻게 설명하면 가장 자연스러운지

인프라 확장 관련:

- Vertex AI 기반 MVP 이후 어떤 인프라 확장 단계를 우선해야 하는지
- `Compute Engine GPU + Ollama`가 Local LLM 확장 1차안으로 적절한지
- `Cloud Run` 중심 managed 구조와 self-hosted GPU 추론 구조를 함께 가져가는 방식이 과하지 않은지
- 교육과정 포트폴리오 기준으로, 배치 파이프라인 자동화와 IaC 중 무엇을 더 우선해서 보여주는 것이 좋은지
