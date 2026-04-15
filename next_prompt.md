RAG refinement를 진행해줘. 계획만 말하지 말고 바로 구현하고, 가능한 범위까지 직접 실행/검증까지 해줘.

단, 이번 세션은 **failure-mode split + low-risk fixes first** 기준이다. decomposition-first가 아니다.
실행 순서는 02_rag_strategy.md의 2026-04-15 전략 전환 기준을 따른다.

먼저 읽을 문서:
1. AGENTS.md
2. CLAUDE.md
3. backend/CLAUDE.md
4. docs/planning/00_project_overview.md
5. docs/planning/02_rag_strategy.md   ← 2026-04-15 재정렬 기준
6. docs/planning/04_architecture.md
7. docs/planning/05_eval_plan.md
8. docs/planning/10_backend_retrieval_plan.md
9. docs/ops/task6_answer_generation_status.md
10. docs/planning/12_scenario_expansion_plan.md

그 다음 실제로 확인할 것:
- backend/app/services/retrieval.py
- backend/app/services/answer_generation.py
- backend/app/services/embedding.py   (LEGAL_QUERY_HINT_RULES 확장 대상)
- backend/app/routers/retrieval.py
- backend/app/routers/answer.py
- backend/verify/check_retrieval.py
- backend/verify/check_answer_generation.py
- eval/run_retrieval_eval.py
- eval/run_answer_eval.py
- eval/scenario_demo_question_sets_v1.json
- backend/data/law_chunks/all_chunks.json
- 현재 PostgreSQL law_chunks 상태

현재 확정 상태:
- source of truth: backend/data/law_chunks/all_chunks.json
- selected_as_of: 2026-04-11
- current live chunks: 1722
- PostgreSQL law_chunks: 1722
- embedding populated: 1722 / 1722
- retrieval MVP 완료
- grounded answer generation 완료
- citation grounding / timeout / eval hardening 완료
- scenario coverage audit 완료

현재 baseline:
- retrieval eval:
  - hit@1 = 51/60 (85.00%)
  - hit@3 = 59/60 (98.33%)
  - hit@5 = 60/60 (100.00%)
- answer eval:
  - items_answered = 60/60
  - JSON/schema failure = 0
  - timed_out_ids = []
  - citation_grounding_clean = 60/60
  - gold_citation_hit = 60/60   ← 단일 gold 지표. multi-citation survival 보장 아님 (02 각주 참조)
  - expected_point_strict_coverage = 117/153
  - failures_or_partial_coverage = 26

이번 세션의 직접 대상:
- SCN-001
- SCN-004
- SCN-005

이번 세션에서 직접 대상이 아닌 것:
- SCN-002
  - 현재는 설명형 Before 데모 범위로 고정
  - 연도별 최저임금 자동 비교 / 단순노무 직종 자동 판정은 현재 범위 밖
- SCN-003
  - 이번 턴에서는 추가 작업 없이 유지

핵심 목표:
1. 현재 vector-only retrieval + answer 구조를 RAG refinement해서
   - SCN-001 Full 질의 안정성 개선 (Step 4, 조건부)
   - SCN-004 제23조 등 실체적 조문이 answer cited_articles에서 더 잘 살아남기 (Step 0 재현 시 Step 3로 진행)
   - SCN-005 가족돌봄 / 서면 통보 / 불리한 처우 금지 surface 개선 (Step 1)
   - baseline 117/153 개선 (Step 2)
2. grounding safety는 절대 유지
3. baseline answer eval 성능을 악화시키지 말 것
4. scenario demo question set 기준으로 실제 개선을 보여줄 것

실행 순서 (02_rag_strategy.md Stepwise Gates를 그대로 따른다):

Step 0. SCN-004 citation survival 재현 확인 (게이트)
  - scenario_demo_question_sets_v1.json의 SCN-004 combined / procedure / unpaid 질의를 돌려서
    근로기준법 제23조가 retrieval top-k에는 있으나 answer cited_articles에서 빠지는 현상이
    실제로 재현되는지 확인
  - 재현되면 Step 3를 후속 실행 항목으로 유지
  - 재현되지 않으면 Step 3를 이번 세션에서 자동 스킵
  - 이 단계는 측정만 수행. 코드 변경 없음.

Step 1. 좁은 phrasing normalization
  - 대상: SCN-005 (가족돌봄 / 서면 통보 / 불리한 처우 금지)
  - 구현 범위: backend/app/services/embedding.py의 LEGAL_QUERY_HINT_RULES에 row 추가 수준
  - 새 구조 도입 금지. 광범위한 synonym 주입 금지.
  - 추가 후 baseline 60 + SCN-005 smoke 재측정
  - Gate: citation_grounding_clean = 60/60, gold_citation_hit = 60/60, JSON/schema failure = 0, timeout = 0.
    hit@1 ±1 허용, baseline 117/153 유지 또는 개선.

