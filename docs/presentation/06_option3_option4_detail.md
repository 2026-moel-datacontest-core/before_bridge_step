# Detailed Explanation Of Option 3 And 4

작성일: `2026-04-16`

## 문서 목적

- `05_architecture_options.md`에서 비교한 4가지 안 중, 실제 선택 가능성이 높은 `3안`과 `4안`을 별도로 자세히 설명하기 위한 문서
- 강사님께 단순 비교표가 아니라 "이 구조가 실제로 어떻게 돌아가는지"까지 검토받기 위한 문서

## 1. 왜 3안과 4안을 따로 보는가

현재 프로젝트 기준으로 실질적인 선택지는 아래 두 가지입니다.

- `3안`: 모듈화된 모놀리스 + serverless-first
- `4안`: 모듈화된 모놀리스 + serverless-first + LLM 서버 분리

이유는 다음과 같습니다.

- `1안` 단순 모놀리스는 현재 MVP 검증에는 적합하지만, 클라우드 교육과정 프로젝트로 확장했을 때 설명력이 다소 약할 수 있음
- `2안` MSA는 현재 팀 규모와 MVP 단계에 비해 운영 복잡도가 너무 큼
- 따라서 실제 논의 대상은 "기본 serverless-first로 갈 것인가", "아니면 Local LLM까지 고려해 LLM 서버만 별도 분리할 것인가"에 가깝습니다.

## 2. 3안: 모듈화된 모놀리스 + serverless-first

### 2-1. 핵심 개념

이 안은 backend를 여러 서비스로 쪼개지 않고 하나의 backend 애플리케이션으로 유지하되, 인프라 배포는 managed cloud 기반으로 가져가는 구조입니다.

즉,

- 애플리케이션 구조는 단일 backend
- 인프라 구조는 `Cloud Run` 중심 serverless-first

형태입니다.

### 2-2. 구성 요소

- frontend: managed hosting 또는 `Cloud Run`
- backend API: `Cloud Run`
- DB: `Cloud SQL for PostgreSQL`
- 비밀값: `Secret Manager`
- 파일/산출물: `Cloud Storage`
- 배치 작업: `Cloud Run Jobs`
- 오케스트레이션: `Workflows`
- 로그/모니터링: `Cloud Logging`, `Cloud Monitoring`
- managed AI: `Vertex AI`

### 2-3. 구조를 그림처럼 보면

```text
사용자
  -> Frontend
  -> Backend API (Cloud Run)
      -> PostgreSQL + pgvector (Cloud SQL)
      -> Vertex AI
      -> Cloud Storage / Cloud Run Jobs / Workflows
  -> 응답 반환
```

### 2-4. 실제 요청 흐름

1. 사용자가 frontend에서 질문을 입력합니다.
2. frontend가 backend API를 호출합니다.
3. backend는 질문을 정리하고 retrieval을 수행합니다.
4. backend는 검색된 법령 context를 바탕으로 `Vertex AI`를 호출합니다.
5. backend는 응답을 검증하고 `cited_articles`를 정리합니다.
6. 최종 응답을 사용자에게 반환합니다.

즉, 모든 핵심 로직은 backend 안에서 이루어지고, 외부 AI 호출은 managed AI 서비스인 `Vertex AI`를 사용합니다.

### 2-5. 이 안의 장점

- 현재 FastAPI 구조를 거의 그대로 유지할 수 있음
- 2인 팀 기준으로 운영 포인트가 과도하게 늘어나지 않음
- 강사님이 말씀하신 `serverless-first` 방향과 정합성이 높음
- Cloud Run의 scale-to-zero 특성을 활용해 초기 MVP 단계의 유휴 비용을 줄이기 쉬움
- `Cloud SQL`, `Secret Manager`, `Cloud Logging` 등을 사용해 self-managed server보다 운영 부담을 줄일 수 있음

### 2-6. 이 안의 한계

- Local LLM을 실제로 운영하려는 순간 구조 설명이 약해질 수 있음
- GPU, warm state, self-hosted inference가 필요한 경우 `Cloud Run + Vertex AI`만으로는 한계가 있음
- 민감도 기반 모델 라우팅을 아키텍처적으로 보여주기 어렵다

