# Frontend App Plan

## 목적

- MVP 앱 구현 범위 고정
- 웹앱 기준 화면/상태/API 전제 정리
- 데모 우선 구현 순서 명확화
- 2026-04-17 기준 실제 frontend 구현 상태와 다음 QA 범위 정리

---

## 앱 방향

- MVP 앱은 **Next.js 기반 웹앱**
- 네이티브 Android / iOS 앱은 이번 범위 아님
- 한국어 메인, 영어 보조
- 데스크톱 데모 우선
- 모바일은 기본 반응형만 지원
- 로그인 없이 사용 가능해야 함
- 개인정보 최소 수집 원칙 유지

## Current Status

- frontend는 SCN-004 After document draft demo 기준으로 구현 완료 상태다.
- 구현 stack:
  - Next.js `16.2.4`
  - React `19.2.5`
  - TypeScript
  - CSS Modules + `--kl-*` design tokens
- 구현 route:
  - `/`
  - `/after`
  - `/after/result`
  - `/after/intake`
  - `/after/draft`
- 실제 API 연동:
  - `POST /api/v1/answer`
  - `POST /api/v1/documents/draft`
- 구현 완료 범위:
  - Phase 1 API-connected happy path
  - Phase 2 error / loading / a11y / route guard
  - Phase 3 A/B: copy, print, evidence checklist local status
- 보류 범위:
  - Phase 3C 이후 확장 작업
  - sessionStorage backup/restore
  - transition animation
  - `/before`, `/bridge`, Recovery 본 구현
- 다음 단계는 QA 정합성 검증이다.

---

## 핵심 사용자 흐름

### Home

- 현재는 frontend foundation placeholder다.
- 제출 전 QA에서 `/after`로 redirect할지, 안내 placeholder로 둘지 결정한다.

### Before

- 현재 frontend 구현 범위 밖이다.
- 제품 구조상 남겨두되 SCN-004 demo QA 전에는 확장하지 않는다.

### After

- 사고 / 분쟁 자유 진술 입력
- 사건 정보 구조화
- 관련 조문 검색
- 다음 행동 안내
- 필요 증빙 항목 제시
- 문서 타입 선택
- 선택적 case intake 입력
- 노동청 진정서 또는 노동위원회 이유서 초안 생성
- rendered_text, missing_fields, cautions, evidence_checklist, cited_articles 표시
- 복사 / 인쇄 제공

### Bridge

- 현재 frontend 구현 범위 밖이다.
- Before 구현 이후 별도 단계에서 연결한다.

### Recovery

- 이번 MVP 본 구현 범위 아님
- placeholder 또는 `추후 지원` 문구만 허용

---

## 화면 제안

- `/`
- `/after`
- `/after/result`
- `/after/intake`
- `/after/draft`

필수 공통 UI:

- 입력 안내 문구
- 인용 조문 카드
- 주의 문구
- 다시 분석 버튼
- masthead
- skip link
- loading/error notification
- route guard fallback

---

## 입력 원칙

- 계약서 원문 업로드보다 텍스트 입력을 우선
- OCR 업로드는 backend OCR API 준비 시 연결
- After는 긴 자유 서술 입력을 기본으로 함
- 예시 입력 문구를 제공해 데모 실패율을 낮춤

---

## 결과 화면 원칙

- 긴 문단보다 카드형 요약 우선
- `무엇이 문제인지`
- `관련 조문`
- `왜 주의가 필요한지`
- `다음에 무엇을 해야 하는지`

법률 응답 공통:

- `cited_articles`가 없으면 법률 답변으로 표시하지 않음
- 검색되지 않은 조문은 화면에 노출하지 않음
- `위법 확정` 표현보다 `위법 가능성`, `주의 필요` 표현 우선

---

## 후속 Bridge 저장 원칙

- 현재 SCN-004 frontend demo는 Bridge 저장을 구현하지 않는다.
- 후속 Bridge 구현 시에는 브라우저 로컬 저장을 우선 검토한다.
- 저장 대상은 최소 필드만 허용
- 원문 전체 저장은 기본 비활성

저장 후보:

- 분석 시각
- 문서 유형
- 핵심 요약
- 위험 태그
- 주요 추출 항목
- cited_articles

이유:

- 로그인 없이도 Bridge 연결 가능
- 개인정보 저장 범위 최소화 가능
- 데모 준비와 복구가 단순함

---

## Backend 연동 전제

- frontend는 backend schema 확정 전 임의 필드 가정 금지
- 현재 frontend는 mock data가 아니라 실제 backend API contract에 연결되어 있음
- `NEXT_PUBLIC_API_BASE_URL` 기본값은 `http://localhost:8000`
- `cited_articles.length === 0` 또는 `grounded_context_ids.length === 0`이면 문서 초안 flow로 진행하지 않음
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response`는 Web Storage에 저장하지 않음

MVP 최소 필요 API:

- `POST /api/v1/answer`
- `POST /api/v1/documents/draft`

응답 최소 요구:

- answer / key_points / cautions
- cited_articles
- grounded_context_ids
- retrieved_chunks
- rendered_text
- missing_fields
- evidence_checklist

---

## 구현 상태

1. 공통 layout / typography / design tokens: 완료
2. API types / FlowContext / API helper: 완료
3. `/after` answer input: 완료
4. `/after/result` answer result + document type selection: 완료
5. `/after/intake` case intake form: 완료
6. `/after/draft` document draft result: 완료
7. API error / route guard / focus / skip link: 완료
8. copy / print: 완료
9. sessionStorage backup/restore: 보류
10. Before / Bridge / Recovery: 보류

우선순위 기준:

- 현재는 `SCN-004 After > QA > demo readiness`

---

## 제외 범위

- 네이티브 앱 개발
- 완전한 모바일 UX 최적화
- 회원가입 / 로그인
- 사용자별 서버 저장소
- 관리자 페이지
- 복잡한 멀티스텝 폼 엔진
- 채팅형 agent loop UI 고도화
- sessionStorage / localStorage backup-restore
- SCN-005 / SCN-001 문서 타입 frontend 확장

---

## 완료 기준

- `/after` 4-route flow가 backend API와 연결되어 동작
- cited_articles와 grounded context가 없으면 법률 답변 / 문서 초안 flow를 guard
- 문서 초안 결과에 rendered_text / missing_fields / cautions / evidence_checklist / cited_articles 표시
- copy / print 동작 확인
- direct URL guard 확인
- 모바일 폭에서도 SCN-004 demo path 레이아웃이 깨지지 않음
- `npm run build` 통과

---

## 메모

- 이번 문서의 `앱`은 네이티브 앱이 아니라 웹앱 의미
- 프론트엔드 구현은 demo stability first
- 세부 UI copy와 시각 스타일은 별도 문서로 분리 가능
- 현재 구현 상세 기준은 `docs/planning/14_frontend_implementation_handoff.md`
- 다음 작업 상세 기준은 QA 정합성 검증
