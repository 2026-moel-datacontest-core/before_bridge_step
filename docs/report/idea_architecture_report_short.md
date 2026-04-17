# K-Labor Shield 아이디어·아키텍처 요약 보고서

작성일: `2026-04-17`

기준선:

- 서비스 corpus 기준일: `selected_as_of = 2026-04-11`
- RAG 및 시나리오 상태 기준일: `2026-04-17`
- frontend 구현 상태 기준일: `2026-04-17`

## 1. 프로젝트 개요

`law-main-road`는 계약 단계 위험 탐지와 분쟁 발생 후 대응 가이드를 하나의 흐름으로 연결하는 근거 기반 노동권 보호 AI입니다. 단순 법령 Q&A가 아니라, 사용자의 실제 상황을 입력받아 관련 조문을 검색하고 검색된 근거 위에서만 답변과 다음 행동을 제시하는 구조를 목표로 합니다.

이 서비스는 일반 사용자도 사용할 수 있지만, 외국인 근로자, 장애인 근로자, 사회초년생, 비정형 노동자처럼 정보 접근성이 낮은 사용자에게 더 유용한 구조를 지향합니다.

## 2. 문제 정의

많은 사용자가 근로계약, 해고, 체불, 육아휴직, 가족돌봄휴가 같은 노동 문제를 겪어도 관련 법과 절차를 바로 이해하기 어렵습니다. 사용자는 법 조문 원문 자체보다, “지금 내 상황에서 어떤 권리가 있고 무엇을 먼저 해야 하는지”를 빠르게 알고 싶어 합니다.

또한 일반적인 생성형 AI는 검색 결과에 없는 조문을 섞어 말할 위험이 있어, 노동권 안내 서비스로 쓰기에는 신뢰 문제가 있습니다. 본 프로젝트는 정보 취약성과 환각 위험을 동시에 줄이는 것을 핵심 과제로 삼고 있습니다.

## 3. 서비스 구조

프로젝트의 기본 구조는 `Before -> Bridge -> After` 흐름입니다.

- `Before`: 계약서 또는 OCR 결과를 입력받아 누락, 불명확, 주의 필요, 위법 가능성 신호를 탐지
- `Bridge`: 계약 단계에서 발견된 위험을 이후 분쟁 상황과 연결
- `After`: 해고, 체불, 휴직 거절 등 분쟁 상황을 자유 서술로 입력받아 관련 조문과 대응 순서를 안내
- `Recovery`: 후속 문서 작성 및 회복 지원 단계로, 현재 MVP 핵심 범위는 아님

차별점은 계약 단계와 분쟁 단계를 하나의 서비스 흐름으로 연결한다는 점, 다양한 노동권 시나리오를 다룬다는 점, 그리고 검색 결과와 grounded context에 없는 조문을 명시적으로 인용하면 검증 단계에서 실패 처리되도록 설계했다는 점입니다.

## 4. 현재 구현 수준

### 공통 기반

- `backend/data/law_chunks/all_chunks.json` 기준 `1722` chunks 고정
- PostgreSQL `law_chunks` `1722`건, embedding `1722 / 1722` 완료
- `POST /api/v1/retrieve` 구현 완료
- retrieval eval `hit@5 = 60/60 (100.00%)`
- eval runner, scenario smoke, citation 검증 구조 확보

### After 단계

- `POST /api/v1/answer` 구현 완료
- `citation_grounding_clean = 60/60`
- 검색 결과에 없는 조문 인용 금지, `cited_articles` 포함 응답 구조 고정
- `SCN-001`, `SCN-004`, `SCN-005` After 핵심 데모 안정화
- `POST /api/v1/documents/draft` 구현 완료
- SCN-004 노동청 진정서 / 노동위원회 이유서 초안 생성 구현 완료
- Next.js frontend에서 `/after -> /after/result -> /after/intake -> /after/draft` 흐름 구현 완료
- copy / print 구현 완료, sessionStorage backup/restore는 데모 안정성 때문에 보류

### Before 단계

- Phase A(표준 항목 매핑) 및 Phase B(OCR -> 비교 -> 검증 -> LLM) 구조 설계와 코드 초안이 정리되어 있습니다.
- 계약서 이미지 2-Layer OCR 테스트와 JSON 구조화 포맷 치환을 확인했습니다.
- `rule_validator.py`, `section_comparator.py` 중심의 deterministic 검증 초안과 T-0 ~ T-7 테스트 파이프라인이 준비되어 있습니다.

## 5. 대표 시나리오와 데모 전략

주요 시나리오는 다음과 같습니다.

- `SCN-001`: 외국인 계약서·기숙사·차별·사업장 변경 (`Full`)
- `SCN-004`: 카톡 해고 및 임금·퇴직금 체불 (`After`)
- `SCN-005`: 육아휴직 및 가족돌봄휴가 거절 (`After`)
- `SCN-003`: 장애인 편의제공 및 지원 제도 안내 (`Before`)
- `SCN-002`: 최저임금/수습 꼼수 (`Before`, partial)