### 2-7. 언제 적합한가

- 지금 당장 클라우드로 옮겨야 할 때
- Local LLM이 아직 실제 구현 범위 밖일 때
- 발표와 데모의 중심이 grounded answer와 시나리오 안정성일 때

## 3. 4안: 모듈화된 모놀리스 + serverless-first + LLM 서버 분리

### 3-1. 핵심 개념

이 안은 `3안`을 baseline으로 유지하면서, GPU가 필요한 Local LLM 계층만 별도 서버로 분리하는 구조입니다.

즉,

- 기본 서비스는 managed / serverless
- LLM 추론 계층만 selective split

구조입니다.

### 3-2. 구성 요소

#### 기본 계층

- frontend: managed hosting 또는 `Cloud Run`
- backend API: `Cloud Run`
- DB: `Cloud SQL for PostgreSQL`
- 비밀값: `Secret Manager`
- 파일/산출물: `Cloud Storage`
- 배치 작업: `Cloud Run Jobs`
- 오케스트레이션: `Workflows`
- 로그/모니터링: `Cloud Logging`, `Cloud Monitoring`
- managed AI: `Vertex AI`

#### 추가 계층

- `Compute Engine GPU VM`
- `Ollama + Qwen` 기반 Local LLM
- backend 내부 라우팅 로직

### 3-3. 구조를 그림처럼 보면

```text
사용자
  -> Frontend
  -> Backend API (Cloud Run)
      -> PostgreSQL + pgvector (Cloud SQL)
      -> (A) Vertex AI
      -> (B) Local LLM Server (Compute Engine GPU VM + Ollama + Qwen)
      -> Cloud Storage / Cloud Run Jobs / Workflows
  -> 응답 반환
```

핵심은 사용자가 Local LLM 서버를 직접 호출하지 않는다는 점입니다.  
항상 backend가 가운데서 retrieval, validation, routing을 담당합니다.

### 3-4. 실제 요청 흐름

#### 경로 A: Managed path

1. 사용자가 질문을 입력합니다.
2. backend가 retrieval을 수행합니다.
3. backend가 일반 질의 또는 managed 경로에 적합하다고 판단합니다.
4. `Vertex AI`를 호출합니다.
5. 응답을 검증하고 반환합니다.

#### 경로 B: Local path

1. 사용자가 질문을 입력합니다.
2. backend가 retrieval을 수행합니다.
3. backend가 민감도 또는 작업 성격상 Local LLM 경로가 적합하다고 판단합니다.
4. GPU VM 위의 `Ollama + Qwen`을 호출합니다.
5. 응답을 검증하고 반환합니다.

즉, `4안`은 retrieval 구조를 바꾸는 안이 아니라, **생성 모델 경로를 두 갈래로 나누는 안**입니다.

### 3-5. 왜 LLM 서버만 따로 떼는가

API 계층과 LLM 계층은 자원 특성이 다릅니다.

- API 계층: 요청 기반 확장, scale-to-zero에 유리
- Local LLM 계층: GPU 필요, 모델 메모리 상주 필요, warm 상태 유지가 중요

이 둘을 같은 서비스로 두면 효율이 떨어질 수 있습니다.  
그래서 전체를 MSA로 쪼개는 대신, **GPU 추론 계층만 별도로 떼는 것**이 실무적으로 더 자연스럽습니다.

### 3-6. 이 안의 장점

- `3안`의 단순함을 유지하면서 Local LLM 구조까지 설명 가능
- `Cloud Run`과 GPU VM의 장점을 동시에 가져갈 수 있음
- 법률/노동권 도메인에서 민감도 기반 모델 라우팅을 설명하기 좋음
- GPU 추론처럼 자원 요구가 큰 계층만 분리하므로, MSA보다 운영 복잡도가 훨씬 낮음

### 3-7. 이 안의 단점

- `Cloud Run`과 GPU VM을 함께 관리해야 함
- backend와 LLM 서버 사이의 통신, timeout, fallback, health check가 필요함
- 너무 이른 시점에 도입하면 현재 MVP보다 인프라 설명이 더 커 보일 수 있음

