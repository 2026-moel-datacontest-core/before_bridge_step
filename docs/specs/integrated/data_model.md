# Integrated Data Model

Status: draft/candidate scaffold

## Candidate Scope

This document is not final until team integration is complete. It should describe cross-surface data contracts and storage boundaries for the unified service.

## Common Integration Checklist

통합 완료 전까지 이 문서는 candidate scaffold다. Before/Begin과 After를 연결할 때 아래 항목을 공통 검토 대상으로 유지하고, 실제 화면/API/schema/ERD는 팀원 통합 결과 확인 후 확정한다.

- `unified frontend flow`: 계약서 검토에서 After 법률 응답/초안 흐름까지 이어지는 사용자 여정.
- `handoff DTO`: Before/Begin 결과를 After 입력으로 넘길 최소 데이터 계약.
- `API gateway/proxy or unified backend strategy`: 분리 서비스 유지, 프록시, 단일 백엔드 중 선택할 통합 방식.
- `shared data/corpus strategy`: Before/Begin assets와 After law_chunks/corpus의 기준 데이터 운영 방식.
- `artifact/privacy policy`: 업로드 원본, OCR/review 산출물, 사용자 입력, intake/draft 산출물의 보관/접근/삭제 정책.
- `final schema/API/ERD confirmation after integration`: 실제 schema/API/ERD는 팀원 통합 완료 후 확정.

## Integration Topics To Cover

- Shared data/corpus strategy between main `all_chunks.json`/`law_chunks` and Before/Begin law chunk assets.
- Handoff DTO from Before/Begin review output to After answer or draft flows.
- Artifact model for uploaded files, OCR output, review result, explanation markdown, and any generated handoff summary.
- Privacy policy for personal/workplace information and draft/intake data.
- Retention and access control strategy for Cloud Storage, DB, logs, and static artifact serving.

## Data TODOs

- Decide the canonical corpus source and update process for integrated deployment.
- Define whether contract review artifacts are stored in Cloud Storage, DB, or both.
- Define whether After user statements, case intake, and draft outputs are stored at all.
- Define ERD only after the storage strategy and service boundaries are chosen.
- Finalize schema/API/ERD after team integration is complete.
