# Option 4 Architecture Draft

작성일: `2026-04-17`

상태 메모: 현재 구현 완료 범위는 로컬 SCN-004 frontend/backend demo이며, 이 문서는 option 4를 적용할 경우의 후속 클라우드 아키텍처 초안이다.

업데이트 메모: 2026-04-20 기준 로컬 MVP는 SCN-004-DEMO-FREEZE, SCN-001-BRIDGE-DEMO answer-only, preflight, full 60 answer evidence report까지 정리됐다. 이 문서는 후속 클라우드 아키텍처 초안으로 유지한다.

## 문서 목적

- `4안: 모듈화된 모놀리스 + serverless-first + LLM 서버 분리` 구조를 강사님께 한눈에 설명하기 위한 아키텍처 초안
- `05_architecture_options.md`, `06_option3_option4_detail.md`에서 설명한 내용을 실제 배포 구조와 요청 흐름 관점에서 시각적으로 정리

## 1. 4안 한 줄 요약

기본 서비스는 `Cloud Run` 중심의 managed / serverless 구조로 유지하고, GPU가 필요한 Local LLM 추론 계층만 `Compute Engine GPU VM`으로 별도 분리하는 구조입니다.

## 2. 아키텍처 다이어그램

```text
┌───────────────────────────────────────────────────────────────────┐
│                           User / Browser                         │
└───────────────────────────────┬───────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│ Frontend                                                          │
│ - Managed hosting 또는 Cloud Run                                  │
│ - 사용자 입력 / 결과 화면 / 시나리오 데모                         │
└───────────────────────────────┬───────────────────────────────────┘
                                │ HTTPS
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│ Backend API (Cloud Run)                                           │
│ - FastAPI                                                         │
│ - retrieval                                                      │
│ - grounded answer orchestration                                  │
│ - document draft                                                  │
│ - citation 검증                                                  │
│ - 모델 경로 라우팅                                                │
└───────────────┬───────────────────────────────┬───────────────────┘
                │                               │
                │ SQL / Vector Search           │ Model Routing
                ▼                               ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│ Cloud SQL for PostgreSQL      │   │ Vertex AI                     │
│ - pgvector                    │   │ - managed model path          │
│ - law_chunks                  │   │ - Gemini API                  │
└───────────────────────────────┘   └───────────────────────────────┘
                                                │
                                                │ fallback / low-risk path
                                                │
                                                ▼
                                 ┌──────────────────────────────────┐
                                 │ Local LLM Server                 │
                                 │ Compute Engine GPU VM            │
                                 │ - Ollama + Qwen                  │
                                 │ - warm 상태 유지                 │
                                 │ - self-hosted inference          │
                                 └──────────────────────────────────┘

부가 계층:
- Secret Manager: API 키 / DB 비밀값 관리
- Cloud Storage: 파일 / 산출물 / 중간 결과 저장
- Cloud Run Jobs: 배치 작업
- Workflows: 작업 오케스트레이션
- Cloud Logging / Monitoring: 로그 / 모니터링 / 운영 확인
```

## 3. 요청 흐름

### 3-1. 기본 경로

1. 사용자가 frontend에서 질문을 입력합니다.
2. frontend가 backend API(`Cloud Run`)를 호출합니다.
3. backend는 질문을 정리하고 `Cloud SQL + pgvector`에서 법령 retrieval을 수행합니다.
4. backend는 검색 결과와 내부 정책을 바탕으로 답변 생성 경로를 결정합니다.
5. 기본 경로에서는 `Vertex AI`를 호출합니다.
6. backend는 응답을 검증하고 `cited_articles`를 정리합니다.
7. 최종 응답을 frontend로 반환합니다.

### 3-2. Local LLM 경로

1. backend가 질문 민감도 또는 작업 성격상 self-hosted 경로가 적합하다고 판단합니다.
2. backend가 GPU VM 위의 `Ollama + Qwen` 서버를 호출합니다.
3. Local LLM이 답변 초안을 생성합니다.
4. backend가 결과를 받아 citation 규칙과 응답 구조를 다시 검증합니다.
5. 최종 응답을 frontend로 반환합니다.

즉, 사용자는 항상 backend만 호출하고, `Vertex AI`와 `Local LLM Server`는 backend 뒤에 숨겨진 내부 추론 계층으로 동작합니다.

## 4. 계층별 역할

| 계층 | 역할 |
|---|---|
| Frontend | 사용자 입력, 결과 출력, 데모 시나리오 UI |
| Backend API (`Cloud Run`) | retrieval, orchestration, citation 검증, 모델 라우팅 |
| Cloud SQL | 법령 chunk 저장, pgvector 검색 |
| Vertex AI | 기본 managed 모델 경로 |
| Compute Engine GPU VM | Local LLM self-hosted 추론 |
| Secret Manager | 인증정보 및 비밀값 관리 |
| Cloud Storage | 파일 및 산출물 저장 |
| Cloud Run Jobs / Workflows | 배치 작업 및 파이프라인 orchestration |
| Logging / Monitoring | 운영 로그, 장애 확인, 데모 안정성 점검 |

## 5. 왜 이 구조가 4안인가

이 구조는 MSA처럼 모든 기능을 서비스로 쪼갠 것이 아닙니다.

- backend는 여전히 하나의 서비스 안에서 동작
- retrieval, answer, validation 로직은 backend 내부에 유지
- 단지 GPU와 warm 상태 유지가 중요한 Local LLM 계층만 별도 서버로 분리

즉, `4안`은 "전체 분산 시스템"이 아니라, **기본은 단순하게 유지하고 자원 특성이 다른 LLM 계층만 선택적으로 분리한 구조**입니다.

## 6. 이 구조의 장점

- `Cloud Run` 기반 serverless-first 구조를 유지할 수 있음
- Local LLM이 필요할 때만 GPU 서버를 별도 계층으로 붙일 수 있음
- `Vertex AI`와 `Ollama + Qwen`을 병행하는 모델 라우팅 구조를 설명하기 좋음
- 법률/노동권 도메인에서 민감도별 추론 경로 분리 논리를 보여줄 수 있음
- 클라우드 포트폴리오 관점에서 managed + self-hosted 구성을 함께 설명할 수 있음

## 7. 이 구조의 주의점

- `Cloud Run`과 GPU VM을 함께 운영해야 하므로 baseline보다 운영 포인트가 늘어남
- backend와 Local LLM 서버 사이 timeout, retry, health check가 필요함
- 너무 이른 시점에 전면 도입하면 현재 MVP보다 인프라 설명이 더 커 보일 수 있음

## 8. 강사님께 검토받고 싶은 포인트

- `4안`처럼 LLM 서버만 별도 분리하는 방식이 실무적으로 자연스러운지
- baseline은 `3안`으로 두고, `4안`은 후속 확장안으로 설명하는 방식이 적절한지
- Local LLM 계층을 실제로 보여줄 경우 `Compute Engine GPU VM`이 1차안으로 적절한지

## 참고 연결 문서

- `docs/presentation/04_infrastructure_expansion.md`
- `docs/presentation/05_architecture_options.md`
- `docs/presentation/06_option3_option4_detail.md`
