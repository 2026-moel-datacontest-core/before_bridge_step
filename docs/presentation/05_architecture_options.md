# Architecture Options For Instructor Review

작성일: `2026-04-17`

업데이트 메모: 이 문서는 2026-04-17 architecture option 검토 초안으로 보존한다. 2026-04-21 기준 MVP는 SCN-004 demo freeze, presentation-local presets, demo preflight, full 60 answer evidence report, `before` DB source/cache 전환까지 정리된 상태이며, 배포/인프라 판단 전 최신 운영 기준은 `docs/ops/README.md`를 우선한다.

## 문서 목적

- 현재 프로젝트를 어떤 시스템 구조로 설명하고 확장하는 것이 가장 적절한지 강사님께 검토받기 위한 비교 문서
- 단순히 기술 이름을 나열하는 것이 아니라, 팀 규모, 현재 MVP 상태, 운영 복잡도, 클라우드 활용 방식까지 함께 고려해 정리

## 1. 현재 판단의 전제

현재 프로젝트는 아래 전제를 기준으로 구조를 판단해야 합니다.

- 2인 팀 프로젝트
- 현재 저장소 구현은 `After` 중심
- backend는 FastAPI 기반
- database는 PostgreSQL + pgvector
- retrieval / grounded answer MVP 확보
- SCN-004 document draft API 확보
- SCN-004 frontend demo 확보
- 현재는 로컬 MVP 단계이며, 이후 GCP 기반 서비스형 인프라 확장 검토 중

즉, 지금의 핵심 과제는 대규모 분산 시스템 설계 자체가 아니라, 이미 검증한 MVP를 어떻게 안정적이고 설득력 있는 구조로 확장할 것인가에 가깝습니다.

## 2. 비교 대상

이번 문서에서는 아래 4가지를 비교합니다.

1. 모놀리스 방식
2. MSA(Microservices Architecture) 방식
3. 모듈화된 모놀리스 + serverless-first
4. 모듈화된 모놀리스 + serverless-first + LLM 서버 분리

## 3. 모놀리스 방식

### 개념

모놀리스는 하나의 backend 애플리케이션 안에 주요 기능을 함께 두는 구조입니다. retrieval, answer generation, Before/After 로직, API route가 하나의 서비스 안에 같이 들어가는 형태입니다.

### 장점

- 구조가 단순해 구현과 배포가 빠름
- 팀 규모가 작을 때 의사소통 비용이 적음
- 로컬 개발과 디버깅이 쉬움
- 초기 MVP 검증 단계에서 가장 현실적임

### 단점

- 기능이 계속 늘어나면 코드베이스가 비대해질 수 있음
- 특정 기능만 독립적으로 확장하기 어려움
- GPU 추론, OCR 배치, 데이터 파이프라인처럼 성격이 다른 기능을 한 덩어리로 운영하게 될 수 있음

### 우리 프로젝트에 적용했을 때

현재 backend는 사실상 모놀리스에 가까운 구조입니다. retrieval과 grounded answer를 빠르게 검증하는 데에는 이 방식이 적절했습니다. 다만 이후 Local LLM 추론, OCR, 배치 파이프라인까지 한 애플리케이션에 모두 넣으면 확장성이 떨어질 가능성이 있습니다.

## 4. MSA 방식

### 개념

MSA는 하나의 큰 애플리케이션을 여러 개의 독립 서비스로 나누는 구조입니다. 예를 들어 `retrieval service`, `answer service`, `OCR service`, `GPU inference service`, `batch pipeline service`처럼 기능별로 분리해 각각 배포하고 운영합니다.

### 장점

- 기능별 독립 배포가 가능함
- 서비스별로 다른 확장 전략을 적용할 수 있음
- GPU 추론처럼 특정 자원 요구가 큰 기능을 별도 서비스로 분리하기 좋음
- 장기적으로 팀이 커지면 역할 분담이 명확해질 수 있음

### 단점

- 작은 팀에는 운영 복잡도가 매우 큼
- 서비스 간 인증, API contract, 로그 추적, 장애 분석이 어려워짐
- 잘못 설계하면 "분산 모놀리스"가 되어 복잡도만 증가함
- 현재 프로젝트 단계에서는 구현 이점보다 운영 부담이 더 클 가능성이 높음

