현재 RAG refinement와 SCN demo 안정화는 landing 완료 상태다. 이 파일은 다음 세션에서 **문서 초안 생성 기능**을 시작하기 위한 handoff prompt다.

## 현재 상태 요약

- source of truth: `backend/data/law_chunks/all_chunks.json`
- selected_as_of: `2026-04-11`
- current live chunks / DB rows: `1722`
- embedding populated: `1722 / 1722`
- retrieval eval:
  - `hit@1 = 51/60 (85.00%)`
  - `hit@3 = 59/60 (98.33%)`
  - `hit@5 = 60/60 (100.00%)`
- answer eval clean pass:
  - `items_answered = 60/60`
  - `citation_grounding_clean = 60/60`
  - `gold_citation_hit = 60/60`
  - `JSON/schema failure = 0`
  - `timeout = 0`
  - `expected_point_strict_coverage = 137/153`
  - `failures_or_partial_coverage = 16`
- committed RAG stabilization:
  - commit: `11fd65f feat: stabilize RAG answer coverage and SCN demo retrieval`

## 운영 기준

- 일반 `/api/v1/answer` 기본값은 `top_k = 5`, `ef_search = 100`으로 유지한다.
- SCN demo / scenario smoke는 `recommended_top_k = 10`을 따른다.
- 특히 `SCN-001 Full` 개선 경로는 `top_k >= 8`에서만 발동한다.
- 데모 UI / scenario runner / 직접 API smoke에서는 payload에 `top_k: 10`, `ef_search: 100`을 명시한다.
- `SCN-001`, `SCN-004`, `SCN-005`가 After 핵심 시나리오다.
- `SCN-002`, `SCN-003`은 이번 문서 초안 MVP의 직접 대상이 아니다.

## 현재 해석

- RAG는 법령 근거 레이어까지 안정화됐다.
- `/api/v1/answer`는 `answer`, `key_points`, `cautions`, `cited_articles`, `grounded_context_ids`, `retrieved_chunks`를 반환한다.
- 즉 진정서/이유서/재신청서에 넣을 법적 근거 데이터는 이미 가져오고 있다.
- 아직 없는 것은 문서 작성에 필요한 사건 사실관계 데이터 수집/구조화 레이어다.
- 다음 단계의 중심은 RAG를 더 고치는 것이 아니라, `case dossier`를 만들고 RAG legal basis와 결합해 문서 초안을 생성하는 것이다.

## 다음 세션 프롬프트

아래 지시를 새 Codex 세션에 그대로 넣는다.

