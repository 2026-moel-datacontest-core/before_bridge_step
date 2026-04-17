# Document Draft Plan

기준일: `2026-04-17`

## 목적

- RAG stabilization 이후 다음 제품 단계인 문서 초안 생성 기능의 첫 설계 기준을 고정한다.
- `SCN-004`를 1순위 MVP로 두고, 노동청 진정서 / 노동위원회 이유서 초안에 필요한 `case intake`와 `document draft` schema를 정의한다.
- 기존 `/api/v1/answer` contract와 retrieval / answer generation service를 변경하지 않고, 사건 사실관계 구조화 레이어를 별도로 둔다.
- 현재 구현 완료 상태를 기준으로 frontend QA에서 확인해야 할 contract를 고정한다.

관련 기준 문서:

- [Project Overview](/home/jongwon/personal_project/law_main_road/docs/planning/00_project_overview.md)
- [Scenario Expansion Plan](/home/jongwon/personal_project/law_main_road/docs/planning/12_scenario_expansion_plan.md)
- [Architecture](/home/jongwon/personal_project/law_main_road/docs/planning/04_architecture.md)
- [MVP Scope](/home/jongwon/personal_project/law_main_road/docs/product/mvp_scope.md)

## 현재 구현 확인

현재 repo 기준으로 문서 초안 MVP는 기존 RAG service와 분리된 deterministic layer로 구현되어 있다.

- 기존 RAG API:
  - `POST /api/v1/retrieve`
  - `POST /api/v1/answer`
- 문서 초안 API:
  - `POST /api/v1/documents/draft`
- 문서 초안 파일:
  - `backend/app/schemas/document_draft.py`
  - `backend/app/services/document_draft.py`
  - `backend/app/routers/document_draft.py`
- frontend 연결 파일:
  - `frontend/src/types/api.ts`
  - `frontend/src/lib/api.ts`
  - `frontend/src/app/after/intake/page.tsx`
  - `frontend/src/app/after/draft/page.tsx`
- 유지 원칙:
  - `/api/v1/answer` contract는 변경하지 않는다.
  - `backend/app/services/retrieval.py`, `backend/app/services/answer_generation.py`, `backend/app/services/embedding.py`는 문서 초안 보완 범위에서 수정하지 않는다.
  - draft service는 RAG retrieval / answer generation을 직접 호출하지 않고, request로 받은 legal basis만 사용한다.

### 2026-04-16 skeleton 보완 사항

- H-1: `UnpaidWageInfo.unpaid_period_start`, `unpaid_period_end`를 optional로 추가하고, 체불 기간 누락 시 `missing_fields`에 표시한다.
- H-3: 부당해고 이유서에서 `dismissal_effective_date` 기준 3개월 초과 가능성을 deterministic caution으로 표시한다.
- H-4: `EmployerInfo.employee_count`, `employee_count_over_5`, `workplace_jurisdiction`를 optional로 추가하고, 5인 미만 / 적용 범위 확인 caution을 표시한다.
- M-1: `DismissalInfo.reinstatement_requested`, `monetary_compensation_requested`를 optional로 추가하고, 둘 다 없으면 구제신청 취지 확인을 `missing_fields`에 표시한다.
- M-4/M-5: `EmploymentInfo.wage_payment_day`, `continuous_service_over_1_year`를 optional로 추가하고, 임금 지급일 및 1년 미만 퇴직금 요건 확인을 deterministic하게 표시한다.
- H-2: 임금 항목별 체불액 구조화(`unpaid_items`)는 변경 폭이 커서 후순위로 둔다.
- fixture / smoke:
  - `backend/verify/fixtures/document_draft_scn004_wage_complaint.json`
  - `backend/verify/fixtures/document_draft_scn004_unfair_dismissal_brief.json`
  - `backend/verify/fixtures/document_draft_scn004_answer_legal_basis_wage_complaint.json`
  - `backend/verify/fixtures/document_draft_scn004_answer_legal_basis_unfair_dismissal_brief.json`
  - `backend/verify/check_document_draft.py`
