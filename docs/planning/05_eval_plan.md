# Eval Plan

## Purpose

현재 MVP 단계에서 가장 먼저 검증할 것은 "현재 보유한 법령 청크 범위 안에서 RAG가 올바른 조문을 검색하고, 그 조문만 근거로 답하는가"이다.

이 문서는 현재 저장소에 추가된 초기 in-scope eval 셋의 작성 기준과 사용 방법을 정리한다.

## Current Scope

- eval source chunk file: `backend/data/law_chunks/all_chunks.json`
- current chunk file `selected_as_of`: `2026-04-11`
- current live chunk count: `1722`
- eval dataset file: `eval/mvp_in_scope_eval_v1.json`
- current item count: `60`

현재 eval 셋은 아래 8개 법령군만 대상으로 한다.

- `근로기준법`
- `최저임금법`
- `근로자퇴직급여보장법`
- `남녀고용평등과일ㆍ가정양립지원에관한법률`
- `산업안전보건법`
- `산업재해보상보험법`
- `외국인근로자의고용등에관한법률`
- `중대재해처벌등에관한법률`

주의:

- current live corpus는 scenario expansion 결과 장애인 관련 법령 chunk까지 포함해 `1722`개다.
- 그러나 현재 `eval/mvp_in_scope_eval_v1.json`은 여전히 기존 8개 법령군, 60문항 baseline을 기준으로 유지한다.
- `SCN-001`~`SCN-005` 시나리오 검증은 이 eval 셋과 별도의 scenario smoke 검증으로 관리한다.

중요:

- 현재 eval 셋은 모두 `in-scope` 질문만 포함한다.
- 즉, "현재 청크 안에 실제로 존재하는 citation label로 답할 수 있는 질문"만 넣었다.
- out-of-scope 거절 평가셋은 별도 파일로 분리하는 것이 맞다.

## Why This Eval Was Created First

현재 프로젝트는 데이터 확장보다 MVP 안정성 검증이 우선이다.

그래서 eval 목표도 다음 순서로 두었다.

1. 검색이 맞는 조문을 가져오는가
2. 답변이 검색된 조문에만 근거하는가
3. 현재 범위를 벗어나는 법률/절차를 지어내지 않는가

즉, "좋은 문장 생성"보다 먼저 "정답 조문 retrieval"과 "citation grounding"을 본다.

## Dataset Creation Method

이번 eval 셋은 아래 절차로 만들었다.

1. `backend/data/law_chunks/all_chunks.json`에서 실제 `citation_label` 목록과 조문 본문을 확인했다.
2. 각 법령군별 주요 주제와 자주 묻는 사용자 질문 패턴을 뽑았다.
3. 질문마다 현재 청크 안에 있는 조문으로만 답할 수 있는지 확인했다.
4. 모호하거나 현재 데이터만으로는 답하기 어려운 질문은 제외했다.
5. 각 문항마다 `gold_citations`와 `expected_points`를 수동으로 부여했다.
6. retrieval에서 헷갈릴 수 있는 조문은 `confusable_citations`로 따로 기록했다.
7. 마지막으로 JSON 파싱과 gold citation 존재 여부를 검증했다.

핵심 원칙은 다음과 같다.

- 현재 청크 범위를 벗어나는 질문은 넣지 않는다.
- 법률 상담에서 실제로 많이 나올 만한 생활형 질문을 우선한다.
- 단순 조회형과 시나리오형을 함께 넣는다.
- 같은 법령 안에서도 retrieval이 헷갈릴 만한 경계 질문을 일부 포함한다.
- gold citation은 실제 현재 chunk label과 완전히 일치해야 한다.

## Item Design Principles

각 문항은 아래 기준으로 만들었다.

### 1. Direct Lookup

조문 자체를 바로 찾으면 되는 질문.

예:

- 소멸시효가 몇 년인지
- 급여 종류가 무엇인지
- 정의 조문이 무엇인지

목적:

- embedding + retrieval의 기본 정확도 확인

### 2. Scenario Single

하나의 핵심 조문으로 대부분 답할 수 있는 생활형 질문.

예:

- 서면 근로조건 명시를 안 한 경우
- 해고 예고 없이 즉시 해고한 경우
- 임금명세서를 안 준 경우
- 성희롱 예방교육을 안 한 경우

목적:

- 자연어 질문이 적절한 조문으로 연결되는지 확인

### 3. Scenario Multi

복수 조문을 함께 찾아야 제대로 답할 수 있는 질문.

예:

- 외국인근로자 사업장 변경 요건 + 기한 + 횟수 제한
- 가족돌봄휴직 + 가족돌봄휴가 + 불이익 금지
- 중대재해 의무 + 시행령상 안전보건관리체계

목적:

- top-k retrieval과 citation composition이 함께 작동하는지 확인

## Dataset Schema

각 문항은 아래 필드를 가진다.

- `id`: 안정적인 문항 식별자
- `bucket`: 상위 평가 영역
- `topic`: 세부 주제
- `question_type`: `direct_lookup` / `scenario_single` / `scenario_multi`
- `difficulty`: `easy` / `medium` / `hard`
- `question`: 실제 사용자 질문 형태
- `gold_citations`: 정답으로 간주할 citation label 목록
- `primary_citation`: 대표 citation label
- `expected_points`: 답변에 포함되어야 할 핵심 포인트
- `confusable_citations`: retrieval 시 혼동되기 쉬운 조문

이 구조는 retrieval 평가와 answer 평가를 모두 염두에 둔 것이다.

## Current Coverage

### bucket distribution