```md
현재 프로젝트는 `/home/jongwon/personal_project/law_main_road` 입니다.

목표:
RAG refinement는 완료됐습니다. 이번 세션에서는 RAG를 더 수정하지 말고, 다음 제품 단계인 **문서 초안 생성 기능**의 첫 단계를 진행해주세요. 핵심은 `SCN-004`를 기준으로 노동청 진정서 / 노동위원회 이유서 초안 생성을 위한 `case intake schema`와 `document draft API/service` 설계를 확정하는 것입니다.

중요 전제:
- 먼저 코드 구현을 크게 시작하지 마세요.
- 우선 문서/코드 구조를 읽고, 최소 설계 문서 또는 아주 작은 schema skeleton까지가 목표입니다.
- `/api/v1/answer`를 무리하게 확장하지 마세요.
- RAG retrieval / answer generation 로직은 수정하지 마세요.
- `backend/app/services/retrieval.py`, `backend/app/services/answer_generation.py`, `backend/app/services/embedding.py`는 이번 세션에서 건드리지 않는 것을 기본 원칙으로 합니다.
- API default `top_k=5`, `ef_search=100`은 유지해야 합니다.
- SCN demo/smoke에서만 `top_k=10`, `ef_search=100`을 사용합니다.
- `data/legalize-kr/`는 절대 수정하지 마세요.
- 개인정보는 MVP에서 최소 수집 원칙을 유지하고, 데모에서는 placeholder를 우선 사용합니다.

먼저 읽을 것:
1. `AGENTS.md`
2. `CLAUDE.md`
3. `docs/planning/00_project_overview.md`
4. `docs/planning/12_scenario_expansion_plan.md`
5. `docs/planning/04_architecture.md`
6. `docs/product/mvp_scope.md`
7. `backend/app/schemas/answer.py`
8. `backend/app/routers/answer.py`
9. `backend/app/schemas/retrieval.py`

현재 기준선:
- source of truth: `backend/data/law_chunks/all_chunks.json`
- selected_as_of: `2026-04-11`
- chunks / DB rows: `1722`
- embeddings: `1722 / 1722`
- retrieval full 60: `hit@1 = 51/60`, `hit@3 = 59/60`, `hit@5 = 60/60`
- answer full 60: `137/153`, `16 partial`, grounding/gold/schema/timeout clean
- RAG stabilization commit: `11fd65f feat: stabilize RAG answer coverage and SCN demo retrieval`

제품 방향:
- 지금 RAG는 법령 근거를 가져오는 단계까지 완료됐습니다.
- 진정서 작성에 필요한 것은 별도 사건 사실관계 구조화입니다.
- `/api/v1/answer` 응답의 `cited_articles`, `grounded_context_ids`, `retrieved_chunks`, `answer`, `key_points`를 legal basis로 활용합니다.
- 새 레이어는 `case dossier` 또는 `case intake`로 설계합니다.

이번 세션 직접 목표:
1. 현재 repo에 문서 초안/진정서/사건 intake 관련 구현이 있는지 확인
2. `SCN-004`를 1순위 문서 초안 MVP로 잡는 것이 맞는지 재확인
3. `case intake schema` 초안 설계
4. `document draft response schema` 초안 설계
5. `POST /api/v1/documents/draft` 같은 별도 endpoint가 적절한지 검토
6. 바로 구현할 경우의 최소 파일 범위 제안
7. 가능하면 문서에 설계안을 남기고, 코드 구현은 사용자 승인 후 다음 세션으로 넘김

우선순위:
1. `SCN-004`
   - 문서 타입:
     - 고용노동청 임금체불 진정서 초안
     - 지방노동위원회 부당해고 구제신청 이유서 초안
   - 필수 근거:
     - `근로기준법 제23조`
     - `근로기준법 제26조`
     - `근로기준법 제27조`
     - `근로기준법 제28조`
     - `근로기준법 제36조`
     - `근로자퇴직급여 보장법 제9조`
     - 필요 시 `근로기준법 제37조`
2. `SCN-005`
   - 문서 타입:
     - 육아휴직/가족돌봄 재신청서
     - 거절 사유 서면 요청서
     - 내용증명 초안
3. `SCN-001`
   - 문서 타입:
     - 외국인근로자 사업장 변경 사유 정리서
     - 상담용 사건 요약서

case intake 최소 필드 후보:
- `scenario_id`
- `document_type`
- `language`
- `worker_info`
- `employer_info`
- `employment_info`
- `incident_timeline`
- `claims`
- `evidence_items`
- `requested_actions`
- `legal_basis`
- `missing_fields`

SCN-004에 필요한 사실관계 후보:
- 근로자 이름 또는 placeholder
- 회사명 또는 placeholder
- 입사일
- 해고 통보일
- 해고 방식: 카톡, 문자, 구두, 서면 등
- 해고 사유 서면 통지 수령 여부
- 30일 전 해고예고 여부
- 퇴사일 또는 마지막 근무일
- 마지막 임금 지급 여부
- 퇴직금 지급 여부
- 14일 경과 여부
- 미지급 금액 또는 확인 필요
- 보유 증거: 카톡, 문자, 급여명세서, 통장내역, 근로계약서, 출퇴근기록 등
- 원하는 조치: 임금 지급, 퇴직금 지급, 조사 요청, 부당해고 구제 등

document draft response 최소 필드 후보:
- `document_type`
- `title`
- `recipient`
- `parties`
- `facts`
- `legal_basis`
- `request`
- `evidence_checklist`
- `missing_fields`
- `cautions`
- `cited_articles`
- `source_context_ids`

guardrails:
- 검색된 조문 밖의 법적 근거를 새로 만들지 않는다.
- 사용자가 말하지 않은 사실을 단정하지 않는다.
- 금액, 날짜, 사업장명, 당사자명은 입력값이 없으면 placeholder 또는 `확인 필요`로 둔다.
- `위법 확정`보다 `위반 가능성`, `다툴 수 있음`, `확인 필요` 표현을 우선한다.
- 문서 초안은 법률대리 문서가 아니라 사용자가 제출 전 검토할 수 있는 초안/정리문으로 표현한다.

권장 산출물:
- 우선 문서 설계안 추가 또는 갱신
  - 예: `docs/planning/13_document_draft_plan.md`
  - 또는 기존 적절한 planning 문서에 섹션 추가
- 코드 구현을 한다면 최소 skeleton만:
  - `backend/app/schemas/document_draft.py`
  - `backend/app/routers/document_draft.py`
  - service는 아직 stub 또는 TODO 가능
- 단, 코드 skeleton 생성 전에는 먼저 설계 요약을 보고하고 진행 여부를 판단하세요.

검증:
- 코드 수정이 없으면 테스트는 필수 아님.
- schema skeleton만 추가했다면:
  - `python -m compileall backend`
  - backend import 확인
- RAG service를 건드리지 않았으면 full 60 eval은 실행하지 마세요.

최종 보고 형식:
1. 현재 구현 존재 여부
2. 권장 아키텍처
3. case intake schema 초안
4. document draft response schema 초안
5. SCN-004 MVP 범위
6. 구현한다면 파일 단위 작업 계획
7. 이번 세션에서 실제 변경한 파일
8. 다음 세션 프롬프트가 필요하면 제공
```