- `check_document_draft.py`는 manual legal basis fixture와 `/api/v1/answer` 응답에서 캡처한 answer-derived legal basis fixture를 모두 draft endpoint에 주입해 contract를 확인한다.
- frontend intake form과 UI 연결은 구현 완료 상태다.
- 다음 단계에서는 backend fixture/smoke와 frontend API payload가 같은 contract를 유지하는지 QA한다.

### 2026-04-17 frontend 연결 상태

- `/after/result`에서 `cited_articles`와 `grounded_context_ids`가 없으면 draft flow를 guard한다.
- `/after/intake`에서 `buildLegalBasis(answer)`와 `buildCaseIntake(...)`를 사용해 draft request를 만든다.
- `buildLegalBasis()`는 `answer.grounded_context_ids`에 포함된 `retrieved_chunks`만 `legal_basis.retrieved_chunks`로 전달한다.
- `buildCaseIntake()`는 항상 `scenario_id: 'SCN-004'`, `document_type`, `language: 'ko'`, 기본 object/list를 채운다.
- 빈 timeline/evidence row는 submit 직전에 제거한다.
- `/after/draft`는 `rendered_text`, `missing_fields`, `cautions`, `evidence_checklist`, `cited_articles`, `source_context_ids`, `missing_legal_basis`를 표시한다.
- copy/print는 구현 완료. 저장/복구 기능은 구현하지 않는다.

### Answer-derived legal basis fixture 재캡처

answer/model output drift로 `SCN-004` answer-derived legal basis fixture를 갱신해야 할 때는 전용 verify script만 사용한다.

- script: `backend/verify/recapture_document_draft_legal_basis.py`
- 대상 fixture:
  - `SCN-004-Q2` -> `backend/verify/fixtures/document_draft_scn004_answer_legal_basis_unfair_dismissal_brief.json`
  - `SCN-004-Q3` -> `backend/verify/fixtures/document_draft_scn004_answer_legal_basis_wage_complaint.json`
- 기본 모드는 dry-run preview이며 기존 fixture를 저장하지 않는다.
- 기존 fixture 파일 갱신은 명시적으로 `--write`를 붙인 경우에만 수행한다.
- script는 `eval/scenario_demo_question_sets_v1.json`에서 질문과 `recommended_top_k`를 읽고, 값이 없으면 SCN demo 기준 `top_k=10`을 사용한다.
- `ef_search` 기본값은 `100`이며, recapture payload에는 `top_k`와 `ef_search`를 명시한다.

사용 예:

```bash
python backend/verify/recapture_document_draft_legal_basis.py --all-scn004
python backend/verify/recapture_document_draft_legal_basis.py --scenario-id SCN-004-Q2
python backend/verify/recapture_document_draft_legal_basis.py --all-scn004 --write
```

재캡처 script는 저장 전 다음을 확인한다.

- `cited_articles`, `source_context_ids`, `retrieved_chunks`가 비어 있지 않을 것
- `retrieved_chunks`는 `/api/v1/answer`의 `grounded_context_ids`에 해당하는 chunk만 포함할 것
- `SCN-004-Q2`는 `근로기준법 제23조`, `제26조`, `제27조`, `제28조` 근거를 포함할 것
- `SCN-004-Q3`는 `근로기준법 제36조`, `근로자퇴직급여 보장법 제9조` 근거를 포함할 것

재캡처 후 필수 검증:

```bash
python backend/verify/check_document_draft.py
```

이 절차는 `/api/v1/answer` contract, retrieval runtime, document draft service를 변경하지 않는 fixture 관리 절차다. full 60 eval, retrieval eval, answer eval, embedding/ingestion 재실행은 필요하지 않다.

## 기준선

