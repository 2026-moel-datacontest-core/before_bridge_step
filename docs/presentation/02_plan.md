# Execution Plan For Instructor Review

작성일: `2026-04-17`

기준선:

- RAG 및 시나리오 상태 기준일: `2026-04-17`
- corpus 기준일: `selected_as_of = 2026-04-11`

## 문서 목적

- 현재 프로젝트가 어디까지 구현되었는지와, 제출 전까지 무엇을 더 해야 하는지를 강사님 검토용으로 정리
- "무엇을 새로 만들지"보다 "무엇을 고정하고 어떤 리스크를 줄일지"에 초점을 둔 계획 문서

## 1. 현재 기준선

현재 프로젝트는 아이디어 검토 단계가 아니라, 이미 동작하는 RAG MVP를 확보한 상태입니다.

- 법령 corpus 고정 완료: `1722` chunks
- retrieval MVP 완료: `hit@5 = 60/60`
- grounded answer MVP 완료: `citation_grounding_clean = 60/60`
- RAG refinement landing 완료
- SCN-004 document draft API 완료
- SCN-004 frontend demo flow 완료
- scenario audit 완료: 주요 데모 시나리오 5개 검토
- 남은 핵심 이슈: SCN-004 QA 정합성과 demo freeze 확인

즉, 다음 단계의 핵심은 SCN-004 path가 backend/frontend schema, route guard, copy/print, live demo rehearsal에서 안정적으로 재현되는지 확인하는 것입니다.
SCN-005 After 확장은 이 확인 뒤 작은 범위로 붙일지 결정합니다.
SCN-001 frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 진행합니다.

## 2. 제출 전 실행 계획

### 2-1. 공통 계획

팀 전체 기준으로 공통으로 맞춰야 하는 계획입니다.

- 청킹 결과와 corpus 기준선 유지
- PostgreSQL + pgvector + embedding 상태 유지
- 발표용 메인 시나리오 1개와 백업 시나리오 1~2개 확정
- 질문 문안, 기대 citation, 시연 순서 최종 고정
- 발표 자료에서 "현재 구현 완료"와 "후속 확장"을 명확히 분리

즉, 공통 계획의 핵심은 새 기능을 넓히는 것보다 현재 기준선을 흔들지 않고 시연 안정성을 확보하는 것입니다.

### 2-2. After / Frontend QA 계획

현재 저장소와 구현 기준으로는 `After` 단계가 먼저 진행된 상태이며, 제출 전 핵심 과제는 SCN-004 frontend/backend 정합성 확인입니다.

- Step 0: backend DocumentDraftResponse와 frontend 타입 정합성 확인
- Step 1: `/api/v1/answer -> buildLegalBasis -> /api/v1/documents/draft` 전달 경로 확인
- Step 2: `/after` happy path 및 API error retry 확인
- Step 3: `/after/result` citation 없음 / grounded context 없음 guard 확인
- Step 4: `/after/intake` 빈 필드 submit과 `buildCaseIntake()` payload 확인
- Step 5: `/after/draft` rendered_text, missing_fields, cautions, evidence_checklist, cited_articles 표시 확인
- Step 6: copy / print / direct URL guard / mobile layout 확인

중요한 판단은 새 기능을 추가하지 않고, 현재 SCN-004 demo path의 실패 지점을 줄이는 것입니다.


### 2-3. Before 계획

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

## 3. 범위 고정

### 이번 제출 범위 안

- 법령 retrieval
- grounded answer
- cited articles 표시
- SCN-004 document draft API
- SCN-004 frontend demo
- `Before`, `After`, `Bridge` 흐름 설명
- 시나리오 기반 데모

### 이번 제출 범위 밖

- Recovery 본격 구현
- 연도별 최저임금 자동 비교
- 단순노무 직종 자동 판정
- 대규모 hybrid retrieval 전환
- Local LLM 운영 전환
- SCN-001 문서 타입 확장
- sessionStorage backup/restore
- Before / Bridge / Recovery frontend 본 구현

SCN-005 After 문서 타입 확장은 SCN-004 QA/freeze 확인 후 다음 구현 후보로 진행 가능하다.

이 구분이 중요한 이유는, 발표에서 확장 가능성을 말하더라도 실제 구현 범위와 혼동되면 프로젝트 평가가 오히려 불안정해질 수 있기 때문입니다.

## 4. 시나리오 운영 계획

| 구분 | 권장 선택 | 이유 |
|---|---|---|
| 제품 스토리 | `SCN-001` | `Before -> Bridge -> After` 흐름을 모두 보여주고 정보 취약 사용자 문제까지 함께 설명할 수 있음 |
| frontend main demo | `SCN-004` | 근거 조문이 선명하고 권리 안내 -> 문서 초안까지 end-to-end 시연 가능 |
| 백업 시나리오 B | `SCN-005` | 사회적 공감도가 높고 권리 + 대응 순서 설명이 자연스러움 |
| 확장 설명용 | `SCN-003` | 약자 지원형 UX 확장성 설명에 적합 |
| 범위 제한 시나리오 | `SCN-002` | 설명형 데모는 가능하지만 자동 숫자 판정은 현재 범위 밖 |

## 5. 현재 리스크와 대응

### 리스크 1. `SCN-001` Full 단일 질의 운영 조건

- 문제: 일반 API default `top_k=5`로 호출하면 SCN-001 selective decomposition이 발동하지 않을 수 있음
- 대응: 데모 UI / scenario runner / 직접 API smoke에서 `top_k=10`, `ef_search=100`을 명시

### 리스크 2. snapshot 혼합 위험

- 문제: raw source HEAD는 더 최신일 수 있지만, 현재 corpus 기준은 `2026-04-11`
- 대응: 발표와 검증은 frozen corpus 기준으로만 정리

### 리스크 3. 범위 확장 욕심

- 문제: OCR, Recovery, 추가 문서 타입을 한 번에 모두 보여주려 하면 메시지가 흐려짐
- 대응: 현재는 SCN-004 end-to-end 안정성에 집중

### 리스크 4. frontend 확장보다 QA가 더 중요

- 문제: 새 화면을 늘리면 QA surface가 커짐
- 대응: 최소 흐름만 유지하고 schema 정합성, route guard, API error 상태를 우선

## 6. 강사님 검토 요청 포인트

- 현재 계획에서 범위를 더 줄이는 것이 맞는지, 아니면 발표 설득력을 위해 일부를 더 보여줘야 하는지
- 제품 스토리와 실제 frontend demo 시나리오를 분리하는 전략이 적절한지
- `SCN-002`를 과감히 제외하고 안정적 시나리오 중심으로 가는 판단이 맞는지
- 발표 자료에서 "실제 구현 완료"와 "후속 확장"의 경계를 어떻게 설명하는 것이 좋은지

## 참고 문서

- `docs/planning/02_rag_strategy.md`
- `docs/planning/05_eval_plan.md`
- `docs/planning/10_backend_retrieval_plan.md`
- `docs/planning/12_scenario_expansion_plan.md`
- `docs/ops/task6_answer_generation_status.md`
- `docs/product/mvp_scope.md`
