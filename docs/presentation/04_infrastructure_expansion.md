# Infrastructure Expansion For Instructor Review

작성일: `2026-04-15`

## 문서 목적

- 현재 MVP를 클라우드 교육과정 프로젝트로 확장할 때 어떤 인프라 방향이 적절한지 정리
- 단순히 앱을 배포하는 수준이 아니라, "왜 이 구성이 클라우드 포트폴리오로 의미가 있는지"까지 설명하기 위한 문서

## 1. 현재 인프라 기준선

현재 프로젝트는 기능 검증 중심 MVP 단계이며, 인프라는 아직 로컬 개발 기준에 가깝습니다.

### 현재 사용 중인 구성

- backend: FastAPI
- database: PostgreSQL + pgvector
- retrieval / answer API 구현 완료
- embedding model: `gemini-embedding-001`
- answer model: `gemini-2.5-flash`
- 개발 환경: WSL + conda

즉, 현재는 **Vertex AI 기반 MVP**로 동작 검증을 완료한 상태이고, 이후 단계에서 **GCP 위에 실제 서비스형 인프라를 구성하는 것**이 다음 확장 포인트입니다.

## 2. 왜 인프라 확장이 중요한가

이 프로젝트는 단순한 CRUD 웹앱이 아니라 아래 요소를 함께 담고 있습니다.

- 벡터 검색 기반 RAG
- 법률 답변 생성
- 모델 라우팅 가능성
- 시나리오 기반 검증
- 향후 민감도별 추론 경로 분리 가능성

그래서 클라우드 교육과정 관점에서는 "앱 하나를 올렸다"보다,

- managed service를 어디까지 쓰고
- 어떤 부분을 self-hosted로 가져가며
- 비용, 운영, 보안, 확장성을 어떻게 나눠 설계했는지

를 보여주는 쪽이 훨씬 포트폴리오 가치가 높습니다.

## 3. 현재 방향과 이후 확장 방향

현재 문서 기준으로는 아래 방향이 이미 정리되어 있습니다.

- 현재: Gemini API 기반 MVP
- 이후: GCP + Ollama 기반 Local LLM 확장 검토

즉, 지금은 **Vertex AI로 빠르게 MVP를 검증**했고, 이후에는 **GCP GPU 자원 위에 Local LLM을 올려 self-hosted inference 경로를 추가**하는 방향이 자연스럽습니다.

### 왜 AWS가 아니라 GCP인가

이 부분은 "AWS는 안 되고 GCP만 된다"는 의미가 아닙니다. AWS도 Amazon Bedrock, SageMaker, EC2 GPU, RDS PostgreSQL 등으로 유사한 구성이 가능합니다.

그럼에도 우리 팀이 GCP를 선택한 이유는 아래와 같습니다.

- 이 프로젝트는 단순 웹 배포보다 생성형 AI, 임베딩, RAG, 이후 GPU 기반 Local LLM 확장까지 포함하는 **AI 중심 프로젝트**입니다.
- 우리 팀은 `Vertex AI 기반 MVP -> GCP GPU 기반 Local LLM 확장`이라는 흐름이 더 단순하고 일관된 AI-first 확장 스토리라고 판단했습니다.
- 즉, GCP 선택의 핵심 이유는 AWS가 불가능해서가 아니라, **프로젝트의 학습 목표와 인프라 확장 방향을 더 자연스럽게 설명할 수 있기 때문**입니다.

정리하면:

- AWS도 충분히 가능한 선택지입니다.
- 다만 이 프로젝트에서는 `Gemini / Vertex AI -> GCP GPU / Ollama`로 이어지는 흐름이 더 명확해서 GCP를 선택했습니다.

### GCP와 AWS를 함께 쓰지 않는 이유

멀티클라우드 구성이 항상 나쁜 것은 아닙니다. 실제로 대규모 조직에서는 규제, 장애 대비, 특정 서비스 선택, 벤더 종속 완화 같은 이유로 GCP와 AWS를 함께 쓰기도 합니다.

하지만 현재 프로젝트 단계에서는 두 클라우드를 섞는 것보다 **하나의 클라우드로 통일하는 편이 더 적절**합니다.

