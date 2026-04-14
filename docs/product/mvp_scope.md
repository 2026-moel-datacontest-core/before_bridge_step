# MVP Scope

## 목적

- 이번 MVP의 구현 범위 고정
- 포함 기능 / 제외 기능 구분
- 구현 우선순위 명확화
- 데모 기준 정리

---

## MVP 목표

- 계약서 또는 산업재해 입력
- 관련 법령 조문 검색
- 근거 기반 응답 생성
- 다음 행동 안내 제공

---

## 포함 범위

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

### 조건부 포함

- vector + keyword/BM25 결합
- metadata filtering
- JSON 응답 구조 고정
- cited_articles 검증

### 후순위

- reranker
- query decomposition
- critic LLM
- local LLM 전환
- agent loop 고도화
- 다국어 UI 확장
- 프론트엔드 polishing

---

## 제외 범위

- Recovery 본격 구현
- 완전한 Local LLM 운영
- Mini-Agent 고도화
- 복잡한 재시도 루프
- 운영용 보안 고도화
- 관리자 기능
- 완전한 모바일 UX 최적화

---

## 성공 기준

### Before

- 계약서 입력 가능
- 주요 항목 구조화 가능
- 관련 법령 검색 가능
- 위험 신호 + 근거 제시 가능

### After

- 자유 진술 입력 가능
- 사건 정보 구조화 가능
- 관련 법령 검색 가능
- 다음 행동 안내 가능

### Bridge

- Before 결과 저장 가능
- After에서 이전 결과 불러오기 가능
- 최소 연결 메시지 출력 가능

### 공통

- 검색된 법령 근거 포함
- retrieval 실제 동작
- 데모 중단 없이 시연 가능

---

## 우선순위

1. 법령 retrieval MVP
2. After MVP
3. Before MVP
4. Bridge 최소 연결
5. 응답 품질 개선
6. 데모 안정화