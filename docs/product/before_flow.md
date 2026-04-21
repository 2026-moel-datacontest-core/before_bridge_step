# Before Flow

기준일: `2026-04-21`

## 현재 상태

Before는 제품 구조상 핵심 단계이며, 현재 이 저장소에는 `/before` frontend와 backend 구현이 포함되어 있다.

현재 기준:

- `/before` route가 구현되어 있고 계약서 업로드/결과 확인 흐름을 제공한다.
- backend는 DB source 기반 법령 캐시, job DB 저장, artifact 로컬 저장 구조를 사용한다.
- 다만 현재 제출/메인 demo 범위는 여전히 `/after` 중심이다.
- `/before`는 repo에 포함된 별도 흐름으로 유지하며, 추가 확장은 별도 범위에서 진행한다.

## 제품상 목표

- 근로계약서 텍스트 또는 OCR 결과 입력
- 주요 근로조건 추출
- 누락 / 불명확 / 주의 필요 / 위법 가능성 신호 분류
- 관련 조문과 근거 요약 표시
- Bridge로 넘길 최소 요약 생성

## 현재 구현 범위

- 계약서 파일 업로드 UI
- OCR/리뷰 파이프라인 연동
- job polling
- `before_review_jobs` DB 저장
- `backend/data/before_artifacts/runs/` 로컬 artifact 저장
- DB source + startup cache 기반 법령 조회

## 현재 제외

- Bridge와의 정식 handoff contract 확정
- Cloud Run 기준 artifact GCS 전환
- 완전한 전역 공유 상태 저장

## 후속 연결 기준

Before 결과를 연결할 때는 원문 전체 저장보다 아래 최소 정보를 우선한다.

- 분석 시각
- 문서 유형
- 핵심 요약
- 위험 태그
- 주요 추출 항목
- cited_articles
- scenario_id
- source_scenario 또는 preset_id

`scenario_id`, `source_scenario`, `preset_id`는 Bridge/After 연결 시 Before 결과가 어떤 시나리오/프리셋으로 이어지는지 구분하기 위한 후보 필드다. 실제 필드 확정은 팀원 Before-begin output contract 확인 후 진행한다.

개인정보 최소 수집 원칙을 유지한다.
