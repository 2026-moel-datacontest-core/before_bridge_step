현재 RAG refinement landing은 완료 상태다. 이 파일은 **다음 세션이 필요할 때만** 사용할 현재 handoff prompt다.

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

현재 landed path:

- Step 1 phrasing normalization 적용 완료
- Step 2 answer-side deterministic hardening 적용 완료
- Step 3 rerank 미적용
- Step 4 decomposition 미적용

현재 해석:

- retrieval보다 answer-side selection / finalization이 주 병목이었다.
- `SCN-004` 제23조 survival은 현재 landed path에서 안정적이다.
- `SCN-005` 가족돌봄 / 서면 통보 / 불리한 처우 / companion citation은 현재 landed path에서 안정적이다.
- timeout 이슈는 clean rerun 기준 재현되지 않았으므로 현재는 runtime caveat로만 관리한다.

## 남은 partial IDs

- `KLS-EVAL-003`
- `KLS-EVAL-007`
- `KLS-EVAL-013`
- `KLS-EVAL-014`
- `KLS-EVAL-016`
- `KLS-EVAL-019`
- `KLS-EVAL-021`
- `KLS-EVAL-027`
- `KLS-EVAL-028`
- `KLS-EVAL-031`
- `KLS-EVAL-038`
- `KLS-EVAL-044`
- `KLS-EVAL-047`
- `KLS-EVAL-050`
- `KLS-EVAL-053`
- `KLS-EVAL-054`

## 다음 세션이 필요할 때의 원칙

- immediate mandatory work는 없다.
- 후속 작업이 필요하면 **remaining partial에 대한 answer-side cleanup만** 진행한다.
- retrieval / rerank / decomposition은 새 증거가 없으면 건드리지 않는다.
- `SCN-002`는 설명형 Before 데모 범위로 유지한다.
- broad refactor, model swap, embedding model 변경은 하지 않는다.

## 선택적 후속 세션 프롬프트

필요할 때만 아래 지시로 시작한다.

```md
이번 세션은 landed RAG refinement의 선택적 후속 세션이다.

목표:
- remaining partial IDs만 좁게 개선
- retrieval / rerank / decomposition은 건드리지 않음
- `backend/app/services/answer_generation.py` 중심의 최소 수정만 허용

먼저 읽을 것:
1. AGENTS.md
2. CLAUDE.md
3. backend/CLAUDE.md
4. docs/planning/02_rag_strategy.md
5. docs/ops/task6_answer_generation_status.md
6. docs/planning/05_eval_plan.md

현재 baseline:
- retrieval: `51/60`, `59/60`, `60/60`
- answer: `137/153`, `16 partial`, grounding/gold/schema/timeout clean

직접 대상:
- `KLS-EVAL-003`
- `KLS-EVAL-007`
- `KLS-EVAL-013`
- `KLS-EVAL-014`
- `KLS-EVAL-016`
- `KLS-EVAL-019`
- `KLS-EVAL-021`
- `KLS-EVAL-027`
- `KLS-EVAL-028`
- `KLS-EVAL-031`
- `KLS-EVAL-038`
- `KLS-EVAL-044`
- `KLS-EVAL-047`
- `KLS-EVAL-050`
- `KLS-EVAL-053`
- `KLS-EVAL-054`

sentinel regression set:
- `KLS-EVAL-010`
- `KLS-EVAL-058`
- `SCN-005-Q3`
- `SCN-004-Q2`

중요 제약:
- code/document 변경은 최소 범위만
- retrieval.py / embedding.py 수정 금지
- Step 3 rerank 금지
- Step 4 decomposition 금지
- grounding clean / gold hit / schema / timeout 회귀 금지
- raw / expanded / grounded semantics 유지

실행 방식:
1. targeted failure items + sentinel만 먼저 반복
2. 개선 후보가 나오면 그때만 full 60 실행
3. regression이 나면 즉시 롤백

마지막 보고 형식:
1. 변경 파일
2. failure pattern
3. narrow fix
4. targeted 결과
5. sentinel regression 결과
6. full 60 영향
7. gate 판정
```
