# Eval Dataset

현재 저장소의 MVP용 법령 RAG를 검증하기 위한 eval 자산 모음이다.

## Files

- `mvp_in_scope_eval_v1.json`: 현재 `backend/data/law_chunks/all_chunks.json` 범위 안에서만 답할 수 있는 baseline 60문항 eval 셋
- `scenario_demo_question_sets_v1.json`: `SCN-001`, `SCN-004`, `SCN-005` 데모용 retrieval/answer smoke 질문 세트
- `run_retrieval_eval.py`: retrieval service 기준 `hit@1`, `hit@3`, `hit@5`를 계산하는 runner
- `run_answer_eval.py`: grounded answer의 schema / citation grounding / expected point coverage를 계산하는 runner

## Source Scope

- source chunk file: `backend/data/law_chunks/all_chunks.json`
- selected_as_of in current chunk file: `2026-04-11`
- current live chunk count: `1722`
- baseline eval covered law groups:
  - `근로기준법`
  - `최저임금법`
  - `근로자퇴직급여보장법`
  - `남녀고용평등과일ㆍ가정양립지원에관한법률`
  - `산업안전보건법`
  - `산업재해보상보험법`
  - `외국인근로자의고용등에관한법률`
  - `중대재해처벌등에관한법률`

## Item Schema

### `mvp_in_scope_eval_v1.json`

- `id`: 안정적인 문항 ID
- `bucket`: 상위 평가 영역
- `topic`: 세부 주제
- `question_type`: `direct_lookup` / `scenario_single` / `scenario_multi`
- `difficulty`: `easy` / `medium` / `hard`
- `question`: 실제 사용자 질문 형태
- `gold_citations`: 정답으로 간주할 citation label 목록
- `primary_citation`: 대표 citation label
- `expected_points`: 답변에 포함되어야 하는 핵심 포인트
- `confusable_citations`: retrieval 시 혼동하기 쉬운 조문

### `scenario_demo_question_sets_v1.json`

- `scenario_id`: 시나리오 ID (`SCN-001`, `SCN-004`, `SCN-005`)
- `scenario_type`: `Full` / `After`
- `coverage_status`: 현재 corpus 기준 커버 판정
- `demo_operation_note`: 데모 운영 시 주의 메모
- `questions[*].id`: 질문 ID
- `questions[*].phase`: `before` / `after` / `full`
- `questions[*].label`: 질문 역할 식별자
- `questions[*].stability`: 현재 retrieval/answer 기준 권장 안정성
- `questions[*].recommended_top_k`: smoke 시 권장 `top_k`
- `questions[*].question`: 실제 데모 질문 문안
- `questions[*].expected_citations`: 우선 surface되길 기대하는 citation 목록
- `questions[*].expected_points`: 답변 핵심 포인트
- `questions[*].demo_note`: 운영 메모

## Intended Use

1. retrieval 평가:
   - `mvp_in_scope_eval_v1.json` 기준으로 `gold_citations`가 top-k 안에 들어오는지 확인
2. answer 평가:
   - 답변이 `expected_points`를 충족하는지 확인
   - `gold_citations` 밖 조문을 임의 인용하지 않았는지 확인
3. 데모 smoke:
   - `scenario_demo_question_sets_v1.json`의 질문을 시나리오별 retrieval/answer smoke에 재사용
4. regression 평가:
   - 같은 질문을 반복 실행해 retrieval/citation 안정성 확인
5. document draft QA:
   - document draft 자체는 `backend/verify/check_document_draft.py`를 기준으로 확인
   - RAG service를 수정하지 않은 문서 초안/frontend 작업에서는 full 60 eval을 기본 재실행하지 않음

## Current Retrieval Baseline (2026-04-13)

실행 명령:

```bash
python eval/run_retrieval_eval.py --top-k 5 --ef-search 100 --show-failures 10
```

측정 결과:

- `items = 60`
- `hit@1 = 51/60 (85.00%)`
- `hit@3 = 59/60 (98.33%)`
- `hit@5 = 60/60 (100.00%)`

breakdown:

- `direct_lookup`: `hit@1 2/4`, `hit@3 4/4`, `hit@5 4/4`
- `scenario_multi`: `hit@1 13/14`, `hit@3 14/14`, `hit@5 14/14`
- `scenario_single`: `hit@1 36/42`, `hit@3 41/42`, `hit@5 42/42`

note:

- 초기 실행에서 `KLS-EVAL-019`가 top-5 miss였음
- query embedding 단계의 법률용어 hint normalization 보강 후 `hit@5_failures = 0`

## Current Answer Baseline (2026-04-16)

실행 명령:

```bash
python eval/run_answer_eval.py --top-k 5 --ef-search 100 --limit 60 --show-failures 20
```

측정 결과:

- `items_answered = 60/60`
- `JSON/schema failure = 0`
- `timed_out_ids = []`
- `citation_grounding_clean = 60/60`
- `gold_citation_hit = 60/60`
- `expected_point_strict_coverage = 137/153`
- `failures_or_partial_coverage = 16`

현재 RAG refinement는 landing 완료 상태다. 다음 작업이 frontend/document draft QA만 건드리는 경우, 이 baseline은 재실행보다 회귀 의심 시 재검증 대상으로 본다.

## Notes

- 현재 baseline eval 파일은 모두 `in-scope` 질문만 포함한다.
- out-of-scope 거절 평가셋은 별도로 분리하는 것이 좋다.
- 데모용 질문 세트는 baseline scoring dataset이 아니라 scenario smoke / 발표 시연용 자산이다.
- 문항은 실제 현재 chunk label에 맞춰 작성했기 때문에, 청킹을 다시 돌리거나 snapshot이 바뀌면 함께 갱신해야 한다.
- SCN-004 document draft smoke는 `backend/verify/check_document_draft.py`에 있다.
