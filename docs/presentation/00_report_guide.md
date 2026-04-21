# Presentation Docs Guide

작성일: `2026-04-17`

업데이트 메모: 이 문서는 2026-04-17 발표/보고서 초안 가이드로 보존한다. 2026-04-21 기준 최신 demo / QA 상태는 `docs/demo/demo_scenario.md`, `docs/demo/presentation_notes.md`, `docs/ops/README.md`, `eval/reports/answer_evidence_2026-04-20.summary.md`를 우선한다.

## 목적

- `docs/presentation/` 문서들을 기반으로 보고서, 발표자료, 검토용 정리 문서를 만들 때 참고할 안내 문서
- 각 파일이 어떤 역할을 하는지와, 아직 추가 입력이 필요한 부분이 무엇인지 빠르게 파악할 수 있도록 정리

## 문서 사용 순서

1. `01_project_overview.md`
2. `02_plan.md`
3. `03_team_role.md`
4. `04_infrastructure_expansion.md`

## 각 문서 역할

### `01_project_overview.md`

- 프로젝트 아이디어
- 문제 정의
- 해결 방식
- 현재 구현 수준
- 대표 데모 시나리오

보고서에서 "프로젝트 소개"와 "현재 상태"를 쓸 때 가장 먼저 참고할 문서입니다.

### `02_plan.md`

- 제출 전 실행 계획
- 공통 계획 / Before 계획 / After 계획
- 범위 고정
- 시나리오 운영 계획
- 리스크와 대응

보고서에서 "향후 계획"과 "진행 전략"을 쓸 때 참고할 문서입니다.

### `03_team_role.md`

- 2인 팀 역할 분담
- 현재 저장소가 After 중심인 이유
- Before / After 담당 구분
- 협업 방식

보고서에서 "팀 구성"과 "개인 기여도"를 쓸 때 참고할 문서입니다.

### `04_infrastructure_expansion.md`

- 현재 Vertex AI 기반 MVP 구조
- GCP managed baseline 확장
- GPU 기반 Local LLM 확장
- 클라우드 포트폴리오 방향

보고서에서 "클라우드 확장성"과 "인프라 설계 방향"을 쓸 때 참고할 문서입니다.

## 현재 주의사항

- `01_project_overview.md`의 `Before 단계 구현 수준`은 팀원 입력이 아직 더 들어갈 수 있습니다.
- `02_plan.md`의 `Before 계획`도 팀원 진행 상황에 맞춰 더 구체화할 수 있습니다.
- 현재 저장소 구현은 `After` 중심이므로, 보고서에서 이를 숨기기보다 역할 분담의 결과로 설명하는 것이 더 자연스럽습니다.
- 현재 실제 frontend demo는 `SCN-004` After document draft flow입니다.
- `SCN-001`은 전체 제품 스토리를 설명하는 대표 시나리오로 두고, 실제 실행 화면은 `SCN-004` 중심으로 설명하는 것이 안전합니다.
- 인프라 확장 문서는 "현재 구현 완료"가 아니라 "다음 확장 방향" 문서입니다. 보고서에서 현재 상태와 구분해서 써야 합니다.

## 보고서 작성 시 권장 원칙

- 현재 구현 완료와 이후 확장 아이디어를 분리해서 쓸 것
- `selected_as_of = 2026-04-11`, 초안 상태 기준일 `2026-04-17`, 최신 QA 기준일 `2026-04-20`, 문서 작성일을 혼동하지 않을 것
- 프로젝트를 외국인 근로자 전용으로 한정하지 말고, 일반 사용자도 사용 가능하되 정보 취약 사용자에게 더 유용한 구조로 설명할 것
- 현재 MVP의 핵심은 grounded answer, SCN-004 문서 초안, demo QA 안정성이라는 점을 유지할 것