Step 2. answer-side deterministic hardening
  - 대상: baseline 117/153 잔존 partial (KLS-EVAL-010 / 017 / 058 류 긴 조문 / 하위 항목 열거형)
  - 구현 범위: grounded clause enumeration / ranking / 숫자·기간·예외·절차·범위 surface 보강
  - Guardrail: retrieved context에 없는 숫자/기간/예외 생성 금지. grounded_context_ids 기준 citation leak 차단 유지.
  - 추가 후 baseline 60 + 관련 약한 문항 재측정
  - Gate: citation_grounding_clean = 60/60, gold_citation_hit = 60/60, JSON/schema failure = 0, timeout = 0.
    hit@1 / hit@3 / hit@5 동일 유지 (retrieval 변경 아님).

Step 3. (조건부) conservative citation-diversity / coverage-aware rerank
  - Step 0에서 재현 확인된 경우에만 진행
  - MMR 람다 보수적(>= 0.85)에서 시작. gold 밀림 없는지 실측.
  - 추가 후 baseline 60 + SCN-004 smoke 재측정
  - Gate: gold_citation_hit = 60/60, citation_grounding_clean = 60/60, hit@3 동일 유지.
    hit@1 -1 허용 (단, hit@3 유지), baseline 117/153 유지.

Step 4. selective decomposition (conditional escalation)
  - 대상: SCN-001 Full류 multi-issue 질의에 한정
  - Trigger 예시 (구현 시 파라미터 확정): 질문 길이 >= 임계값, 법령명 2개 이상 언급, composition 마커 다수
  - Trigger 미발동 질의에는 현재 단일 retrieval 경로 유지
  - 추가 후 baseline 60 + SCN-001 Full smoke 재측정
  - Gate: citation_grounding_clean = 60/60, gold_citation_hit = 60/60, JSON/schema failure = 0, timeout = 0.
    trigger 미발동 질의에 영향 없어야 함.

중요 제약:
- model swap 금지
- embedding model 변경 금지
- BM25 / hybrid retrieval 대규모 도입 금지
- frontend 대규모 작업 금지
- OCR / 문서 자동 생성 기능 구현 금지
- broad refactor 금지
- API contract 임의 변경 금지
- 검색 결과에 없는 citation 인용 금지
- cited_articles 없는 법률 응답 금지
- answer text explicit citation grounding 검증 유지
- grounded_context_ids 기준 citation leak 금지
- article / clause exactness 완화 금지
- data/legalize-kr/ 직접 수정 금지
- selected_as_of = 2026-04-11 frozen corpus 기준 유지

측정축 (02_rag_strategy.md Success Criteria 준수):
- 측정축 1 — baseline 60 eval: expected_point_strict_coverage 117/153 개선, grounding / gold / schema / timeout 유지
- 측정축 2 — scenario smoke: SCN-001 Full, SCN-004 (Step 0 재현 시), SCN-005 서면통보 surface
- 두 축은 독립이다. 한쪽 성과로 다른 쪽을 대체해 판정하지 않는다.

우선 검증했으면 하는 것:
1. PostgreSQL readiness
2. scenario_demo_question_sets_v1.json 기준 retrieval / answer smoke
3. Step 0 — SCN-004 제23조 citation survival 재현 확인
4. 각 Step 적용 후 baseline 60 (limit 20 또는 full 60) + 관련 scenario smoke 재측정
5. Step별 gate 통과 여부 기록

최소 기대 결과:
- SCN-005 가족돌봄 / 서면 통보 / 불리한 처우 금지 포인트 surface 개선 (Step 1)
- baseline 117/153 개선 (Step 2)
- Step 0 재현된 경우 SCN-004 제23조 multi-citation survival 개선 (Step 3)
- Step 4 진행한 경우 SCN-001 Full 질의 안정성 개선
- 전 단계에서 grounding clean / gold citation hit 유지
- baseline 60 성능 악화 없음

마지막 보고 형식:
1. 변경 파일
2. 각 Step별로 어떤 RAG refinement를 넣었는지 (또는 Step 0 결과로 스킵했는지)
3. Step별 gate 통과 여부
4. scenario별 실제 실행 결과 (SCN-001 / SCN-004 / SCN-005)
5. baseline eval 영향 (측정축 1)
6. 남은 blocker / 리스크

중요:
- 이번 세션은 source expansion이 아니라 RAG refinement 세션이다.
- SCN-002는 현재 범위 밖이므로 건드리지 말 것.
- broad하게 흔들지 말고, failure mode별로 대응 수단이 다르다는 점을 유지할 것.
- decomposition은 기본 경로가 아니라 Step 4 conditional escalation이다.
- 각 Step은 single change → baseline + scenario 재측정 → gate 통과 → 다음 단계 진행 순서를 지킬 것.
