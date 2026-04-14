# RAG Strategy

기준일: `2026-04-14`

## 목적

- 현재 live corpus / retrieval / answer baseline을 기준으로 다음 RAG 개선 방향을 고정
- 어떤 문제를 retrieval 구조 개선으로 풀고, 어떤 문제를 현재 범위 밖으로 둘지 구분
- 다음 세션에서 broad refactor 없이 `query decomposition -> sub-query retrieval -> union/dedupe -> grounded answer` 방향으로 진행할 수 있게 기준선을 정리

관련 기준 문서:

- [Task 6 Answer Generation Status](/home/jongwon/personal_project/law_main_road/docs/ops/task6_answer_generation_status.md)
- [Scenario Expansion Plan](/home/jongwon/personal_project/law_main_road/docs/planning/12_scenario_expansion_plan.md)
- [Eval Plan](/home/jongwon/personal_project/law_main_road/docs/planning/05_eval_plan.md)

---

## Current Baseline

### Data Source

- source: `data/legalize-kr/`
- processed source of truth: `backend/data/law_chunks/all_chunks.json`
- database target: PostgreSQL `law_chunks`
- current live corpus: `1722` chunks
- `selected_as_of = 2026-04-11`

현재 live corpus는 원래 baseline `1713` chunks에 더해, `SCN-003` 대응으로 아래 법령군을 최소 범위로 추가 반영한 상태다.

- `장애인차별금지 및 권리구제 등에 관한 법률`
- `장애인고용촉진 및 직업재활법`

중요:

- `data/legalize-kr/` raw source HEAD가 더 최신이더라도, 현재 서비스 기준은 `selected_as_of = 2026-04-11` frozen corpus다.
- 이후 데이터 보강 시에도 snapshot 혼합 없이 현재 source of truth와 DB 정합성을 유지해야 한다.

### Chunk Unit

- 기본 단위: 조문 단위
- 긴 조문: 항 / 서브청크 단위 분리 허용
- citation label / source metadata / article_ordinal 유지
- answer generation은 현재 grounded clause extraction과 제한적 adjacent expansion을 이미 사용 중

### Retrieval / Answer Baseline

- retrieval: vector-only (`gemini-embedding-001` + pgvector HNSW)
- answer: grounded answer generation with `gemini-2.5-flash`
- citation rule:
  - 검색 결과에 없는 citation 인용 금지
  - `cited_articles` 포함 응답 구조 유지
  - answer text도 explicit citation grounding 검증 통과 필요

현재 성능 기준:

- retrieval eval:
  - `hit@1 = 51/60 (85.00%)`
  - `hit@3 = 59/60 (98.33%)`
  - `hit@5 = 60/60 (100.00%)`
- answer eval:
  - `items_answered = 60/60`
  - `JSON/schema failure = 0`
  - `timed_out_ids = []`
  - `citation_grounding_clean = 60/60`
  - `gold_citation_hit = 60/60`
  - `expected_point_strict_coverage = 117/153`
  - `failures_or_partial_coverage = 26`

---

## Current Diagnosis

현재 병목은 크게 두 종류다.

### A. Retrieval / Context Composition 문제

복합 질문에서 필요한 논점이 한 번에 다 안 잡히는 경우가 있다.

대표 예:

- `SCN-001`
  - Before / After를 분리하면 잘 되지만, Full 단일 질문에서는 `근로기준법 제17조`, `외국인고용법 제9조`, `제22조(차별 금지)`가 밀릴 수 있음
- `SCN-004`
  - `근로기준법 제23조`가 retrieval에는 잡혀도 answer cited_articles에서 빠질 수 있음
- `SCN-005`
  - 가족돌봄 질문에서 `서면 통보` 포인트는 phrasing에 따라 잘 안 올라올 수 있음

이 문제는 현재 데이터가 없어서라기보다, query shaping / retrieval ranking / answer-side selection의 문제에 가깝다.

### B. Source Coverage 문제

현재 corpus만으로는 grounded하게 답하기 어려운 질문도 있다.

대표 예:

- `SCN-002`
  - 수습 감액 규칙 자체는 설명 가능
  - 다만 “올해 최저임금보다 낮은 시급인지 자동 판정”은 현재 범위 밖으로 두는 편이 맞다

이 문제는 retrieval tuning만으로 해결되지 않는다. 먼저 source 범위를 넓히거나 structured supplement를 따로 둬야 한다.

---

## Strategy Split

다음 단계에서 해결 전략은 아래처럼 분리한다.

### 1. RAG Refinement로 해결할 대상

- `SCN-001`
- `SCN-004`
- `SCN-005`
- baseline eval 중 복합 retrieval / 긴 조문 열거형 커버리지 문제

