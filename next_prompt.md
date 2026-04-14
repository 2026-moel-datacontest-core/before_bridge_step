RAG refinement를 진행해줘. 계획만 말하지 말고 바로 구현하고, 가능한 범위까지 직접 실행/검증까지 해줘.

  먼저 읽을 문서:
  1. AGENTS.md
  2. CLAUDE.md
  3. backend/CLAUDE.md
  4. docs/planning/00_project_overview.md
  5. docs/planning/02_rag_strategy.md
  6. docs/planning/04_architecture.md
  7. docs/planning/05_eval_plan.md
  8. docs/planning/10_backend_retrieval_plan.md
  9. docs/ops/task6_answer_generation_status.md
  10. docs/planning/12_scenario_expansion_plan.md

  그 다음 실제로 확인할 것:
  - backend/app/services/retrieval.py
  - backend/app/services/answer_generation.py
  - backend/app/services/embedding.py
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
    - gold_citation_hit = 60/60
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
     - SCN-001 Full 질의 안정성 개선
     - SCN-004에서 제23조 등 실체적 조문이 answer cited_articles에서도 더 잘 살아남게 개선
     - SCN-005에서 가족돌봄 질의의 서면 통보 / 불리한 처우 금지 포인트가 더 잘 surface되게 개선
  2. grounding safety는 절대 유지
  3. baseline answer eval 성능을 악화시키지 말 것
  4. 가능하면 scenario demo question set 기준으로 실제 개선을 보여줄 것

  권장 방향:
  - query decomposition
  - sub-query별 retrieval
  - 결과 union / dedupe
  - citation-aware rerank 또는 clause ranking 보강
  - answer-side selection 개선
  - 필요하면 query normalization 보강
  - 필요하면 제한적 adjacent context expansion 조정

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

  작업 방식:
  1. 먼저 현재 retrieval/answer 코드와 scenario question set을 읽고 병목을 짧게 정리
  2. SCN-001 / SCN-004 / SCN-005 중심으로 최소 범위 수정
  3. 구현 후 실제 검증
  4. baseline 60문항 answer eval도 가능한 범위에서 다시 돌려서 악화 여부 확인
  5. 마지막에 변경 사항과 검증 결과를 짧게 정리

  우선 검증했으면 하는 것:
  1. PostgreSQL readiness
  2. scenario_demo_question_sets_v1.json 기준 retrieval / answer smoke
  3. SCN-001
     - before / after / full
  4. SCN-004
     - combined / procedure / unpaid
  5. SCN-005
     - parental / family care general / family care with written reason
  6. 가능하면 baseline answer eval limit 20 또는 limit 60 재확인

  최소 기대 결과:
  - SCN-001 Full 질의가 이전보다 안정적으로 핵심 citation을 회수
  - SCN-004에서 제23조가 answer cited_articles에서 더 자주 살아남거나, 최소한 관련 실체적 논점이 더 잘 반영
  - SCN-005에서 가족돌봄 질문의 서면 통보 / 불리한 처우 금지 포인트가 더 잘 surface
  - grounding clean 유지
  - baseline 60 성능 악화 없음

  마지막 보고 형식:
  1. 변경 파일
  2. 어떤 RAG refinement를 넣었는지
  3. scenario별 실제 실행 결과
  4. baseline eval 영향
  5. 남은 blocker / 리스크

  중요:
  - 이번 세션은 source expansion이 아니라 RAG refinement 세션이다.
  - SCN-002는 현재 범위 밖이므로 건드리지 말 것.
  - broad하게 흔들지 말고, SCN-001/004/005 개선에 집중할 것.