# After Flow

기준일: `2026-04-20`

## 현재 구현 상태

SCN-004 After flow는 backend와 frontend가 연결된 demo path까지 구현 완료됐고, QA/content/frontend rehearsal을 통과했다.

구현 route:

- `/after`
- `/after/result`
- `/after/intake`
- `/after/draft`

연동 API:

- `POST /api/v1/answer`
- `POST /api/v1/documents/draft`

## 사용자 흐름

1. 사용자가 해고, 임금, 퇴직금, 사업장 변경 등 상황을 자유 진술로 입력한다.
2. 발표용 presentation-local preset exact path는 fixed answer fixture를 사용한다.
   - `SCN-001-BRIDGE-DEMO`: eval `SCN-001-Q3`이 아닌 Before/Bridge 발표 연결용 query, answer-only
   - `SCN-004-DEMO-FREEZE`: eval `SCN-004-Q1`이 아닌 document draft freeze용 query, SCN-004 draft eligibility 적용
3. preset 문장을 수정하면 `top_k=10`, 일반 자유 입력은 `top_k=5`로 `/api/v1/answer`를 호출한다.
4. 결과 화면에서 grounded answer, key points, cautions, cited_articles를 확인한다.
5. cited_articles와 grounded_context_ids가 없으면 문서 초안 flow로 진행하지 않는다.
6. SCN-004 draft 지원 상태면 문서 타입을 선택한다.
   - 고용노동청 임금체불 진정서 초안
   - 노동위원회 부당해고 구제신청 이유서 초안
7. 사건 정보는 선택 입력으로 받고, 빈 필드는 제출을 막지 않는다.
8. `/api/v1/documents/draft`가 facts, legal_basis, request, evidence_checklist, missing_fields, cautions, rendered_text를 반환한다.
9. 사용자는 초안을 검토하고 복사 또는 인쇄할 수 있다.

## Guardrails

- 검색되지 않은 조문을 초안에 추가하지 않는다.
- 사용자가 말하지 않은 날짜, 금액, 사업장명, 당사자명은 확인 필요로 둔다.
- 법률 판단 확정 문구를 피하고 제출 전 검토용 초안으로 표시한다.
- `SCN-001-BRIDGE-DEMO` preset은 fixed/live 여부와 관계없이 answer-only로 유지한다.
- `SCN-004-DEMO-FREEZE` preset과 preset 없는 자유 입력만 SCN-004 draft eligibility를 적용한다.
- SCN-005는 현재 frontend preset UI에서 제외하고 후속 확장 후보로만 유지한다.
- raw user_statement, answer_response, case_intake, draft_response는 Web Storage에 저장하지 않는다.

## 현재 freeze 기준

- `SCN-004-DEMO-FREEZE` exact preset fixed answer는 `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`를 유지한다.
- 부당해고 이유서 draft는 `근로기준법 제23조`, `제26조`, `제27조`, `제28조`를 포함하고 `missing_legal_basis=[]`를 유지한다.
- 임금체불 진정서 draft는 `근로기준법 제36조`, `근로자퇴직급여 보장법 제9조`를 포함하고 `missing_legal_basis=[]`를 유지한다.
- API error / direct URL guard / citation 없음 상태와 desktop/mobile demo layout은 제출 전 재확인 대상이다.