### 우리 프로젝트에 적용했을 때

2인 팀 기준으로는 지금 당장 MSA를 도입하는 것은 과한 선택으로 보입니다. 특히 현재 핵심 과제가 기능 분산이 아니라 시나리오 안정성, grounded answer 품질, 발표용 구조 정리인 점을 고려하면, MSA는 기술적 완성도보다 운영 복잡도를 먼저 키울 가능성이 큽니다.

## 5. 모듈화된 모놀리스 + serverless-first

### 개념

이 안은 backend를 당장 여러 마이크로서비스로 쪼개지 않고, 하나의 backend 안에서 모듈 경계를 분명히 유지하는 방식입니다. 인프라 측면에서는 `Cloud Run` 중심의 serverless-first 구조를 사용합니다.

즉,

- 애플리케이션 구조는 "모듈화된 모놀리스"
- 인프라 구조는 "managed cloud 중심"

으로 보는 것이 맞습니다.

### 추천 구성

- frontend: managed hosting 또는 `Cloud Run`
- backend API: `Cloud Run`
- database: `Cloud SQL for PostgreSQL`
- secret: `Secret Manager`
- 파일/산출물: `Cloud Storage`
- 배치: `Cloud Run Jobs`
- 오케스트레이션: `Workflows`
- 로그/모니터링: `Cloud Logging`, `Cloud Monitoring`
- managed AI: `Vertex AI`

### 장점

- 현재 팀 규모와 MVP 단계에 가장 잘 맞음
- 직접 서버를 운영하는 부담을 줄일 수 있음
- 강사님이 강조하신 `serverless-first` 방향과도 잘 맞음
- 클라우드 교육과정 포트폴리오로 설명하기에도 자연스러움
- 현재 FastAPI 중심 구조를 거의 그대로 살릴 수 있음

### 단점

- GPU 기반 Local LLM이 필요해지면 결국 별도 계층이 필요함
- 아주 큰 규모의 분산 시스템처럼 보이지는 않음
- 향후 기능이 크게 늘어나면 일부 영역은 결국 서비스 분리가 필요할 수 있음

### 우리 프로젝트에 적용했을 때

지금 당장 서비스형 인프라로 옮긴다면 가장 깔끔한 baseline입니다. 다만 Local LLM을 실제로 운영하려는 시점이 오면, 이 구조만으로는 GPU 추론 계층을 충분히 설명하기 어렵습니다.

## 6. 모듈화된 모놀리스 + serverless-first + LLM 서버 분리

### 개념

이 안은 현재 팀이 실제로 생각하고 있는 구조에 가장 가깝습니다. 기본 backend는 계속 모듈화된 모놀리스로 유지하되, GPU와 warm 상태 유지가 중요한 Local LLM 계층만 별도 서버로 분리하는 방식입니다.

즉,

- 기본 서비스는 managed / serverless
- GPU 추론만 selective split

구조입니다.

### 현재 팀이 생각한 구체 구성

#### 1단계: serverless-first baseline

- frontend: managed hosting 또는 `Cloud Run`
- backend API: `Cloud Run`
- DB: `Cloud SQL for PostgreSQL`
- 비밀값: `Secret Manager`
- 파일/산출물: `Cloud Storage`
- 배치 작업: `Cloud Run Jobs`
- 오케스트레이션: `Workflows`
- 로그/모니터링: `Cloud Logging`, `Cloud Monitoring`
- managed AI: `Vertex AI`

#### 2단계: 선택적 LLM 서버 분리

- `Compute Engine GPU VM`
- `Ollama + Qwen` 기반 Local LLM
- backend에서 작업 민감도와 성격에 따라 `Vertex AI`와 Local LLM을 라우팅

### 장점

- 현재 팀 규모와 MVP 단계에 맞으면서도, Local LLM 운영 구조까지 설명 가능
- `Cloud Run`의 장점과 GPU VM의 장점을 동시에 가져갈 수 있음
- 법률/노동권 도메인에서 민감도에 따라 모델 경로를 나누는 구조를 설명하기 좋음
- GPU 추론처럼 자원 특성이 다른 계층만 따로 떼어내므로 과도한 MSA보다 현실적임