- `labor_standards`: 13
- `minimum_wage`: 4
- `retirement_benefits`: 5
- `equality_and_family`: 11
- `occupational_safety_and_health`: 9
- `workers_compensation`: 6
- `foreign_workers`: 8
- `serious_accident_punishment`: 4

### question type distribution

- `scenario_single`: 42
- `scenario_multi`: 14
- `direct_lookup`: 4

### difficulty distribution

- `easy`: 23
- `medium`: 31
- `hard`: 6

의도:

- MVP 단계에서는 실제 사용자 질문과 유사한 `scenario_single` 비중을 높인다.
- retrieval 조합 능력을 보기 위해 `scenario_multi`를 일부 포함한다.
- 완전 초반 단계이므로 지나치게 많은 `hard` 문항은 넣지 않는다.

## What Was Explicitly Excluded

아래 영역은 현재 eval 셋에서 제외했다.

- 출입국 행정 실무 전반
- 체류자격 세부 절차
- 실제 민원서류 작성 방법
- 판례 기반 해석
- 행정해석 / 고시 / FAQ 전반
- 현재 데이터셋 밖 기관 절차 문서

이 질문들은 지금 데이터 범위를 넘거나, 조문만으로는 답변 안정성이 낮기 때문이다.

## Evaluation Targets

이 eval 셋으로 최소 아래 4가지를 본다.

### 1. Retrieval Hit

- `gold_citations` 중 하나 이상이 top-k 안에 들어오는지 확인

### 2. Citation Match

- 최종 답변의 `cited_articles`가 gold citation과 얼마나 일치하는지 확인

### 3. Groundedness

- 검색 결과에 없는 조문을 임의로 인용하지 않았는지 확인

### 4. Answer Coverage

- `expected_points`를 얼마나 충족했는지 확인

## Current Answer Baseline (2026-04-16)

full 60 live answer eval 기준:

- `items_answered = 60/60`
- `JSON/schema failure = 0`
- `timed_out_ids = []`
- `citation_grounding_clean = 60/60`
- `gold_citation_hit = 60/60`
- `expected_point_strict_coverage = 137/153`
- `failures_or_partial_coverage = 16`

개선 경과:

- strict coverage: `84/153 -> 107/153 -> 117/153 -> 122/153 -> 124/153 -> 126/153 -> 137/153`
- partial bucket: `36 -> 30 -> 26 -> 24 -> 23 -> 16`

현재 잔존 약점은 retrieval miss보다 answer-side coverage다. 특히 숫자/기간/예외/범위 열거형 질문과 긴 조문 / subchunk 조합에서 누락이 남는다.

## Minimal Success Criteria For MVP

초기 MVP 기준으로는 아래 정도를 1차 목표로 둔다.

- top-5 retrieval에서 `gold_citations` hit rate 확인
- 법률 답변에 `cited_articles`가 항상 포함되는지 확인
- `gold_citations` 밖의 조문 환각이 없는지 확인
- 자주 나올 질문군에서 `expected_points` 누락이 과도하지 않은지 확인

정량 기준은 retrieval/answer runner가 만들어진 뒤 실제 측정값을 보고 고정하는 것이 적절하다.

현재 실무 기준:

- grounding clean / gold citation hit은 유지된 상태에서 coverage를 추가 개선하는 것이 다음 단계 목표
- eval runner는 partial coverage가 남으면 non-zero exit로 종료될 수 있음

## Current Retrieval Baseline (2026-04-13)

`eval/run_retrieval_eval.py --top-k 5 --ef-search 100` 실행 기준:

- `hit@1 = 51/60 (85.00%)`
- `hit@3 = 59/60 (98.33%)`
- `hit@5 = 60/60 (100.00%)`

question type breakdown:

- `direct_lookup`: `hit@1 2/4`, `hit@3 4/4`, `hit@5 4/4`
- `scenario_multi`: `hit@1 13/14`, `hit@3 14/14`, `hit@5 14/14`
- `scenario_single`: `hit@1 36/42`, `hit@3 41/42`, `hit@5 42/42`

보정 메모:

- 초기 실행에서 `KLS-EVAL-019`가 top-5 miss였음
- query embedding 단계에서 생활어를 법조문 표현으로 보강하는 최소 query hint normalization을 추가한 뒤 `hit@5`를 `60/60`으로 끌어올림

## Validation Already Completed

현재 `eval/mvp_in_scope_eval_v1.json`에 대해 아래 검증을 완료했다.

- JSON 파싱 통과
- 총 문항 수 `60`
- ID 중복 없음
- `gold_citations` 누락 없음
- 모든 `gold_citations`가 현재 `backend/data/law_chunks/all_chunks.json` 안에 실제로 존재함

즉, 현재 파일은 "지금 있는 데이터 기준으로 실제 평가 가능한 상태"다.

## Maintenance Rules

- 청킹을 다시 돌려 `citation_label`이 바뀌면 eval 셋도 함께 갱신해야 한다.
- `selected_as_of`가 바뀌면 문서와 eval 메타데이터를 함께 업데이트해야 한다.
- 신규 데이터셋을 추가할 때는 기존 `v1`을 덮어쓰기보다 새 버전을 추가하는 것이 안전하다.
- out-of-scope eval, abstention eval, multilingual eval은 별도 파일로 분리한다.

## Next Step

다음 구현 단계는 아래 순서가 적절하다.

1. answer generation 결과의 `cited_articles` 비교
2. `expected_points` 기반의 간이 채점 규칙 추가
3. out-of-scope 거절 평가셋 분리
4. multilingual eval 분리
5. retrieval parameter / hint normalization 회귀 평가 추가