### 3-8. 언제 적합한가

- Local LLM을 실제로 데모하거나 운영할 계획이 있을 때
- Vertex AI와 self-hosted LLM을 함께 보여주고 싶을 때
- 클라우드 포트폴리오에서 "managed + self-hosted" 구조를 보여주고 싶을 때

## 4. 3안과 4안의 차이

| 항목 | 3안 | 4안 |
|---|---|---|
| 기본 API/DB 구조 | 동일 | 동일 |
| managed cloud 활용 | 높음 | 높음 |
| Local LLM 운영 | 없음 | 있음 |
| GPU 계층 설명력 | 약함 | 강함 |
| 운영 복잡도 | 더 낮음 | 조금 더 높음 |
| 현재 MVP 적합성 | 매우 높음 | 높음 |
| 장기 확장성 | 보통 | 높음 |

## 5. 현재 추천 해석

현재 프로젝트 기준으로는 아래처럼 이해하는 것이 가장 자연스럽습니다.

- 지금 당장 설명할 baseline: `3안`
- 이후 Local LLM을 실제로 붙일 때의 확장안: `4안`

즉, `4안`은 `3안`을 부정하는 별도 방향이 아니라, **3안 위에 GPU 추론 계층만 추가하는 확장 구조**입니다.

## 6. 원래 인프라 계획과의 비교

기존 인프라 문서(`04_infrastructure_expansion.md`)에서 원래 계획했던 방향은 아래와 같았습니다.

- **기본 방향:** `Cloud Run` 중심 serverless-first
- **예외적 확장:** Local LLM이 꼭 필요할 때만 `Compute Engine GPU VM` 추가

즉, 원래 인프라 계획은 사실상 아래와 같이 해석할 수 있습니다.

- `04` 문서의 **1단계 managed baseline** = `3안`
- `04` 문서의 **2단계 GPU Local LLM 확장** = `4안`

따라서 원래 계획은 별도의 완전히 다른 인프라안이 아니라,

- 먼저 `3안`으로 baseline을 만들고
- 이후 필요 시 `4안`으로 확장하는 단계형 로드맵

에 가까웠습니다.

### 왜 이렇게 해석하는가

`04_infrastructure_expansion.md`에서는 아래처럼 정리되어 있습니다.

- 기본은 `Cloud Run` 중심 serverless-first [04_infrastructure_expansion.md](/home/jongwon/personal_project/law_main_road/docs/presentation/04_infrastructure_expansion.md:112)
- Local LLM이 필요할 때만 GPU VM 추가 [04_infrastructure_expansion.md](/home/jongwon/personal_project/law_main_road/docs/presentation/04_infrastructure_expansion.md:113)
- 1단계는 `Cloud Run + Cloud SQL + Secret Manager + Cloud Build` 중심 baseline [04_infrastructure_expansion.md](/home/jongwon/personal_project/law_main_road/docs/presentation/04_infrastructure_expansion.md:119)
- 2단계는 `Compute Engine GPU + Ollama + Qwen` 기반 Local LLM 확장 [04_infrastructure_expansion.md](/home/jongwon/personal_project/law_main_road/docs/presentation/04_infrastructure_expansion.md:142)

즉, `06` 문서의 `3안`, `4안`은 기존 인프라 계획을 다시 구조 선택 관점에서 풀어쓴 버전이라고 보면 됩니다.

### 한 줄 정리

- 원래 인프라 계획의 출발점은 `3안`
- 원래 인프라 계획의 확장 방향은 `4안`

즉, **원래 계획 = `3안 baseline + 4안 확장`** 으로 보는 것이 가장 정확합니다.

## 7. 강사님께 검토받고 싶은 포인트

- baseline을 `3안`으로 설명하는 것이 적절한지
- Local LLM이 실제 필요해질 경우 `4안`처럼 LLM 서버만 별도 분리하는 방식이 가장 자연스러운지
- 발표에서는 `3안`을 현재 선택안, `4안`을 후속 확장안으로 설명하는 구성이 적절한지

## 참고 연결 문서

- `docs/presentation/04_infrastructure_expansion.md`
- `docs/presentation/05_architecture_options.md`