- source of truth: `backend/data/law_chunks/all_chunks.json`
- `selected_as_of`: `2026-04-11`
- current live chunks / DB rows: `1722`
- embeddings: `1722 / 1722`
- retrieval full 60:
  - `hit@1 = 51/60 (85.00%)`
  - `hit@3 = 59/60 (98.33%)`
  - `hit@5 = 60/60 (100.00%)`
- answer full 60:
  - `items_answered = 60/60`
  - `citation_grounding_clean = 60/60`
  - `gold_citation_hit = 60/60`
  - `JSON/schema failure = 0`
  - `timeout = 0`
  - `expected_point_strict_coverage = 137/153`
  - `failures_or_partial_coverage = 16`

운영 기준:

- 일반 `/api/v1/answer` 기본값은 `top_k = 5`, `ef_search = 100`으로 유지한다.
- SCN demo / scenario smoke에서는 payload에 `top_k = 10`, `ef_search = 100`을 명시한다.
- 특히 `SCN-001 Full` 개선 경로는 `top_k >= 8`에서만 발동한다.
- 문서 초안 기능 구현 중 `backend/app/services/retrieval.py`, `backend/app/services/answer_generation.py`, `backend/app/services/embedding.py`는 기본적으로 수정하지 않는다.

## 우선순위

### 1순위: SCN-004

문서 타입:

- 고용노동청 임금체불 진정서 초안
- 지방노동위원회 부당해고 구제신청 이유서 초안

필수 근거 후보:

- `근로기준법 제23조 (해고 등의 제한)`
- `근로기준법 제26조 (해고의 예고)`
- `근로기준법 제27조 (해고사유 등의 서면통지)`
- `근로기준법 제28조 (부당해고등의 구제신청)`
- `근로기준법 제36조 (금품 청산)`
- `근로자퇴직급여 보장법 제9조 (퇴직금의 지급 등)`
- 필요 시 `근로기준법 제37조 (미지급 임금에 대한 지연이자)`
- 절차 안내가 필요한 경우 `근로기준법 시행규칙 제5조 (부당해고등의 구제신청)`

SCN-004가 1순위인 이유:

- 현재 corpus에서 핵심 조문이 모두 확인됐다.
- scenario smoke에서 결합 질의, 부당해고 절차 질의, 임금/퇴직금 체불 질의가 모두 안정적으로 동작한다.
- 문서 초안에 필요한 사실관계가 비교적 명확하다: 해고 통보 방식, 서면통지 여부, 30일 전 예고 여부, 마지막 근무일, 14일 경과 여부, 미지급 임금/퇴직금, 증거 자료.

### 2순위: SCN-005

문서 타입:

- 육아휴직 / 가족돌봄 재신청서
- 거절 사유 서면 요청서
- 내용증명 초안

### 3순위: SCN-001

문서 타입:

- 외국인근로자 사업장 변경 사유 정리서
- 상담용 사건 요약서

## 권장 아키텍처

기존 `/api/v1/answer`는 법령 근거와 행동 안내를 반환한다. 문서 작성에 필요한 사건 사실관계는 별도 `case_intake`로 수집하고, 문서 초안 endpoint는 이 둘을 결합한다.

```text
User statement
  -> /api/v1/answer
       - top_k=10, ef_search=100 for SCN demo
       - cited_articles
       - grounded_context_ids
       - retrieved_chunks
       - answer / key_points / cautions
  -> case intake collection
       - dates
       - parties
       - dismissal method
       - unpaid amount
       - evidence
       - requested actions
  -> /api/v1/documents/draft
       - case_intake
       - legal_basis copied from /answer response
  -> structured document draft
       - facts
       - legal_basis
       - request
       - evidence_checklist
       - missing_fields
       - cautions
```

권장 endpoint:

- `POST /api/v1/documents/draft`

설계 원칙:

