# After Flow

기준일: `2026-04-17`

## 현재 구현 상태

SCN-004 After flow는 backend와 frontend가 연결된 demo path까지 구현 완료됐다.

구현 route:

- `/after`
- `/after/result`
- `/after/intake`
- `/after/draft`

연동 API:

- `POST /api/v1/answer`
- `POST /api/v1/documents/draft`

## 사용자 흐름

1. 사용자가 해고, 임금, 퇴직금 상황을 자유 진술로 입력한다.
2. SCN-004 preset을 쓰면 `top_k=10`, 일반 입력은 `top_k=5`로 `/api/v1/answer`를 호출한다.
3. 결과 화면에서 grounded answer, key points, cautions, cited_articles를 확인한다.
4. cited_articles와 grounded_context_ids가 없으면 문서 초안 flow로 진행하지 않는다.
5. 문서 타입을 선택한다.
   - 고용노동청 임금체불 진정서 초안
   - 노동위원회 부당해고 구제신청 이유서 초안
6. 사건 정보는 선택 입력으로 받고, 빈 필드는 제출을 막지 않는다.
7. `/api/v1/documents/draft`가 facts, legal_basis, request, evidence_checklist, missing_fields, cautions, rendered_text를 반환한다.
8. 사용자는 초안을 검토하고 복사 또는 인쇄할 수 있다.

## Guardrails

- 검색되지 않은 조문을 초안에 추가하지 않는다.
- 사용자가 말하지 않은 날짜, 금액, 사업장명, 당사자명은 확인 필요로 둔다.
- 법률 판단 확정 문구를 피하고 제출 전 검토용 초안으로 표시한다.
- raw user_statement, answer_response, case_intake, draft_response는 Web Storage에 저장하지 않는다.

## 다음 단계

- QA 정합성 검증
- API error / direct URL guard / citation 없음 상태 smoke
- desktop/mobile demo layout 확인
