# Frontend App Plan

## 목적

- MVP 앱 구현 범위 고정
- 웹앱 기준 화면/상태/API 전제 정리
- 데모 우선 구현 순서 명확화

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

- frontend는 이번 backend MVP 범위에서 아직 본격 구현하지 않음
- backend retrieval / answer schema는 현재 고정 기준선이 존재함
- frontend 후속 작업은 `cited_articles`, grounded answer 구조, timeout/503 처리 방식을 그대로 따라야 함
- 다음 단계는 frontend polishing보다 backend RAG refinement가 우선

---

## 핵심 사용자 흐름

### Home

- 서비스 소개
- `Before 시작`
- `After 시작`
- 저장된 Before 결과가 있으면 Bridge 진입 안내

### Before

- 근로계약서 텍스트 입력
- OCR 결과 붙여넣기 입력
- 주요 항목 구조화
- 위험 신호 분류
- 관련 조문 / 근거 요약 표시
- Bridge용 최소 결과 저장

### After

- 사고 / 분쟁 자유 진술 입력
- 사건 정보 구조화
- 관련 조문 검색
- 다음 행동 안내
- 필요 증빙 항목 제시
- 저장된 Before 결과가 있으면 연결 메시지 표시

### Bridge

- Before의 위험 태그 / 요약 표시
- After 결과와 연결
- `계약 단계에서 예견 가능했던 위험` 섹션 표시

### Recovery

- 이번 MVP 본 구현 범위 아님
- placeholder 또는 `추후 지원` 문구만 허용

---

## 화면 제안

- `/`
- `/before`
- `/before/result`
- `/after`
- `/after/result`
- `/bridge`

필수 공통 UI:

- 상단 언어 토글
- 입력 안내 문구
- 인용 조문 카드
- 주의 문구
- 다시 분석 버튼

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

## Bridge 저장 원칙

- MVP는 브라우저 로컬 저장 우선
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
- 초기 UI 구현은 mock data로 가능
- 실제 연동은 확정된 API response에 맞춰 adapter 층에서 연결

MVP 최소 필요 API:

- `POST /before/analyze`
- `POST /after/analyze`
- `POST /ocr/extract` optional

응답 최소 요구:

- 구조화 결과
- summary
- cited_articles
- risk signals 또는 next actions

---

## 구현 순서

1. 공통 layout / typography / language toggle
2. Home 화면
3. After 입력/결과 화면
4. Before 입력/결과 화면
5. Bridge 최소 연결 화면
6. mock data 연결
7. backend API 연결
8. demo polish

우선순위 기준:

- `After > Before > Bridge > Recovery`

---

## 제외 범위

- 네이티브 앱 개발
- 완전한 모바일 UX 최적화
- 회원가입 / 로그인
- 사용자별 서버 저장소
- 관리자 페이지
- 복잡한 멀티스텝 폼 엔진
- 채팅형 agent loop UI 고도화

---

## 완료 기준

- Home / Before / After / Bridge 화면이 모두 존재
- mock data만으로도 데모 흐름 재현 가능
- cited_articles가 결과 카드에 표시됨
- Before 결과를 저장하고 After에서 불러올 수 있음
- Recovery는 placeholder로 분리됨
- 모바일 폭에서도 레이아웃이 깨지지 않음

---

## 메모

- 이번 문서의 `앱`은 네이티브 앱이 아니라 웹앱 의미
- 프론트엔드 구현은 demo stability first
- 세부 UI copy와 시각 스타일은 별도 문서로 분리 가능