현재 실제 frontend main demo는 `SCN-004`입니다. `top_k=10`, `ef_search=100` preset 경로로 권리 안내와 문서 초안까지 한 번에 보여줄 수 있습니다. `SCN-001`은 전체 제품 스토리(`Before -> Bridge -> After`)를 설명하는 대표 시나리오로 유지하고, `SCN-005`는 backup answer scenario로 둡니다. `SCN-003`은 확장성 설명용, `SCN-002`는 설명형 데모까지만 권장됩니다.

## 6. 제출 전 실행 계획

현재 단계의 핵심은 신규 기능 확장보다 QA 정합성과 시연 안정성 강화입니다.

### 공통 계획

- corpus 기준선 유지
- 메인/백업 시나리오 확정
- 질문 문안, 기대 citation, 시연 순서 최종 고정
- “현재 구현 완료”와 “후속 확장”을 발표 자료에서 명확히 분리

### After / Frontend 계획

- SCN-004 frontend/backend contract 정합성 확인
- `/api/v1/answer -> /api/v1/documents/draft` legal basis 전달 확인
- direct URL guard, API error, citation 없음 상태 확인
- copy / print / mobile layout smoke
- RAG 수정은 QA에서 regression이 재현될 때만 좁게 진행

### Before 계획

- Step 0: JSON 스키마와 파이프라인 안정화
- Step 1: 2-Layer OCR 및 핵심 항목 분류 고도화
- Step 2: `rule_validator.py` 중심 deterministic 검증 강화
- Step 3: `SCN-002`, `SCN-003` 중심 Before 시나리오 검증
- Step 4: Bridge 인터페이스 정의

## 7. 팀 구성 및 역할 분담

본 프로젝트는 2인 팀으로 운영됩니다.

- 김종원: `After` 단계 전체, 데이터 전처리 및 split 작업, 현재 저장소 구현 코드 담당
- 김민수: `Before` 단계 전체 담당

현재 저장소 구현이 `After` 중심으로 보이는 이유는, 김종원이 데이터 전처리와 backend 로직을 먼저 진행했기 때문입니다. 이후 `Before` 모듈이 붙으면서 전체 서비스는 `Before -> Bridge -> After` 흐름으로 통합될 예정입니다.

## 8. 인프라 확장성과 클라우드 방향

현재는 Vertex AI 기반 MVP로 동작 검증을 완료한 상태이며, 이후 GCP 위에 실제 서비스형 인프라를 구성하는 방향을 검토하고 있습니다.

### 왜 GCP인가

AWS도 유사 구성이 가능하지만, 본 프로젝트는 생성형 AI, 임베딩, RAG, 이후 GPU 기반 Local LLM 확장까지 포함하는 AI 중심 프로젝트입니다. 따라서 `Vertex AI 기반 MVP -> GCP GPU 기반 Local LLM 확장`이라는 흐름이 더 단순하고 일관된 AI-first 확장 스토리라고 판단했습니다.

### 기본 방향

- 기본 아키텍처: `Cloud Run` 중심의 serverless-first 구성
- API: `Cloud Run`
- DB: `Cloud SQL for PostgreSQL`
- 비밀값: `Secret Manager`
- 파일/산출물: `Cloud Storage`
- 배치: `Cloud Run Jobs`
- 오케스트레이션: `Workflows`
- AI: `Vertex AI`

Local LLM이 꼭 필요할 경우에는 `Compute Engine GPU + Ollama + Qwen` 계층을 선택적으로 추가하는 방향이 적절합니다.

## 9. 기대 효과 및 검토 요청 사항

### 기대 효과

- 일반 사용자도 계약 전 위험과 사후 대응 방향을 더 빠르게 이해할 수 있음
- 정보 취약 사용자에게 더 직접적인 보호 효과 제공 가능
- 분쟁 발생 후에도 법 조문 근거와 함께 대응 순서를 정리받을 수 있음
- 공공기관, 상담 보조 인력, 지원 활동가에게 보조 도구로 확장 가능

### 강사님께 검토받고 싶은 부분

- 프로젝트 포지셔닝이 적절한지
- 메인 시나리오를 `SCN-001`로 두는 전략이 적절한지
- `SCN-002`를 현재 범위 밖으로 두는 판단이 맞는지
- `After`를 먼저 구현하고 `Before`를 후속 연결하는 진행 방식이 괜찮은지
- 실제 실행 가능한 frontend demo를 `SCN-004`로 두고, 제품 대표 스토리를 `SCN-001`로 설명하는 구성이 자연스러운지
- `Cloud Run` 중심 serverless-first 구조와 GPU 기반 Local LLM 확장 방향이 적절한지