### 단점

- 완전한 serverless-only 구조는 아님
- `Cloud Run`과 GPU VM을 함께 관리해야 해서 운영 포인트가 baseline보다 조금 늘어남
- 너무 이른 시점에 도입하면 현재 MVP 범위보다 인프라 설명이 더 커 보일 수 있음

### 우리 프로젝트에 적용했을 때

현재 인프라 문서와 가장 잘 맞는 실제 선택안입니다. 다만 이 안도 "지금 당장 전체 구현"이라기보다, `Cloud Run` baseline 위에 필요할 때만 LLM 서버를 추가하는 확장 전략으로 설명하는 것이 맞습니다.

## 7. 4가지 방식 비교

| 항목 | 모놀리스 | MSA | 모듈화된 모놀리스 + serverless-first | 모듈화된 모놀리스 + serverless-first + LLM 서버 분리 |
|---|---|---|---|---|
| 팀 규모 적합성 | 높음 | 낮음 | 높음 | 높음 |
| 초기 구현 속도 | 높음 | 낮음 | 높음 | 중간 |
| 운영 복잡도 | 낮음 | 매우 높음 | 중간 | 중간 이상 |
| 발표/설명 난이도 | 쉬움 | 어려움 | 비교적 쉬움 | 비교적 쉬움 |
| 클라우드 포트폴리오 적합성 | 보통 | 높지만 과할 수 있음 | 높음 | 매우 높음 |
| GPU 추론 확장성 | 낮음 | 높음 | 보통 | 높음 |
| 현재 프로젝트 단계 적합성 | 높음 | 낮음 | 매우 높음 | 높음 |
| Local LLM 운영 설명력 | 낮음 | 높음 | 보통 | 매우 높음 |

## 8. 현재 판단

현재 프로젝트를 설명할 때는 아래처럼 구분하는 것이 가장 자연스럽다고 판단합니다.

- **지금 기준 baseline:** `모듈화된 모놀리스 + serverless-first`
- **확장 기준 선택안:** `모듈화된 모놀리스 + serverless-first + LLM 서버 분리`

즉, 처음부터 MSA로 가는 것보다,

- backend는 하나의 서비스 안에서 모듈 경계를 유지하고
- 기본 배포는 `Cloud Run` 중심 managed 구조로 가져가며
- Local LLM이 실제로 필요할 때만 GPU 서버를 별도 계층으로 추가

하는 방식이 가장 현실적입니다.

그 이유는 다음과 같습니다.

- 2인 팀 기준으로 MSA는 운영 포인트가 너무 많음
- 현재 핵심 과제는 서비스 분해보다 RAG 품질과 시연 안정성 확보임
- `Cloud Run + Cloud SQL + Secret Manager` 구조는 self-managed server보다 운영 부담을 줄이면서도 실제 서비스형 구조를 설명하기 좋음
- GPU 계층만 분리하면 Local LLM 운영 필요성과 클라우드 선택 이유를 동시에 설명할 수 있음

## 9. 강사님께 검토받고 싶은 포인트

- 현재 프로젝트 단계와 팀 규모를 고려했을 때, 처음부터 MSA를 설명하는 것이 과한지
- baseline을 `모듈화된 모놀리스 + serverless-first`로 잡는 것이 적절한지
- Local LLM 확장 시 `LLM 서버만 별도 분리`하는 안이 실무적으로 가장 자연스러운지
- 발표에서는 4가지 안을 모두 비교하되, 실제 선택은 `3안 -> 4안 확장` 흐름으로 설명하는 구성이 괜찮은지
- 이후 확장 단계에서 가장 먼저 분리할 계층을 `GPU inference`, `OCR/문서 처리`, `배치 파이프라인` 중 어디로 보는 것이 좋은지

## 참고 연결 문서

- `docs/presentation/02_plan.md`
- `docs/presentation/03_team_role.md`
- `docs/presentation/04_infrastructure_expansion.md`