- `/api/v1/answer`를 확장하지 않는다.
- draft endpoint는 RAG retrieval default를 바꾸지 않는다.
- 첫 구현에서는 draft request가 `/api/v1/answer`의 legal basis 결과를 입력으로 받는 구조가 가장 안전하다.
- draft service가 직접 retrieval / answer_generation service를 호출하는 orchestration은 후순위로 둔다.
- 법적 근거는 request에 들어온 `cited_articles`와 `source_context_ids`에서만 사용한다.
- 필수 근거가 누락되면 초안에서 새로 만들지 않고 `missing_legal_basis` 또는 `missing_fields`에 표시한다.

## Case Intake Schema 초안

초기 schema 이름 후보:

- `CaseIntake`
- `CaseDossier`

MVP에서는 `CaseIntake`를 request 중심 이름으로 사용하고, 향후 저장/재사용 객체가 되면 `CaseDossier`로 확장한다.

### 최상위 필드

- `scenario_id`: `SCN-004`, `SCN-005`, `SCN-001`
- `document_type`: 생성할 문서 타입
- `language`: `ko` 우선, `en`은 후순위
- `worker_info`: 근로자 정보
- `employer_info`: 사용자 / 회사 정보
- `employment_info`: 근로관계 정보
- `dismissal_info`: 해고 관련 사실
- `unpaid_wage_info`: 임금 / 퇴직금 체불 관련 사실
- `incident_timeline`: 날짜별 사건 경위
- `claims`: 사용자가 주장하려는 쟁점
- `evidence_items`: 증거 목록
- `requested_actions`: 원하는 조치
- `intake_notes`: 자유 메모

### 개인정보 원칙

- MVP demo에서는 이름, 연락처, 주소를 실제값으로 요구하지 않는다.
- 입력값이 없으면 `[근로자 이름 확인 필요]`, `[회사명 확인 필요]` 같은 placeholder를 사용한다.
- 전화번호, 이메일, 외국인등록번호, 계좌번호 등 직접 식별 정보는 MVP schema 필수값으로 두지 않는다.

### 필드 상세

```json
{
  "scenario_id": "SCN-004",
  "document_type": "labor_office_wage_complaint",
  "language": "ko",
  "worker_info": {
    "name_or_placeholder": "[근로자 이름 확인 필요]",
    "nationality": null,
    "preferred_language": "ko"
  },
  "employer_info": {
    "company_name_or_placeholder": "[회사명 확인 필요]",
    "representative_name": null,
    "workplace_address": null
  },
  "employment_info": {
    "start_date": null,
    "last_work_date": null,
    "job_title": null,
    "wage_terms": null,
    "employment_contract_exists": null
  },
  "dismissal_info": {
    "dismissal_notice_date": null,
    "dismissal_effective_date": null,
    "notice_method": "kakaotalk",
    "written_notice_received": false,
    "dismissal_reason_provided": null,
    "advance_notice_30_days": false
  },
  "unpaid_wage_info": {
    "final_wage_paid": false,
    "unpaid_wage_amount": null,
    "severance_paid": false,
    "unpaid_severance_amount": null,
    "days_since_separation_over_14": true
  },
  "incident_timeline": [
    {
      "date": null,
      "event": "카카오톡으로 다음 날부터 출근하지 말라는 통보를 받음",
      "evidence_refs": ["카카오톡 캡처"]
    }
  ],
  "claims": [
    "no_written_dismissal_notice",
    "no_advance_dismissal_notice",
    "unpaid_final_wages",
    "unpaid_severance_pay"
  ],
  "evidence_items": [
    {
      "type": "message",
      "description": "해고 통보 카카오톡 캡처",
      "status": "available"
    }
  ],
  "requested_actions": [
    "request_unpaid_wages_payment",
    "request_severance_payment",
    "request_labor_office_investigation"
  ],
  "intake_notes": null
}
```

권장 enum 후보:

- `document_type`
  - `labor_office_wage_complaint`
  - `labor_commission_unfair_dismissal_brief`
  - `family_leave_reapplication`
  - `written_reason_request`
  - `certified_letter`
  - `workplace_change_reason_summary`
  - `consultation_case_summary`
