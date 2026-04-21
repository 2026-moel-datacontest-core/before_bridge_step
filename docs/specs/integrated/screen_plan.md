# Integrated Screen Plan

Status: draft/candidate scaffold

## Candidate Scope

This document is not final until team integration is complete. It should describe the eventual unified screen flow across Before/Begin, Bridge, and After.

## Common Integration Checklist

통합 완료 전까지 이 문서는 candidate scaffold다. Before/Begin과 After를 연결할 때 아래 항목을 공통 검토 대상으로 유지하고, 실제 화면/API/schema/ERD는 팀원 통합 결과 확인 후 확정한다.

- `unified frontend flow`: 계약서 검토에서 After 법률 응답/초안 흐름까지 이어지는 사용자 여정.
- `handoff DTO`: Before/Begin 결과를 After 입력으로 넘길 최소 데이터 계약.
- `API gateway/proxy or unified backend strategy`: 분리 서비스 유지, 프록시, 단일 백엔드 중 선택할 통합 방식.
- `shared data/corpus strategy`: Before/Begin assets와 After law_chunks/corpus의 기준 데이터 운영 방식.
- `artifact/privacy policy`: 업로드 원본, OCR/review 산출물, 사용자 입력, intake/draft 산출물의 보관/접근/삭제 정책.
- `final schema/API/ERD confirmation after integration`: 실제 schema/API/ERD는 팀원 통합 완료 후 확정.

## Integration Topics To Cover

- Unified frontend flow and navigation model.
- Whether Before/Begin remains a separate Vite app, is embedded/linked from main Next.js, or is migrated into a single route surface.
- Bridge handoff screen or summary state from contract review to legal question.
- After result/intake/draft continuation from a Before/Begin-derived handoff DTO.
- Privacy and artifact notice screens for uploaded contracts and generated outputs.

## Screen TODOs

- Define route map only after frontend integration strategy is chosen.
- Define handoff summary UI and user consent point.
- Define error and unsupported-state screens for cross-service failures.
- Define whether uploaded artifact previews remain visible after handoff.
- Finalize copy, mobile layout, and accessibility behavior after actual integration.