이유는 아래와 같습니다.

- RAG API, PostgreSQL, 모델 호출, 이후 GPU 기반 Local LLM 확장까지 서비스 간 연결이 긴밀함
- 클라우드를 혼합하면 네트워크 홉이 늘고 지연 가능성이 커짐
- 인증, 권한, 비밀값, 로그, 모니터링 관리 포인트가 늘어남
- 교육과정 프로젝트와 포트폴리오 관점에서 아키텍처 설명이 불필요하게 복잡해짐

따라서 이 프로젝트는 멀티클라우드 실험보다, **단일 클라우드 기반의 일관된 AI 서비스 아키텍처를 구성하는 것**을 우선합니다.

### 강사님 방향과의 정합성: serverless-first 구성

강사님이 서버리스 방식을 강조한다면, 현재 프로젝트와 가장 잘 맞는 선택지는 **Cloud Run 중심의 serverless-first 아키텍처**입니다.

Google Cloud 공식 문서도 Cloud Run을 **fully managed, serverless** 플랫폼으로 설명합니다. 즉 서버를 직접 운영하지 않고도 컨테이너 기반 API와 이벤트 기반 서비스를 배포할 수 있습니다.

이 프로젝트에 맞춰 보면 아래 구성이 가장 자연스럽습니다.

- API 서버: `Cloud Run`
- 배치 작업: `Cloud Run Jobs`
- DB: `Cloud SQL for PostgreSQL`
- 비밀값: `Secret Manager`
- 파일/산출물 저장: `Cloud Storage`
- 오케스트레이션: `Workflows`
- 로그/모니터링: `Cloud Logging`, `Cloud Monitoring`
- managed AI: `Vertex AI`

이 구조의 장점은 다음과 같습니다.

- 현재 FastAPI 컨테이너 구조를 거의 그대로 살릴 수 있음
- 서버 운영보다 서비스 연결과 아키텍처 설계에 집중할 수 있음
- 교육과정 발표에서 "서버리스 기반 AI 서비스 아키텍처"로 설명하기 쉬움

다만 한 가지 예외는 **GPU 기반 Local LLM 확장**입니다.

- `Vertex AI`를 사용하는 현재 MVP와 서버리스 기반 API 계층은 Cloud Run 중심으로 충분히 설명 가능합니다.
- 하지만 `Ollama + Qwen` 같은 self-hosted Local LLM을 상시 구동하려면, 완전한 서버리스보다 `Compute Engine GPU VM`이 더 현실적일 수 있습니다.

따라서 현재 프로젝트의 권장 방향은 아래처럼 정리할 수 있습니다.

- **기본 방향:** serverless-first (`Cloud Run` 중심)
- **예외적 확장:** Local LLM이 꼭 필요할 때만 GPU VM 추가

즉, 발표에서는 "기본 아키텍처는 서버리스로 구성하고, 고비용 GPU 추론만 선택적으로 별도 계층으로 분리한다"는 방식으로 설명하는 것이 가장 자연스럽습니다.

## 4. 권장 인프라 확장 로드맵

### 4-1. 1단계: GCP managed baseline 구성

가장 먼저 추천하는 확장입니다. 사실상 **serverless-first baseline**에 해당합니다.

- backend API: `Cloud Run`
- frontend: `Cloud Run` 또는 정적 배포 구조
- DB: `Cloud SQL for PostgreSQL`
- 컨테이너 이미지 저장: `Artifact Registry`
- CI/CD: `Cloud Build`
- 비밀값 관리: `Secret Manager`
- 로그/모니터링: `Cloud Logging`, `Cloud Monitoring`

### 이 단계가 중요한 이유

- 로컬에서 돌던 RAG 앱을 GCP 서비스형 구조로 옮길 수 있음
- DB, 배포, 비밀값, 로그 관리까지 포함해 "실서비스형 기본기"를 보여줄 수 있음
- 이후 Local LLM을 붙이더라도 기반 서비스는 이미 managed로 안정화할 수 있음

### 포트폴리오 관점 장점

