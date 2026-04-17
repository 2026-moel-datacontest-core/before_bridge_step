# MVP Scope

## 목적

- 이번 MVP의 구현 범위 고정
- 포함 기능 / 제외 기능 구분
- 구현 우선순위 명확화
- 데모 기준 정리

---

## MVP 목표

- 계약서 또는 노동분쟁 상황 입력
- 관련 법령 조문 검색
- 근거 기반 응답 생성
- 다음 행동 안내 제공
- 현재 freeze 기준: SCN-004 기준 문서 초안 생성 demo 안정화
- 최종 demo 확장 목표: SCN-001 `Before -> Bridge -> After`, SCN-004 After document draft, SCN-005 After answer/document flow까지 단계적으로 포함

---

## 포함 범위

현재 구현 기준일: `2026-04-17`

### 현재 구현된 demo scope

- `After` 중심 SCN-004 flow
- 자유 진술 또는 preset 입력
- `/api/v1/answer` 기반 grounded answer
- 문서 타입 선택
- 선택적 case intake 입력
- `/api/v1/documents/draft` 기반 문서 초안 생성
- `rendered_text`, `missing_fields`, `cautions`, `evidence_checklist`, `cited_articles` 표시
- 초안 복사 / 인쇄

아래 Before / Bridge는 제품 구조상 MVP 범위다. 다만 현재 frontend 구현은 SCN-004 After flow에만 맞춰져 있으므로, Before / Bridge frontend 확장은 팀원이 작성한 Before / Bridge 코드와 contract를 확인한 뒤 별도 단계에서 진행한다.

### Before

- 계약서 텍스트 입력 또는 OCR 결과 입력
- 주요 항목 추출
- 위험 신호 분류
  - 누락
  - 불명확
  - 주의 필요
  - 위법 가능성
- 관련 법령 조문 제시
- 근거 기반 요약 응답

### After

- 자유 진술 입력
- 사건 핵심 정보 구조화
- 관련 법령 검색
- 근거 기반 설명
- 다음 행동 안내
- 필요 증빙 항목 제시
- SCN-004 문서 초안 생성:
  - 고용노동청 임금체불 진정서 초안
  - 노동위원회 부당해고 구제신청 이유서 초안

### Bridge

- Before 결과 저장
- 위험 태그 또는 요약 정보 저장
- After 분석 시 이전 결과 불러오기
- “계약 단계에서 예견 가능했던 위험” 섹션 출력

---

## 제한 포함 범위

### Recovery

- 제품 구조에는 포함
- 이번 MVP 핵심 범위는 아님
- 시간 여유 시만 검토
- 발표 자료에서는 확장 기능으로 설명 가능

---

## 기술 범위

### 포함

- 법령 청킹 결과 사용
- PostgreSQL + pgvector
- 기본 retrieval 구현
- top-k 조문 검색
- 근거 기반 응답 생성
- Gemini API 기반 MVP
- deterministic document draft service
- Next.js SCN-004 demo frontend
- 후속 frontend 확장 대상:
  - SCN-005 After demo
  - SCN-001 `Before -> Bridge -> After` demo
  - 팀원 Before / Bridge 코드 확인 후 연결되는 route와 payload adapter

### 조건부 포함

- JSON 응답 구조 고정
- cited_articles 검증
- frontend QA에서 필요한 최소 polish
- SCN-005 After frontend / 문서 타입 route 확장
- Before / Bridge contract 확인 후 SCN-001 frontend route 확장

### 후순위

- vector + keyword/BM25 결합
- metadata filtering
- reranker
- query decomposition 대규모 확장
- critic LLM
- local LLM 전환
- agent loop 고도화
- 다국어 UI 확장
- 프론트엔드 polishing
- 팀원 Before / Bridge 코드 확인 전 임의 frontend 확장

---

## 제외 범위

- Recovery 본격 구현
- 완전한 Local LLM 운영
- Mini-Agent 고도화
- 복잡한 재시도 루프
- 운영용 보안 고도화
- 관리자 기능
- 완전한 모바일 UX 최적화
- sessionStorage / localStorage backup-restore
- PDF / HWP 다운로드
- 실제 제출 기능
- 팀원 Before / Bridge code / schema / API contract 확인 없는 SCN-001 frontend 확장
- SCN-005 API / schema 검토 없는 독단적 문서 타입 확장
- SCN-001 문서 타입의 독단적 확장
- 현재 SCN-004 QA/demo freeze 완료 전에 `/before`, `/bridge` frontend 본 구현

---

## 성공 기준

### 현재 freeze 성공 기준

- SCN-004 `/after` 4-route flow가 backend API와 연결되어 동작
- cited_articles와 grounded_context_ids가 없으면 법률 답변 / 문서 초안 flow를 guard
- 문서 초안 결과에 rendered_text / missing_fields / cautions / evidence_checklist / cited_articles 표시
- copy / print 동작 확인
- direct URL guard 확인
- QA에서 backend/frontend schema mismatch 없음
- 데모 중단 없이 SCN-004 시연 가능

### 최종 demo 확장 성공 기준

#### Before

- 계약서 입력 가능
- 주요 항목 구조화 가능
- 관련 법령 검색 가능
- 위험 신호 + 근거 제시 가능

#### After

- 자유 진술 입력 가능
- 사건 정보 구조화 가능
- 관련 법령 검색 가능
- 다음 행동 안내 가능
- SCN-004 문서 초안 생성 가능
- 검색된 legal basis 밖 조문을 초안에 새로 만들지 않음
- SCN-005 After demo 확장 가능

#### Bridge

- Before 결과 저장 가능
- After에서 이전 결과 불러오기 가능
- 최소 연결 메시지 출력 가능
- SCN-001에서 `Before -> Bridge -> After` 연결 demo 가능

#### 공통

- 검색된 법령 근거 포함
- retrieval 실제 동작
- SCN-005 확장 시 backend schema와 frontend adapter contract 정합성 확보
- SCN-001 확장 시 팀원 Before / Bridge 코드와 frontend adapter contract 정합성 확보

---

## 우선순위

1. 법령 retrieval MVP
2. After MVP
3. grounded answer 품질 개선
4. SCN-004 document draft MVP
5. SCN-004 frontend demo
6. QA 정합성 검증
7. 데모 안정화
8. SCN-005 After demo / 문서 타입 확장
9. 팀원 Before / Bridge 코드와 contract 확인
10. SCN-001 `Before -> Bridge -> After` frontend 확장