핵심 수단:

- query decomposition
- sub-query별 retrieval
- 결과 union / dedupe
- citation-aware rerank 또는 clause ranking 보강
- answer-side selection 개선

### 2. 현재 범위 밖으로 둘 대상

- `SCN-002`의 연도별 최저임금 자동 비교
- `SCN-002`의 단순노무 직종 자동 판정
- 향후 현재 corpus 밖 기관 절차 / 고시 / 지원 제도 정보가 필요한 시나리오

즉 다음 세션의 RAG 수정은 “현재 데이터가 이미 있는 시나리오를 더 잘 통과시키는 것”에 집중하고, `SCN-002`는 설명형 Before 데모 범위로 유지한다.

---

## Recommended Next Retrieval Architecture

다음 세션의 1차 후보 구조는 아래다.

```text
User query
  -> query normalizer
  -> query decomposition
       - sub_query_1
       - sub_query_2
       - ...
  -> each sub-query retrieval (top_k per branch)
  -> union / dedupe / citation-aware rerank
  -> bounded context assembly
  -> grounded answer generation
  -> cited_articles from grounded context only
```

### Query Decomposition 방향

목표:

- 사용자 질문을 법적 논점 단위로 쪼개기
- 하나의 긴 질문 때문에 특정 핵심 조문이 top-k에서 밀리는 현상 완화

예시:

- `SCN-001 Full`
  - 계약 단계 서면 명시
  - 외국인 고용계약 / 표준계약
  - 기숙사 / 숙소비 공제
  - 차별 / 폭언
  - 사업장 변경 가능성

### Sub-query Retrieval 방향

- 각 sub-query마다 작은 `top_k`로 retrieval
- 전체를 다시 합쳐 candidate pool 형성
- 같은 citation / 같은 article / 같은 parent article 기준 dedupe
- 필요 시 상위 chunk + adjacent chunk를 제한적으로 보강

### Context Assembly 방향

- 무조건 많이 넣는 방식은 피한다
- citation 다양성, 질문 커버리지, 중복 제거를 함께 본다
- 최종 answer context는 grounded citation 추적이 가능한 형태를 유지한다

---

## Non-Goals For Next Session

다음 세션에서 기본적으로 하지 않을 것:

- 모델 교체
- embedding model 교체
- BM25 / hybrid retrieval 대규모 도입
- frontend 대규모 확장
- OCR / 문서 자동 생성 기능 본격 구현
- 새로운 broad schema 변경

판단 이유:

- `gemini-2.5-pro`는 live A/B에서 더 느리고 timeout이 많았으며 품질 우위가 없었다.
- retrieval miss보다 복합 query composition 문제가 더 뚜렷하다.
- 현재는 시스템을 다시 뒤집기보다 retrieval flow를 더 정교하게 만드는 편이 수익이 크다.

---

## Guardrails

- 검색 결과에 없는 조문 인용 금지
- `cited_articles` 없는 법률 응답 금지
- answer text explicit citation grounding 검증 유지
- `grounded_context_ids` 기준 citation leak 금지
- article / clause exactness 완화 금지
- `selected_as_of = 2026-04-11` frozen corpus 기준 유지
- `data/legalize-kr/` 직접 수정 금지
- broad refactor 금지

---

## Success Criteria For Next RAG Session

다음 세션의 성공 기준은 아래처럼 잡는 것이 맞다.

### Scenario 기준

- `SCN-001`
  - Before / After 분리 없이 Full 질의 안정성 개선
- `SCN-004`
  - `근로기준법 제23조` 등 실체적 조문이 answer cited_articles에서도 더 안정적으로 살아남기
- `SCN-005`
  - 가족돌봄 질의에서 `서면 통보`와 `불리한 처우 금지` 포인트가 더 잘 surface되기

### Eval 기준

- current baseline `117/153`, `26 partial`보다 개선
- grounding clean / gold citation hit 유지
- JSON/schema failure `0` 유지
- timeout `0` 유지

즉, 다음 세션 목표는 “안전성을 유지한 채 복합 시나리오 coverage를 올리는 것”이다.

---

## Current Phase

- chunking complete
- DB foundation / ingestion complete
- embedding generation complete
- vector indexing complete
- retrieval MVP complete
- grounded answer generation complete
- answer-side citation grounding / timeout / eval hardening complete
- scenario data coverage audit complete
- scenario demo question sets created
- next:
  - query decomposition
  - sub-query retrieval
  - union / dedupe
  - clause ranking refinement
  - answer-side selection refinement
  - `SCN-002`는 설명형 Before 데모 범위로 유지