- `Cloud Run + Cloud SQL + Secret Manager + Cloud Build` 조합만으로도 완성도 높은 GCP 실전 구조를 설명할 수 있음
- 특히 현재 프로젝트의 PostgreSQL + pgvector 구조를 Cloud SQL로 옮기는 흐름은 RAG 서비스 포트폴리오로 설득력이 높음

## 4-2. 2단계: GCP GPU 기반 Local LLM 확장

이 프로젝트의 인프라 확장성에서 가장 중요한 축입니다.

### 목표

- 현재 Vertex AI에 의존하는 answer generation 일부를
- GCP GPU 환경에서 직접 운영하는 Local LLM으로 옮겨
- self-hosted inference 구조를 추가

### 권장 방향

- `Compute Engine GPU VM` 위에 `Ollama + Qwen 계열 모델` 배포
- backend에서 모델 라우팅
  - `HIGH / MEDIUM` 민감 작업: Local LLM 우선
  - `LOW` 민감 작업 또는 fallback: Vertex AI 사용

이 방향은 현재 저장소의 상위 규칙과도 맞습니다.

### 왜 이 구성이 좋은가

- 교육과정 관점에서 "managed AI API 사용"을 넘어서 "GPU inference 운영" 경험을 보여줄 수 있음
- 비용/보안/성능에 따라 모델 경로를 나누는 아키텍처를 설명할 수 있음
- 법률/노동권 도메인처럼 민감도가 있는 서비스에서 왜 Local LLM이 필요한지도 자연스럽게 설명 가능

### Compute Engine GPU를 우선 추천하는 이유

- 모델을 상시 올려두고 warm 상태를 유지하기 쉬움
- Ollama 같은 self-hosted inference 서버 운영 흐름을 설명하기 좋음
- 발표/시연 기준으로도 Cloud Run GPU보다 예측 가능한 운영 구성이 가능함

### 대안

- `Cloud Run GPU`

이 경로도 가능성이 있습니다. 다만 현재 프로젝트에서는 **self-hosted Local LLM을 안정적으로 보여주는 것**이 더 중요하므로, 1차 확장안으로는 `Compute Engine GPU + Ollama`가 더 적합하다고 판단합니다.

## 4-3. 3단계: 데이터 및 배치 파이프라인의 클라우드화

클라우드 포트폴리오로 더 강하게 만들려면, 추론 서비스만이 아니라 데이터 운영 파이프라인도 보여주는 것이 좋습니다.

추천 요소:

- 원본 파일 / 중간 산출물 저장: `Cloud Storage`
- 청킹 / 임베딩 / 검증 배치: `Cloud Run Jobs`
- 배치 순서 제어: `Workflows`
- 비동기 작업 분리: `Pub/Sub`

### 예시 흐름

1. 법령 source 또는 데이터 변경 발생
2. `Workflows`가 작업 순서를 orchestration
3. `Cloud Run Jobs`가 청킹 / ingestion / embedding 실행
4. 결과는 `Cloud SQL`과 `Cloud Storage`에 반영
5. 검증 결과를 로그 및 모니터링에 남김

이렇게 되면 프로젝트가 단순 앱이 아니라 **데이터 파이프라인이 포함된 클라우드 시스템**으로 보입니다.

## 4-4. 4단계: 운영성과 포트폴리오 완성도 보강

여기서부터는 "잘 돌아가는 서비스"를 넘어서 "운영 가능한 서비스"를 보여주는 단계입니다.

추천 요소:

- `Terraform`으로 인프라 코드화
- 서비스 계정 분리 및 최소 권한 IAM
- Secret Manager로 API 키 / DB 비밀번호 관리
- Cloud Logging / Monitoring 기반 지표, 로그, 알림 구성
- dev / prod 환경 분리

### 이 단계가 중요한 이유

- 클라우드 포트폴리오에서 IaC와 관측성은 완성도를 크게 높여줌
- "서비스를 띄울 수 있다"가 아니라 "재현 가능하게 운영할 수 있다"는 점을 보여줄 수 있음

## 5. 클라우드 포트폴리오로 보이게 만드는 핵심 포인트

