# Next Prompt

아래 내용을 다음 새 세션의 첫 프롬프트로 사용한다.

```text
/home/jongwon/personal_project/law_main_road 에서 작업해주세요.

현재 상태:
- 기준일은 2026-04-17입니다.
- RAG refinement landing 완료
- SCN-004 document draft backend 완료
- SCN-004 After frontend 4-route flow 완료
- Phase 3A/B 완료: rendered_text copy, browser print, print disclaimer
- SCN-004 QA 정합성 검증, content output 확인, manual browser rehearsal 통과
- 현재 작업 중심은 SCN-004 demo freeze 유지와 제출 전 재현성 확인입니다.
- 다음 확장 후보는 SCN-005 After frontend / 문서 타입이지만, SCN-004 freeze 기준을 유지한 별도 패치로만 진행합니다.
- SCN-001 frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 진행합니다.

먼저 해주세요:
1. git status로 origin/main과 clean/dirty 상태를 확인해주세요.
2. AGENTS.md, CLAUDE.md, backend/CLAUDE.md, frontend/CLAUDE.md를 읽고 현재 phase와 금지 범위를 확인해주세요.
3. README.md, docs/ops/runbook.md, docs/demo/demo_scenario.md를 읽고 SCN-004 freeze/QA 기록과 제출 전 재확인 절차를 확인해주세요.
4. docs/planning/00_project_overview.md, docs/planning/12_scenario_expansion_plan.md, docs/planning/13_document_draft_plan.md, docs/planning/14_frontend_implementation_handoff.md를 읽고 SCN-004 output 기대값과 후속 확장 조건을 확인해주세요.

현재 SCN-004 freeze 기준:
- SCN-004 preset `/api/v1/answer`: top_k=10, ef_search=100
- answer cited_articles=6
- answer grounded_context_ids=[1, 2, 3, 5, 10, 4]
- answer key_points에 정당한 이유, 30일 전 예고/통상임금, 서면통지, 노동위원회, 3개월 이내, 14일 금품청산 내용 표시
- wage complaint draft: cited_articles=2, missing_legal_basis=[]
- unfair dismissal brief draft: cited_articles=4, source_context_ids=[1, 2, 3, 4], missing_legal_basis=[]
- frontend `/after -> /after/result -> /after/intake -> /after/draft` manual browser flow 통과 상태
- copy, print, direct URL guard 통과 상태

제출 전 재확인 권장 명령:
```bash
conda activate law_main_road
python -c "from backend.main import app; print('import_ok')"
python backend/verify/check_document_draft.py

cd frontend
npm run build
```

필요하면 dev server를 띄워 manual browser rehearsal을 다시 확인해주세요.

backend:
```bash
conda activate law_main_road
uvicorn backend.main:app --reload
```

frontend:
```bash
cd frontend
npm run dev
```

브라우저 재확인 순서:
1. `/after`
2. SCN-004 preset 입력
3. 법 조문 찾기
4. `/after/result`에서 answer, key_points, cautions, cited_articles 확인
5. cited_articles / grounded_context_ids guard 확인
6. 문서 타입 선택
7. `/after/intake`에서 일부 값 또는 빈 값 제출
8. `/after/draft`에서 rendered_text, missing_fields, cautions, evidence_checklist, cited_articles 확인
9. copy 버튼 확인
10. print 버튼 확인
11. direct URL guard는 브라우저 런타임에서 확인

주의:
- SCN-005를 바로 구현하지 마세요. 사용자가 명시적으로 요청하면 별도 패치로만 진행하세요.
- SCN-001을 구현하지 마세요.
- `/before`, `/bridge`, Recovery를 구현하지 마세요.
- backend API contract를 임의 변경하지 마세요.
- RAG / retrieval / answer behavior를 regression 재현 없이 수정하지 마세요.
- `data/legalize-kr/`를 수정하지 마세요.
- `backend/data/law_chunks/`를 직접 수정하지 마세요.
- raw user_statement, answer_response, case_intake, draft_response를 Web Storage에 저장하지 마세요.
- 문제가 발견되면 코드 수정 전에 실패 지점, 재현 절차, 원인을 먼저 보고해주세요.
- 파일 수정이 필요하면 먼저 수정 범위를 보고해주세요.

이번 세션 목표는 먼저 SCN-004 freeze 상태가 유지되는지 확인하는 것입니다.
확인 후 사용자가 요청하면 다음 단계 후보로 SCN-005 After 문서 타입 확장을 별도 범위로 검토해주세요.

마지막에는 다음을 짧게 정리해주세요:
- git 상태
- 읽은 문서
- 실행한 검증과 결과
- SCN-004 freeze 유지 여부
- 수정한 파일
- 남은 리스크 또는 다음 권장 작업
```

## 참고

현재 문서상 다음 작업은 신규 기능 구현이 아니라 SCN-004 demo freeze 유지와 제출 전 재현성 확인이다.
SCN-005는 다음 확장 후보지만, SCN-004 freeze 기준을 깨지 않는 별도 패치로만 진행한다.
SCN-001 / Before / Bridge / Recovery는 팀원 contract 확인 전까지 구현하지 않는다.
