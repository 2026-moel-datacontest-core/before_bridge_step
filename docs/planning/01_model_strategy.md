# Model Strategy

## 목적

- 현재 고려 중인 모델 및 추론 전략 정리
- MVP 단계와 후속 확장 단계를 구분
- 확정 사항과 검토 중인 사항 분리

---

## 현재 방향

- **MVP는 Gemini API 기반으로 진행**
- 우선 목표는 **동작하는 retrieval + grounded answer + SCN-004 document draft 흐름 검증**
- 복잡한 자체 호스팅보다 **제출 안정성** 우선
- 모델은 확정이 아니라 **현재 기준 후보 및 방향**으로 관리

---

## MVP 단계

### 기본 방향

- Gemini API 중심으로 MVP 구현
- 검색 결과 기반 응답 생성 우선
- 법령 retrieval 품질과 응답 구조 검증 우선

### 현재 고려 중인 구성

- **임베딩 모델:** `gemini-embedding-001`
- **생성 모델:** `Gemini 2.5 Flash`

### 이유

- 초기 구현 속도 빠름
- 별도 GPU / 서버 운영 부담 없음
- MVP 단계에서 인프라 리스크 낮음
- 모델 자체보다 retrieval 흐름 검증에 집중 가능

---

## 이후 확장 방향

### Local LLM

- GCP + Ollama 기반 Local LLM 구조 검토
- HIGH / MEDIUM 민감도 입력 자체 처리 방향 고려
- 후보 예시: Qwen 계열 모델

### Reranker

- 별도 reranker 도입 가능성 검토
- 후보 예시: `BGE-reranker-v2-m3`

### 기타 고도화 요소

- Query Decomposition
- Critic 검증 루프
- Multi-tier 인덱스
- 민감도 기준 모델 라우팅

---

## 현재 확정된 것

- MVP는 Gemini API 기반으로 우선 진행
- retrieval MVP 완료
- grounded answer generation 및 citation grounding 구조 구현 완료
- RAG refinement landing 완료
- SCN-004 document draft backend 및 frontend demo flow 구현 완료
- default answer model은 `gemini-2.5-flash` 유지
- default embedding model은 `gemini-embedding-001` 유지

### A/B 결과 메모

- `gemini-2.5-pro`는 live A/B에서 `gemini-2.5-flash`보다 느리고 timeout이 많았음
- coverage 개선이 실측으로 유의미하게 확인되지 않아 default로 채택하지 않음
- 현재 병목은 retrieval miss보다 answer-side coverage와 clause selection에 가까움

---

## 현재 미확정 / 검토 중인 것

- Local LLM 실제 도입 여부
- Ollama 운영 방식
- reranker 도입 시점
- query decomposition 포함 여부
- critic 루프 적용 여부
- 민감도별 모델 분리 수준
- 향후 RAG 수정 이후 answer model 재평가 필요 여부
- QA에서 answer / draft 품질 회귀가 확인될 경우의 model 재측정 필요 여부

---

## 선택 원칙

- 제출 안정성 우선
- 구현 복잡도 최소화
- retrieval 품질 우선
- 근거 기반 응답 구조 우선
- 고도화는 MVP 이후 진행

---

## 정리

### 현재
- Gemini API 기반 MVP 유지
- answer: `gemini-2.5-flash`
- embedding: `gemini-embedding-001`

### 이후 검토
- GCP + Ollama 기반 Local LLM 확장
- reranker / critic / decomposition 등 고도화 요소 추가 검토
- RAG 구조 조정 이후 model choice 재측정

### 기준
- 지금은 **모델 교체보다 SCN-004 demo freeze 유지가 우선**
