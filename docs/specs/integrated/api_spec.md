# Integrated API Spec

Status: draft/candidate scaffold

## Candidate Scope

This document is not final until team integration is complete. It should describe how the Before/Begin APIs and After APIs are exposed or connected in the unified service.

## Common Integration Checklist

통합 완료 전까지 이 문서는 candidate scaffold다. Before/Begin과 After를 연결할 때 아래 항목을 공통 검토 대상으로 유지하고, 실제 화면/API/schema/ERD는 팀원 통합 결과 확인 후 확정한다.

- `unified frontend flow`: 계약서 검토에서 After 법률 응답/초안 흐름까지 이어지는 사용자 여정.
- `handoff DTO`: Before/Begin 결과를 After 입력으로 넘길 최소 데이터 계약.
- `API gateway/proxy or unified backend strategy`: 분리 서비스 유지, 프록시, 단일 백엔드 중 선택할 통합 방식.
- `shared data/corpus strategy`: Before/Begin assets와 After law_chunks/corpus의 기준 데이터 운영 방식.
- `artifact/privacy policy`: 업로드 원본, OCR/review 산출물, 사용자 입력, intake/draft 산출물의 보관/접근/삭제 정책.
- `final schema/API/ERD confirmation after integration`: 실제 schema/API/ERD는 팀원 통합 완료 후 확정.

## Integration Topics To Cover

- API gateway/proxy strategy or unified backend strategy.
- Handoff DTO contract from contract review result to After/RAG input.
- Whether Before/Begin job APIs remain separate or are proxied under a main backend.
- Whether After `/api/v1/answer` and `/api/v1/documents/draft` remain unchanged behind the unified surface.
- Artifact access policy for `/artifacts` or any replacement storage URLs.

## Current API Families

- Before/Begin: contract review jobs, sync review, accessibility recommendations, health check.
- After: retrieve, answer, document draft.

## API TODOs

- Define the real gateway/proxy topology after integration.
- Define the handoff DTO schema and privacy filters.
- Define auth, access control, upload size limits, and artifact URL semantics for deployment.
- Confirm whether any endpoint paths change; do not mark final until code contracts are implemented or approved.
