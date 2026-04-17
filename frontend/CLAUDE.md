# CLAUDE.md — frontend/

## 역할

- Next.js 기반 SCN-004 After demo 웹앱 담당
- 한국어 메인, 영어 보조
- demo stability first

## 우선 문서

1. `../docs/planning/08_frontend_app_plan.md`
2. `../docs/planning/14_frontend_implementation_handoff.md`
3. `../docs/planning/13_document_draft_plan.md`
4. `../docs/product/*.md`
5. `../CLAUDE.md`
6. existing code

## 현재 범위

- `/`
- `/after`
- `/after/result`
- `/after/intake`
- `/after/draft`
- `Before` / `Bridge` / `Recovery`는 현재 frontend 구현 범위에서 제외

## 현재 구현 상태

- Next.js `16.2.4`, React `19.2.5`, App Router, TypeScript, CSS Modules
- Phase 1 API-connected happy path 완료
- Phase 2 error / loading / a11y / route guard 완료
- Phase 3 A/B 완료:
  - rendered_text clipboard copy
  - browser print + print disclaimer
  - 증거 체크리스트 화면 내 로컬 상태
- Phase 3C 이후 확장 작업은 보류:
  - sessionStorage backup/restore
  - page transition animation
  - 현재 SCN-004 QA/demo freeze 완료 전 `/before`, `/bridge`, SCN-005/SCN-001 문서 타입 확장
- SCN-001 `Before -> Bridge -> After` 및 SCN-005 frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 별도 단계에서 검토
- 다음 단계는 QA 정합성 검증

## 핵심 원칙

- 앱은 네이티브가 아니라 웹앱 기준
- 데스크톱 데모 우선
- 모바일은 기본 반응형만 맞춤
- 긴 설명보다 구조화된 결과 카드 우선
- 인용 조문 표시가 핵심
- 입력 실패율 낮추는 UX 우선
- 문서 초안은 제출 전 검토용 보조이며 법률 판단 확정 UI로 보이지 않게 유지

## 상태 관리

- MVP는 복잡한 전역 상태 관리 도입 금지
- 현재 SCN-004 flow는 React Context + useReducer 메모리 상태만 사용
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response`를 sessionStorage/localStorage에 저장하지 않음
- 증거 체크리스트 상태는 화면 내 로컬 상태만 허용

## Backend 연동 규칙

- backend schema 확인 없이 응답 필드 가정 금지
- 실제 연동은 확정 API 기준으로 연결
- `cited_articles` 없는 법률 답변은 결과 화면에 노출 금지
- 검색되지 않은 조문 인용 금지
- `/api/v1/answer`는 SCN preset에서 `top_k=10`, 일반 자유 입력에서 `top_k=5`, 항상 `ef_search=100`
- `/api/v1/documents/draft`에는 `buildCaseIntake()`와 `buildLegalBasis()` 결과만 보냄

## 구현 우선순위

1. SCN-004 `/after` 4-route flow QA
2. backend schema / frontend type 정합성 확인
3. direct URL guard / API error / citation 없음 상태 확인
4. desktop/mobile smoke
5. demo polish는 regression 없이 가능한 범위만

## 제외 범위

- Android / iOS 네이티브 앱
- 완전한 모바일 UX 최적화
- 로그인 / 회원가입
- 사용자별 서버 저장
- 관리자 페이지
- 과도한 UI polishing
- Before / Bridge / Recovery 본 구현
- sessionStorage backup/restore
- PDF 다운로드 / 실제 제출 기능
- 현재 SCN-004 QA/demo freeze 완료 전 SCN-005 / SCN-001 문서 타입 확장
- 팀원 Before / Bridge code / schema / API contract 확인 없는 SCN-001 frontend 확장

## Do Not

- backend contract 임의 변경 전제 UI 작성
- 근거 없는 법률 문구 하드코딩
- 개인정보 수집 기능 추가
- 현재 SCN-004 QA/demo freeze 중 신규 대형 기능 추가
- 문서 범위를 넘는 독단적 화면 확장
