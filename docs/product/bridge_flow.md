# Bridge Flow

기준일: `2026-04-20`

## 현재 상태

Bridge는 제품 구조상 `Before -> After`를 연결하는 단계다. 현재 SCN-004 frontend demo에서는 구현하지 않는다.

현재 기준:

- `/bridge` route 없음
- Before 결과 저장/복구 없음
- SCN-004 demo freeze 유지 중에는 Bridge 확장 금지
- 발표에서는 제품 확장 구조로 설명 가능

## 제품상 목표

- Before 단계에서 발견된 위험 태그와 요약을 보관
- After 분석 시 이전 위험 신호를 함께 보여줌
- “계약 단계에서 예견 가능했던 위험” 섹션 제공
- 상담자나 사용자가 계약 전/후 맥락을 한 번에 볼 수 있게 정리

## 저장 원칙

MVP에서는 개인정보 최소 수집 원칙을 우선한다.

저장 후보:

- 분석 시각
- 문서 유형
- 핵심 요약
- 위험 태그
- 주요 추출 항목
- cited_articles
- scenario_id
- source_scenario 또는 preset_id

`scenario_id`, `source_scenario`, `preset_id`는 `SCN-001-BRIDGE-DEMO` 같은 presentation preset과 Before output을 After에서 연결하기 위한 후보 필드다. 실제 API/DB 스펙 확정 전까지는 계획 수준 후보로만 둔다.

저장 금지 또는 후순위:

- 계약서 원문 전체
- 연락처, 계좌번호, 주민등록번호, 외국인등록번호
- raw OCR image / file body
- After raw statement

## 후속 조건

Bridge는 Before frontend와 결과 schema가 안정화된 뒤 별도 단계로 구현한다. 현재 다음 단계는 Bridge 구현이 아니라 SCN-004 demo freeze 유지다.