### 1. Managed + Self-hosted를 함께 보여주기

- Vertex AI만 쓰면 편하지만 운영 설계의 깊이가 약해 보일 수 있음
- 반대로 전부 self-hosted로 가면 시간과 안정성 리스크가 큼
- 따라서
  - 기본 서비스는 managed
  - 민감 추론은 GPU 기반 Local LLM
  구조가 가장 설명력이 좋음

### 2. 단일 서버가 아니라 서비스 역할 분리를 보여주기

- API 서비스
- DB
- 모델 추론 서비스
- 배치 파이프라인
- 로그/모니터링

이렇게 역할이 분리되어야 클라우드 아키텍처 포트폴리오로 보입니다.

### 3. 운영 자동화를 일부라도 보여주기

- 수동 실행만 있는 구조보다
- Cloud Build, Workflows, Terraform 중 하나라도 실제로 연결되어 있으면 훨씬 강해집니다.

### 4. 비용과 보안을 설계 이유로 설명하기

- 왜 Vertex AI를 MVP에서 먼저 썼는지
- 왜 이후에는 Local LLM을 붙이려는지
- 왜 민감도에 따라 라우팅하려는지

이런 설명이 있으면 인프라 선택이 더 설득력 있어집니다.

## 6. 현재 프로젝트에 가장 적합한 추천 확장 순서

현실적으로는 아래 순서가 가장 좋습니다.

1. `Cloud Run + Cloud SQL + Secret Manager + Artifact Registry + Cloud Build`로 기본 배포 구조 완성
2. `Cloud SQL`로 PostgreSQL + pgvector 이전
3. `Compute Engine GPU + Ollama + Qwen` 기반 Local LLM 추론 서비스 추가
4. backend에서 민감도 기반 모델 라우팅 추가
5. `Cloud Logging / Monitoring`과 alerting 추가
6. 여유가 있으면 `Cloud Storage + Workflows + Cloud Run Jobs + Pub/Sub`로 데이터 파이프라인 자동화
7. 마지막으로 `Terraform`으로 인프라 코드화

## 7. 강사님께 검토받고 싶은 포인트

- 현재 프로젝트에서 Vertex AI 기반 MVP 이후 어떤 인프라 확장 단계를 우선하는 것이 가장 적절한지
- `Compute Engine GPU + Ollama`가 Local LLM 확장 1차안으로 적절한지
- `Cloud Run` 중심 managed 구조와 self-hosted GPU 추론 구조를 함께 가져가는 방식이 과하지 않은지
- 교육과정 포트폴리오 기준으로, 배치 파이프라인 자동화와 IaC 중 무엇을 더 우선해서 보여주는 것이 좋은지

## 참고 문서

- `docs/planning/01_model_strategy.md`
- `docs/planning/04_architecture.md`
- `docs/planning/09_backend_embedding_plan.md`
- `docs/planning/10_backend_retrieval_plan.md`
- `docs/ops/task6_answer_generation_status.md`

## 클라우드 참고 자료

- Cloud Run: https://docs.cloud.google.com/run/docs/overview/what-is-cloud-run
- Cloud Run GPU: https://docs.cloud.google.com/run/docs/configuring/services/gpu
- Compute Engine GPU: https://docs.cloud.google.com/compute/docs/gpus/about-gpus
- Cloud SQL for PostgreSQL: https://docs.cloud.google.com/sql/docs/postgres
- Cloud SQL PostgreSQL extensions (`pgvector` 포함): https://cloud.google.com/sql/docs/postgres/extensions
- Secret Manager: https://docs.cloud.google.com/secret-manager/docs/overview
- Artifact Registry: https://docs.cloud.google.com/artifact-registry/docs/repositories
- Cloud Build: https://cloud.google.com/build/docs
- Workflows: https://docs.cloud.google.com/workflows/docs/overview
- Pub/Sub: https://docs.cloud.google.com/pubsub/docs/pubsub-basics
- Cloud Monitoring: https://docs.cloud.google.com/monitoring/docs/monitoring-overview
- Terraform on Google Cloud: https://docs.cloud.google.com/docs/terraform/terraform-overview
