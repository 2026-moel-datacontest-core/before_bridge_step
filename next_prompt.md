# Next Prompt

현재 RAG refinement, SCN-004 document draft backend, SCN-004 After frontend implementation은 완료 상태다. 다음 세션의 목표는 신규 기능 확장이 아니라 **QA 정합성 검증과 demo freeze**다.

## 현재 상태 요약

- corpus 기준: `selected_as_of = 2026-04-11`
- current chunks / DB rows: `1722`
- embedding: `1722 / 1722`
- retrieval baseline: `hit@5 = 60/60`
- answer baseline: `citation_grounding_clean = 60/60`, `gold_citation_hit = 60/60`, `expected_point_strict_coverage = 137/153`, `16 partial`
- RAG refinement landing 완료
- `POST /api/v1/documents/draft` 구현 완료
- frontend SCN-004 After 4-route flow 구현 완료:
  - `/after`
  - `/after/result`
  - `/after/intake`
  - `/after/draft`
- Phase 3 A/B 완료:
  - copy
  - print
  - evidence checklist local status
- Phase 3C 이후 확장 작업은 하지 않기로 결정:
  - sessionStorage backup/restore
  - transition animation
  - Before / Bridge / Recovery 확장
  - SCN-005 / SCN-001 문서 타입 확장

## 다음 세션 프롬프트

```text
현재 프로젝트는 `/home/jongwon/personal_project/law_main_road` 입니다.

이번 세션에서는 새 기능을 추가하지 말고, SCN-004 After document draft demo의 QA 정합성 검증을 진행해주세요.

먼저 아래 문서를 순서대로 읽어주세요.

1. AGENTS.md
2. CLAUDE.md
3. frontend/CLAUDE.md
4. backend/CLAUDE.md
5. docs/planning/00_project_overview.md
6. docs/planning/13_document_draft_plan.md
7. docs/planning/14_frontend_implementation_handoff.md
8. docs/product/after_flow.md
9. docs/ops/runbook.md

확인할 실제 코드:

- backend/app/schemas/document_draft.py
- backend/app/services/document_draft.py
- backend/app/routers/document_draft.py
- frontend/src/types/api.ts
- frontend/src/lib/api.ts
- frontend/src/context/FlowContext.tsx
- frontend/src/app/after/page.tsx
- frontend/src/app/after/result/page.tsx
- frontend/src/app/after/intake/page.tsx
- frontend/src/app/after/draft/page.tsx

QA 목표:

1. backend DocumentDraftResponse와 frontend DocumentDraftResponse 타입 정합성 확인
2. AnswerResponse -> buildLegalBasis -> DocumentDraftRequest 경로가 grounded_context_ids 기준으로 안전한지 확인
3. buildCaseIntake가 빈 row 제거, 기본 object/list 채움, 개인정보 최소 수집 원칙을 지키는지 확인
4. /after happy path smoke
5. /after/result citation 없음 / grounded context 없음 guard 확인
6. /after/intake 빈 필드 submit과 error retry 확인
7. /after/draft rendered_text, missing_fields, cautions, evidence_checklist, cited_articles 표시 확인
8. copy / print 동작 확인
9. direct URL guard 확인
10. desktop/mobile 기본 레이아웃 확인

실행 권장:

- python backend/verify/check_document_draft.py
- cd frontend && npm run build
- backend 실행 후 frontend dev server에서 manual smoke

주의:

- backend API contract를 임의 변경하지 말 것
- RAG service를 수정하지 말 것
- data/legalize-kr/를 수정하지 말 것
- sessionStorage backup/restore를 추가하지 말 것
- /before, /bridge, Recovery를 구현하지 말 것
- SCN-005 / SCN-001 문서 타입을 확장하지 말 것

마지막에는 확인한 항목, 통과/실패, 수정한 파일, 남은 리스크를 짧게 정리해주세요.
```

## QA 통과 후 후보 작업

1. 발표용 demo script와 fallback script 최종화
2. mobile smoke에서 발견된 layout 문제만 좁게 수정
3. QA에서 실제 schema mismatch가 발견된 경우에만 frontend type 또는 adapter 수정
4. RAG regression이 재현된 경우에만 targeted answer/retrieval 보강