- `notice_method`
  - `written`
  - `kakaotalk`
  - `sms`
  - `email`
  - `verbal`
  - `phone`
  - `unknown`
- `claim`
  - `unfair_dismissal`
  - `no_written_dismissal_notice`
  - `no_advance_dismissal_notice`
  - `unpaid_final_wages`
  - `unpaid_severance_pay`
  - `delay_interest_possible`
- `evidence_type`
  - `message`
  - `sms`
  - `email`
  - `paystub`
  - `bank_statement`
  - `employment_contract`
  - `attendance_record`
  - `work_schedule`
  - `recording`
  - `photo`
  - `memo`
- `evidence_status`
  - `available`
  - `needs_collection`
  - `unknown`

## Legal Basis Input Schema 초안

문서 초안 endpoint는 `/api/v1/answer` 응답 중 문서 작성에 필요한 법령 근거를 별도 객체로 받는다.

```json
{
  "answer_query": "사장님이 카톡으로 내일부터 나오지 말라고 했어요...",
  "answer": "...",
  "key_points": ["..."],
  "cautions": ["..."],
  "cited_articles": [
    "근로기준법 제27조 (해고사유 등의 서면통지)",
    "근로기준법 제26조 (해고의 예고)",
    "근로기준법 제28조 (부당해고등의 구제신청)",
    "근로기준법 제36조 (금품 청산)",
    "근로자퇴직급여 보장법 제9조 (퇴직금의 지급 등)"
  ],
  "source_context_ids": [1, 2, 3, 4, 5],
  "retrieved_chunks": []
}
```

초기 구현에서는 `retrieved_chunks`를 optional로 둘 수 있다. 다만 문서 초안의 `source_context_ids`와 `cited_articles`는 `/api/v1/answer` 결과에서 온 값만 사용해야 한다.

## Document Draft Response Schema 초안

초기 schema 이름 후보:

- `DocumentDraftRequest`
- `DocumentDraftResponse`

응답은 사람이 바로 읽을 수 있는 `rendered_text`와 UI가 섹션별로 표시할 수 있는 structured sections를 함께 반환하는 구조가 적절하다.

```json
{
  "document_type": "labor_office_wage_complaint",
  "title": "임금 및 퇴직금 체불 진정서 초안",
  "recipient": "관할 고용노동청",
  "language": "ko",
  "parties": {
    "worker": "[근로자 이름 확인 필요]",
    "employer": "[회사명 확인 필요]"
  },
  "facts": [
    "근로자는 [입사일 확인 필요]부터 [회사명 확인 필요]에서 근무했습니다.",
    "근로자는 카카오톡으로 해고 통보를 받았다고 진술했습니다.",
    "퇴직 또는 마지막 근무 후 14일이 지났으나 마지막 임금과 퇴직금이 지급되지 않았다고 진술했습니다."
  ],
  "legal_basis": [
    {
      "citation_label": "근로기준법 제36조 (금품 청산)",
      "summary": "퇴직 후 임금 등 금품 청산 기한과 관련된 근거입니다.",
      "source_context_ids": [4]
    }
  ],
  "request": [
    "미지급 임금과 퇴직금 지급 여부를 조사해 주시기 바랍니다.",
    "미지급 금액은 [금액 확인 필요]입니다."
  ],
  "evidence_checklist": [
    "해고 통보 카카오톡 원본 및 캡처",
    "급여명세서",
    "통장 입금 내역",
    "근로계약서",
    "출퇴근기록 또는 근무표"
  ],
  "missing_fields": [
    "근로자 이름",
    "회사명",
    "입사일",
    "마지막 근무일",
    "미지급 임금 금액",
    "퇴직금 발생 여부와 미지급 금액"
  ],
  "cautions": [
    "이 문서는 제출 전 검토용 초안이며 법률대리 문서가 아닙니다.",
    "사용자가 제공하지 않은 날짜, 금액, 회사명은 확인 필요로 표시했습니다."
  ],
  "cited_articles": [
    "근로기준법 제36조 (금품 청산)",
    "근로자퇴직급여 보장법 제9조 (퇴직금의 지급 등)"
  ],
  "source_context_ids": [4, 5],
  "missing_legal_basis": [],
  "rendered_text": "..."
}
```

