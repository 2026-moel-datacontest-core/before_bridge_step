# Next Prompt

아래 내용을 다음 새 세션의 첫 프롬프트로 사용한다.

```text
/home/jongwon/personal_project/law_main_road 에서 작업해주세요.

현재 상태:
- 기준일은 2026-04-20입니다.
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
확인 후에는 아래 MVP 완성 순서를 기준으로 다음 작업을 정리해주세요.

MVP 완성 순서:
1. SCN-004 freeze 재확인
   - answer, draft, frontend flow, copy, print, direct URL guard가 기존 기준대로 동작하는지 확인
   - preset path가 통과하면 기존 SCN-004 demo output은 더 흔들지 않음
2. 자유 입력 문서 선택 guard 보강
   - 현재 `/after/result` 문서 선택지는 SCN-004 문서 2개로 고정되어 있음
   - 자유 입력 질문이 해고/임금체불/퇴직금 SCN-004 범위와 맞지 않으면 문서 선택지를 보여주지 않거나 disabled 처리
   - unsupported free input은 answer/key_points/cautions/cited_articles만 표시하고, "현재 문서 초안 지원 범위 밖" 안내를 표시
   - SCN-004 관련 자유 입력이면 기존 2개 문서 타입을 계속 선택 가능하게 유지
   - eligibility 판단은 query/cited_articles/grounded chunks 기반의 작은 frontend guard로 먼저 검토하고, backend API contract는 변경하지 않음
   - 이 작업은 SCN-005 구현이 아니라 SCN-004 자유 입력 correctness guard로 취급
3. 발표용 demo script / fallback script 고정
   - 실제 입력 문장, 클릭 순서, 강조할 조문, 보여줄 draft 영역, API 실패 시 fallback 멘트 정리
4. SCN-005 After 확장 여부 결정
   - 시간이 충분하면 문서 타입 1개만 좁게 구현
   - 시간이 애매하면 backup answer scenario / 후속 확장 후보로만 유지
5. SCN-005를 진행하는 경우 최소 범위로 구현
   - 육아휴직 / 가족돌봄휴가 질의 1~2개 확정
   - retrieval/answer smoke로 핵심 조문 확인
   - deterministic draft template 1개, fixture, verifier, 필요한 frontend 선택지만 추가
6. 팀원 Before output contract 확인
   - Before가 내보내는 JSON, risk_tags, extracted_terms, cited_articles, 개인정보 포함 여부 확인
   - 이 확인 전 SCN-001 frontend 확장 금지
7. Bridge 최소 contract 초안 정리
   - scenario_id, summary, risk_tags, extracted_terms, cited_articles, created_at, source 정도의 최소 필드만 검토
   - raw 계약서 원문, OCR 이미지, 민감 개인정보 저장은 피함
8. SCN-001 Before -> Bridge -> After는 마지막에 검토
   - Before contract와 Bridge 최소 contract가 정해진 뒤에만 진행 여부 판단
9. 최종 제출 패키징
   - README / runbook / demo_scenario / 발표 자료 최신화
   - 구현 완료 범위와 후속 확장 범위 구분
   - 스크린샷 또는 녹화, 로컬 실행 fallback 준비

위 1~9가 정리되면 인프라 단계로 넘어가면 됩니다.

인프라 전환 순서:
1. 로컬 실행 재현성 정리
2. `.env` / secret / credential 분리
3. backend 배포 방식 결정
4. frontend 배포 방식 결정
5. PostgreSQL + pgvector 운영 위치 결정
6. Vertex AI 인증 방식 정리
7. demo용 최소 배포 또는 로컬 발표 fallback 결정
8. 비용 / 보안 / 장애 대응 문서화

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
그 다음은 MVP 완성 순서 1~9를 진행하고, 이후 인프라 전환 순서로 넘어간다.
자유 입력을 열어둘 계획이므로, SCN-005보다 먼저 `/after/result` 문서 선택 eligibility guard를 보강한다.
SCN-005는 다음 확장 후보지만, SCN-004 freeze 기준을 깨지 않는 별도 패치로만 진행한다.
SCN-001 / Before / Bridge / Recovery는 팀원 contract 확인 전까지 구현하지 않는다.
