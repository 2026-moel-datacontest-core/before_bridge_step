# CLAUDE.md — frontend/

## 역할

- Next.js 기반 MVP 웹앱 담당
- `Before` / `After` / `Bridge` 화면 구현
- 한국어 메인, 영어 보조
- demo stability first

## 우선 문서

1. `../docs/planning/08_frontend_app_plan.md`
2. `../docs/product/*.md`
3. `../CLAUDE.md`
4. existing code

## 현재 범위

- `/`
- `/before`
- `/before/result`
- `/after`
- `/after/result`
- `/bridge`
- `Recovery`는 placeholder만 허용

## 핵심 원칙

- 앱은 네이티브가 아니라 웹앱 기준
- 데스크톱 데모 우선
- 모바일은 기본 반응형만 맞춤
- 긴 설명보다 구조화된 결과 카드 우선
- 인용 조문 표시가 핵심
- 입력 실패율 낮추는 UX 우선

## 상태 관리

- MVP는 복잡한 전역 상태 관리 도입 금지
- `Before -> Bridge` 연결은 브라우저 로컬 저장 우선
- 원문 전체 저장보다 요약 / 태그 / cited_articles 우선

## Backend 연동 규칙

- backend schema 확인 없이 응답 필드 가정 금지
- mock data로 먼저 화면 구현 가능
- 실제 연동은 확정 API 기준으로 연결
- `cited_articles` 없는 법률 답변은 결과 화면에 노출 금지
- 검색되지 않은 조문 인용 금지

## 구현 우선순위

1. 공통 layout / language toggle
2. `After`
3. `Before`
4. `Bridge`
5. backend 연결
6. demo polish

## 제외 범위

- Android / iOS 네이티브 앱
- 완전한 모바일 UX 최적화
- 로그인 / 회원가입
- 사용자별 서버 저장
- 관리자 페이지
- 과도한 UI polishing

## Do Not

- backend contract 임의 변경 전제 UI 작성
- 근거 없는 법률 문구 하드코딩
- 개인정보 수집 기능 추가
- freeze 이후 신규 대형 기능 추가
- 문서 범위를 넘는 독단적 화면 확장