응답 필드:

- `document_type`: 생성 문서 타입
- `title`: 문서 제목
- `recipient`: 제출처 또는 수신자
- `language`: 출력 언어
- `parties`: 당사자 표시
- `facts`: 입력 사실 기반 사건 경위
- `legal_basis`: 검색된 조문 기반 근거 요약
- `request`: 요청사항
- `evidence_checklist`: 제출 / 보존 증거
- `missing_fields`: 초안 완성 전 확인해야 할 사실
- `cautions`: 단정 금지, 제출 전 검토 안내
- `cited_articles`: 실제 사용한 조문
- `source_context_ids`: 근거 context id
- `missing_legal_basis`: 문서 타입상 필요하지만 request의 legal basis에 없는 조문
- `rendered_text`: 섹션을 합친 초안 본문

## SCN-004 문서별 MVP 범위

### 고용노동청 임금체불 진정서 초안

목표:

- 미지급 임금과 퇴직금 지급 요청을 중심으로 사건을 정리한다.
- 해고 사실은 체불 발생 경위로만 쓰고, 부당해고 판단은 노동위원회 이유서로 분리한다.

필수 intake:

- 근로자 이름 또는 placeholder
- 회사명 또는 placeholder
- 입사일
- 퇴사일 또는 마지막 근무일
- 체불 기간 시작일 / 종료일
- 임금 지급일
- 마지막 임금 지급 여부
- 퇴직금 지급 여부
- 14일 경과 여부
- 미지급 금액 또는 `확인 필요`
- 보유 증거: 급여명세서, 통장내역, 근로계약서, 출퇴근기록, 해고 통보 메시지

사용 가능한 법적 근거:

- `근로기준법 제36조 (금품 청산)`
- `근로자퇴직급여 보장법 제9조 (퇴직금의 지급 등)`
- 필요 시 `근로기준법 제37조 (미지급 임금에 대한 지연이자)`

요청사항:

- 미지급 임금 조사
- 퇴직금 지급 여부 조사
- 지급기한 경과 여부 확인
- 미지급 금액 산정 보완 요청

### 지방노동위원회 부당해고 구제신청 이유서 초안

목표:

- 해고 통보 방식, 서면통지 여부, 해고예고 여부, 해고 사유 확인 필요성을 중심으로 부당해고 다툼 가능성을 정리한다.
- 임금 / 퇴직금 체불은 별도 진정 대상이므로 부수 사정 또는 별도 절차 안내로 분리한다.

필수 intake:

- 근로자 이름 또는 placeholder
- 회사명 또는 placeholder
- 입사일
- 해고 통보일
- 해고 효력 발생일 또는 마지막 근무일
- 상시근로자 수 또는 5인 이상 사업장 해당 여부
- 해고 방식: 카카오톡, 문자, 구두, 서면 등
- 해고 사유 서면 통지 수령 여부
- 30일 전 해고예고 여부
- 해고 사유 설명 여부
- 원하는 구제 내용: 원직복직, 금전보상, 임금상당액, 기타 조정 등 `확인 필요`
- 보유 증거: 카카오톡, 문자, 근로계약서, 근무표, 출퇴근기록, 동료 진술 등

사용 가능한 법적 근거:

- `근로기준법 제23조 (해고 등의 제한)`
- `근로기준법 제26조 (해고의 예고)`
- `근로기준법 제27조 (해고사유 등의 서면통지)`
- `근로기준법 제28조 (부당해고등의 구제신청)`
- 절차 안내가 필요하고 retrieval 근거가 있는 경우 `근로기준법 시행규칙 제5조 (부당해고등의 구제신청)`

