# Execution Plan For Instructor Review

작성일: `2026-04-15`

기준선:

- RAG 및 시나리오 상태 기준일: `2026-04-14`
- corpus 기준일: `selected_as_of = 2026-04-11`

## 문서 목적

- 현재 프로젝트가 어디까지 구현되었는지와, 제출 전까지 무엇을 더 해야 하는지를 강사님 검토용으로 정리
- "무엇을 새로 만들지"보다 "무엇을 고정하고 어떤 리스크를 줄일지"에 초점을 둔 계획 문서

## 1. 현재 기준선

현재 프로젝트는 아이디어 검토 단계가 아니라, 이미 동작하는 RAG MVP를 확보한 상태입니다.

- 법령 corpus 고정 완료: `1722` chunks
- retrieval MVP 완료: `hit@5 = 60/60`
- grounded answer MVP 완료: `citation_grounding_clean = 60/60`
- scenario audit 완료: 주요 데모 시나리오 5개 검토
- 남은 핵심 이슈: 데이터 부족보다 복합 질의에서의 retrieval ranking과 answer coverage

즉, 다음 단계의 핵심은 대규모 기능 추가가 아니라 "현재 만든 시스템을 더 안정적으로 시연 가능한 상태로 다듬는 것"입니다.

## 2. 제출 전 실행 계획

### Phase 1. 기준선 고정

이미 완료된 범위입니다.

- 청킹 파이프라인 결과 고정
- PostgreSQL + pgvector + embedding 구성 완료
- retrieval / answer API 구현 완료
- eval runner 및 scenario smoke 자산 확보

### Phase 2. RAG refinement

다음 세션에서 가장 먼저 해야 하는 작업입니다.

- `SCN-001`, `SCN-004`, `SCN-005` 중심으로 복합 질의 안정성 보강
- query decomposition 검토
- sub-query retrieval + union / dedupe 검토
- clause ranking 및 answer-side selection 개선

중요한 판단은 "모델 교체"보다 "retrieval-grounding-answer 연결 정교화"가 우선이라는 점입니다.

### Phase 3. 데모 흐름 고정

- 메인 시나리오 1개와 백업 시나리오 1~2개 확정
- 질문 문안과 기대 citation을 최종 고정
- 발표 중 실패 가능성이 높은 문안은 제외
- `SCN-002`는 설명형 Before 범위로만 유지

### Phase 4. 프론트엔드/발표 자료 정리

- 최소한의 데모 화면 흐름 정리
- `Before`, `After`, `Bridge` 결과 구조를 발표용으로 단순화
- 시연 중 설명해야 하는 확장 기능과 실제 구현 완료 범위를 명확히 분리

## 3. 범위 고정

### 이번 제출 범위 안

- 법령 retrieval
- grounded answer
- cited articles 표시
- `Before`, `After`, `Bridge` 흐름 설명
- 시나리오 기반 데모

### 이번 제출 범위 밖

- Recovery 본격 구현
- 연도별 최저임금 자동 비교
- 단순노무 직종 자동 판정
- 대규모 hybrid retrieval 전환
- Local LLM 운영 전환
- 문서 자동 생성 기능의 본격 구현

이 구분이 중요한 이유는, 발표에서 확장 가능성을 말하더라도 실제 구현 범위와 혼동되면 프로젝트 평가가 오히려 불안정해질 수 있기 때문입니다.

## 4. 시나리오 운영 계획

| 구분 | 권장 선택 | 이유 |
|---|---|---|
| 메인 시나리오 | `SCN-001` | 프로젝트 정체성인 외국인 근로자 특화와 `Before -> Bridge -> After` 흐름을 모두 보여줌 |
| 백업 시나리오 A | `SCN-004` | 근거 조문이 선명하고 After 데모 안정성이 높음 |
| 백업 시나리오 B | `SCN-005` | 사회적 공감도가 높고 권리 + 대응 순서 설명이 자연스러움 |
| 확장 설명용 | `SCN-003` | 약자 지원형 UX 확장성 설명에 적합 |
| 범위 제한 시나리오 | `SCN-002` | 설명형 데모는 가능하지만 자동 숫자 판정은 현재 범위 밖 |

## 5. 현재 리스크와 대응

### 리스크 1. `SCN-001` Full 단일 질의 랭킹 불안정

- 문제: 복합 질문 한 번에 넣으면 필요한 조문 일부가 밀릴 수 있음
- 대응: 질의 분리, query shaping, sub-query retrieval 검토

### 리스크 2. snapshot 혼합 위험

- 문제: raw source HEAD는 더 최신일 수 있지만, 현재 corpus 기준은 `2026-04-11`
- 대응: 발표와 검증은 frozen corpus 기준으로만 정리

### 리스크 3. 범위 확장 욕심

- 문제: 자동 문서 작성, OCR, Recovery를 한 번에 모두 보여주려 하면 메시지가 흐려짐
- 대응: 현재는 grounded legal answer와 대표 시나리오 안정성에 집중

### 리스크 4. frontend 완성도보다 backend 품질이 더 중요

- 문제: 화면 polish에 시간을 많이 쓰면 핵심 품질 개선이 밀릴 수 있음
- 대응: 최소 흐름만 유지하고 RAG refinement를 우선

## 6. 강사님 검토 요청 포인트

- 현재 계획에서 범위를 더 줄이는 것이 맞는지, 아니면 발표 설득력을 위해 일부를 더 보여줘야 하는지
- 메인 시나리오를 하나로 고정하는 전략이 적절한지
- `SCN-002`를 과감히 제외하고 안정적 시나리오 중심으로 가는 판단이 맞는지
- 발표 자료에서 "실제 구현 완료"와 "후속 확장"의 경계를 어떻게 설명하는 것이 좋은지

## 참고 문서

- `docs/planning/02_rag_strategy.md`
- `docs/planning/05_eval_plan.md`
- `docs/planning/10_backend_retrieval_plan.md`
- `docs/planning/12_scenario_expansion_plan.md`
- `docs/ops/task6_answer_generation_status.md`
- `docs/product/mvp_scope.md`