요청사항:

- 해고의 정당성 및 절차 위반 여부 확인
- 구제신청 접수 전 사실관계 정리
- 구제 내용은 사용자가 명시하지 않으면 `확인 필요`로 표시

## Guardrails

- 검색된 조문 밖의 법적 근거를 새로 만들지 않는다.
- 사용자가 말하지 않은 사실을 단정하지 않는다.
- 금액, 날짜, 사업장명, 당사자명은 입력값이 없으면 placeholder 또는 `확인 필요`로 둔다.
- `위법 확정`, `무조건 무효`보다 `위반 가능성`, `다툴 수 있음`, `확인 필요` 표현을 우선한다.
- 문서 초안은 법률대리 문서가 아니라 사용자가 제출 전 검토할 수 있는 초안 / 정리문으로 표현한다.
- 노동청 진정과 노동위원회 구제신청은 목적과 제출처가 다르므로 한 문서로 섞지 않는다.
- 개인정보는 MVP에서 최소 수집 원칙을 유지한다.
- demo fixture에는 실제 이름, 연락처, 주소, 계좌번호를 넣지 않는다.

## 구현 파일 범위

현재 구현 파일:

- `backend/app/schemas/document_draft.py`
  - `CaseIntake`
  - `LegalBasisInput`
  - `DocumentDraftRequest`
  - `DocumentDraftResponse`
  - 관련 enum / nested model
- `backend/app/routers/document_draft.py`
  - `POST /api/v1/documents/draft`
  - blank / unsupported document type validation
- `backend/app/services/document_draft.py`
  - 초기에는 deterministic template builder 또는 TODO stub
  - retrieval / answer_generation service 직접 호출은 후순위
- `backend/app/routers/__init__.py`
  - document draft router 등록
- `frontend/src/types/api.ts`
  - frontend-side API contract mirror
- `frontend/src/lib/api.ts`
  - `fetchDraft`, `buildLegalBasis`, `buildCaseIntake`
- `frontend/src/app/after/intake/page.tsx`
  - case intake submit
- `frontend/src/app/after/draft/page.tsx`
  - draft result UI

후속 검증:

- `python backend/verify/check_document_draft.py`
- `cd frontend && npm run build`
- RAG service를 수정하지 않았으면 full 60 eval은 실행하지 않는다.

## 구현 완료 경과

1. Pydantic schema skeleton만 추가한다.
2. `SCN-004` demo fixture 2개를 만든다.
   - 임금체불 진정서
   - 부당해고 이유서
3. deterministic template service를 추가한다.
4. router를 등록한다.
5. `compileall`과 import smoke를 돌린다.
6. RAG legal basis 입력값은 기존 `/api/v1/answer` smoke 결과를 복사해 사용한다.
7. 문서 draft smoke 기준을 별도 eval로 분리한다.
8. frontend intake / draft UI를 연결한다.
9. copy / print polish를 추가한다.

현재는 1~9까지 완료됐고, SCN-004 QA 정합성 검증과 demo rehearsal도 통과했다. 현재 freeze 기준은 answer-derived draft 2종이 모두 `missing_legal_basis=[]`를 유지하는 것이다. SCN-005 After 문서 타입 확장은 SCN-004 freeze 기준을 유지한 별도 패치에서 진행한다.

## 후순위 검토

- draft endpoint가 직접 `/api/v1/answer` 경로를 orchestration할지 여부
- 다국어 출력 (`ko` primary, `en` secondary)
- missing field follow-up question generator
- document template versioning
- PDF / HWP export
- 제출기관별 실제 양식 반영
- SCN-005 문서 타입 확장
- 팀원 Before / Bridge contract 확인 후 SCN-001 문서 타입 확장
- sessionStorage backup/restore 없는 상태에서 demo 운영 문구 정리
