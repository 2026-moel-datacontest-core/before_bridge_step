# RAG Strategy

기준일: `2026-04-17`

## 목적

- 현재 live corpus / retrieval / answer baseline을 기준으로 다음 RAG 개선 방향을 고정
- 어떤 문제를 retrieval 구조 개선으로 풀고, 어떤 문제를 answer-side 보강으로 풀고, 어떤 문제를 현재 범위 밖으로 둘지 구분
- RAG refinement landing 이후에는 broad refactor 없이 현재 baseline을 QA 기준선으로 유지

## 전략 전환 요약 (2026-04-15)

이전 기준(2026-04-14)은 `query decomposition -> sub-query retrieval -> union/dedupe -> grounded answer`를 1차 후보로 두었다. 그러나 현재 baseline 숫자(`hit@5 = 100%`, `gold_citation_hit = 60/60`)와 실제 코드 구조를 재검토한 결과, **병목의 중심은 retrieval recall이 아니라 answer-side clause selection**에 가깝다. 이에 따라 다음 원칙으로 재정렬한다.

- decomposition은 **기본 파이프라인이 아니라 conditional escalation path**로 내린다.
- failure mode를 네 축으로 분리하고, 축마다 대응 수단을 다르게 둔다.
- 각 단계는 single change → baseline + scenario 재측정 → gate 통과 → 다음 단계로 진행하는 incremental 구조로 둔다.

## 실행 결과 업데이트 (2026-04-16)

2026-04-15 기준 Step 0~4 전략으로 실제 refinement를 진행했고, 현재 landed path는 다음과 같이 정리된다.

- **Step 0 — SCN-004 citation survival 확인**
  - 초기 targeted 측정에서는 `근로기준법 제23조`가 retrieval top-k에 있으나 answer `cited_articles`에서 탈락하는 현상이 재현됐다.
  - 이후 answer-side hardening이 반영된 현재 landed path에서는 `SCN-004-Q1/Q2` 모두 제23조 survival이 안정적으로 유지된다.
  - 따라서 **Step 3 rerank는 현재 landed code에 포함되지 않았다.**
- **Step 1 — 좁은 phrasing normalization**
  - `LEGAL_QUERY_HINT_RULES`에 가족돌봄 / 육아휴직 관련 좁은 rule을 추가했다.
  - retrieval baseline 회귀 없이 `SCN-005` phrasing sensitivity를 완화했다.
- **Step 2 — answer-side deterministic hardening**
  - focus-aware clause selection, compact matching, incomplete answer recovery, raw/expanded citation semantics 분리, family-care companion citation, weak item 전용 narrow finalization을 단계적으로 반영했다.
  - 긴 조문 / 하위 항목 / 숫자·기간·예외·절차 surface 보강의 대부분이 이 단계에서 해결됐다.
- **Step 3 — conditional rerank**
  - 초기 전략에서는 보류 카드였지만, landed path에서는 미적용이다.
  - 현재 기준으로 citation-diversity / coverage-aware rerank를 도입할 직접 근거가 부족하다.
- **Step 4 — selective decomposition**
  - `SCN-001 Full`은 composition-heavy 질의이므로 After 핵심 SCN 안정화 세션에서 전용 selective decomposition을 좁게 도입했다.
  - 이 경로는 일반 API default 경로에는 발동하지 않고, `top_k >= 8` 및 SCN-001 Full marker 조합이 맞을 때만 발동한다.
  - scenario demo는 `recommended_top_k = 10`을 사용해야 한다.

현재 clean landing verification 기준 baseline은 다음과 같다.

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
  - `expected_point_strict_coverage = 137/153`
  - `failures_or_partial_coverage = 16`

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
  - `expected_point_strict_coverage = 137/153`
  - `failures_or_partial_coverage = 16`

> **`gold_citation_hit = 60/60` 해석 주의.**
> 이 지표는 각 문항에 지정된 **단일 gold citation 하나**가 최종 `cited_articles`에 포함되었는지만 본다. 즉 "gold 1개는 살아남았다"는 뜻이지, retrieval에 잡힌 **그 외 실체적 조문들까지 answer에 살아남았다**는 의미가 아니다. multi-citation survival(예: SCN-004에서 `근로기준법 제23조`가 다른 관련 조문과 함께 유지되는지)은 이 지표로 측정되지 않으며, 필요 시 scenario smoke 또는 별도 citation survival eval로 확인해야 한다.

---

## Current Diagnosis

현재 병목은 크게 두 종류다.

### A. Retrieval / Ranking / Answer-side selection 문제

현재 데이터가 없어서가 아니라 **query shaping / ranking / answer-side clause selection**의 문제다. 다만 하나의 증상으로 뭉치면 대응이 엇나가므로, 아래 네 축으로 failure mode를 분리한다.

#### Failure mode split

- **SCN-001 = composition 문제.**
  - Before / After를 분리하면 잘 되지만, Full 단일 질문에서는 `근로기준법 제17조`, `외국인고용법 제9조`, `제22조(차별 금지)` 등이 top-k에서 밀릴 수 있음.
  - 한 query에 법적 논점 다수가 섞여 embedding이 한쪽으로 편향되는 composition 문제로 본다.
  - 대응 축: **selective decomposition (conditional escalation)**.
- **SCN-004 = citation survival 이슈 (현재 landed path에서는 안정화).**
  - 초기 targeted 측정에서는 `근로기준법 제23조`가 retrieval에는 잡혀도 최종 `cited_articles`에서 빠지는 현상이 재현됐다.
  - 하지만 현재 landed path에서는 `SCN-004-Q1/Q2` 모두 제23조 survival이 유지되며, Step 3 rerank 없이 해결됐다.
  - 따라서 현시점 권장 대응은 **Step 3 도입이 아니라 현재 answer-side 경로 유지**다. citation survival 이슈가 다시 재현될 때만 rerank를 재검토한다.
- **SCN-005 = phrasing sensitivity 문제.**
  - 가족돌봄 질문에서 `서면 통보`, `불리한 처우 금지` 포인트가 phrasing에 따라 top-k에 안 올라오는 경우가 있음.
  - 대응 축: **좁은 범위의 phrasing normalization**. 기존 `backend/app/services/embedding.py`의 `LEGAL_QUERY_HINT_RULES`에 row 추가 수준으로 스코프를 고정한다. 신규 구조 도입이 아니다.
- **baseline `137/153` 잔존 partial = answer-side enumeration / completeness 문제.**
  - 현재 남은 partial은 `KLS-EVAL-003`, `007`, `013`, `014`, `016`, `019`, `021`, `027`, `028`, `031`, `038`, `044`, `047`, `050`, `053`, `054`에 집중된다.
  - 공통 패턴은 여전히 **긴 조문 / 하위 항목 열거형에서 숫자·기간·예외·절차·범위 surface가 불완전**하거나 answer finalization이 덜 직접적인 경우다.
  - retrieval / ranking 변경으로는 풀리지 않으며 answer-side clause selection과 prompt 설계의 문제에 더 가깝다.
  - 대응 축: **answer-side deterministic hardening** (grounded clause enumeration 보강, 숫자·기간·예외 surface 룰 강화). 점수 기여도가 가장 클 가능성이 높다.

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
- baseline eval 중 긴 조문 열거형 coverage 문제

핵심 수단 (2026-04-16 landed 결과 반영):

1. **Step 0 — SCN-004 재현 확인 (게이트).** 실제 제23조 citation drop이 재현되는지 targeted smoke/eval로 먼저 확인. 재현 안 되면 Step 3 자동 스킵.
2. **Step 1 — 좁은 phrasing normalization.** 구현 완료. SCN-005 중심.
3. **Step 2 — answer-side deterministic hardening.** 구현 완료. baseline `117/153 -> 137/153` 개선의 주력.
4. **Step 3 — (조건부) conservative citation-diversity / coverage-aware context assembly.** 현재 landed path에서는 미적용.
5. **Step 4 — selective decomposition.** 일반 경로에는 미적용. After 핵심 `SCN-001 Full` demo path에 한해 `top_k >= 8` 조건부로 적용.

### 2. 현재 범위 밖으로 둘 대상

- `SCN-002`의 연도별 최저임금 자동 비교
- `SCN-002`의 단순노무 직종 자동 판정
- 향후 현재 corpus 밖 기관 절차 / 고시 / 지원 제도 정보가 필요한 시나리오

즉 다음 세션의 RAG 수정은 “현재 데이터가 이미 있는 시나리오를 더 잘 통과시키는 것”에 집중하고, `SCN-002`는 설명형 Before 데모 범위로 유지한다.

---

## Recommended Next Retrieval Architecture

기본 파이프라인은 현재 구조를 유지한다. decomposition은 조건부 branch로 붙는다.

```text
User query
  -> query normalizer (phrasing hints 포함, 기존 LEGAL_QUERY_HINT_RULES 확장)
  -> [선택] decomposition trigger 평가
       - trigger hit: sub-query decomposition → 각 branch retrieval → union/dedupe
       - trigger miss: 단일 retrieval (현재 경로 유지)
  -> [조건부] conservative citation-diversity / coverage-aware rerank
       - Step 0 재현 통과 시에만 활성화
  -> bounded context assembly (grounded citation 추적 유지)
  -> grounded answer generation (answer-side deterministic hardening 적용)
  -> cited_articles from grounded context only
```

### Decomposition Trigger (conditional escalation)

decomposition은 기본 경로가 아니라 **escalation path**다. 아래 후보 룰 중 하나 이상 해당할 때만 발동한다. (문서 단계 예시이며 실제 파라미터는 구현 시 확정.)

- 호출 `top_k`가 trigger minimum 이상이어야 함. 현재 SCN-001 Full selective decomposition은 `top_k >= 8`일 때만 발동한다.
- 질문 길이가 임계값 이상 (예: `len(query) >= N` 문자)
- 법령명이 2개 이상 언급됨
- composition 마커 (`그리고`, `또한`, `및`) 다수 또는 법적 쟁점 키워드가 복수 영역에 걸침
- `SCN-001 Full` 류 multi-issue 데모 질의

Trigger 미발동 질의는 현재 단일 retrieval 경로를 그대로 쓴다. 단순 질문에 sub-query가 남발되지 않도록 하는 것이 핵심이다.

### top_k 운영 기준

- 일반 `/api/v1/answer` 기본값은 `top_k = 5`로 유지한다.
  - 이유: 일반 단일 쟁점 질의에서는 latency와 context noise를 낮추는 것이 더 중요하다.
  - baseline 60 eval도 이 기본 경로 안정성을 기준으로 본다.
- SCN demo / scenario smoke 경로는 `eval/scenario_demo_question_sets_v1.json`의 `recommended_top_k`를 따라야 한다.
  - 현재 `SCN-001`, `SCN-004`, `SCN-005` demo questions는 `recommended_top_k = 10`이다.
  - 특히 `SCN-001 Full` selective decomposition은 `top_k >= 8`에서만 발동하므로, `top_k`를 생략해 API default `5`로 호출하면 개선 경로가 발동하지 않는다.
- 따라서 데모 UI / scenario runner / 직접 API smoke에서는 반드시 payload에 `top_k: 10`, `ef_search: 100`을 명시한다.
- backend global default를 `10`으로 올리지는 않는다. demo-only requirement로 관리한다.

### Phrasing Normalization 범위

- 기존 `backend/app/services/embedding.py`의 `LEGAL_QUERY_HINT_RULES` 확장 수준으로만.
- SCN-005 중심 (가족돌봄 / 서면 통보 / 불리한 처우 금지 phrasing).
- 광범위한 synonym 주입 금지. 각 rule 추가마다 baseline 재측정으로 `hit@1` 회귀 없는지 확인.

### Answer-side Deterministic Hardening 범위

- 긴 조문 / 하위 항목 / 숫자·기간·예외·절차·범위 surface 보강.
- grounded clause enumeration / ranking 로직의 결정적 보강.
- **Guardrail**: surface 강제 중 retrieved context에 없는 숫자/기간/예외를 생성하지 않도록 grounding 경로 유지. `citation_grounding_clean`, `grounded_context_ids` 기준 citation leak 금지는 절대 완화되지 않는다.

### Conditional Citation-diversity / Coverage-aware Rerank 범위 (Step 0 통과 시)

- MMR 람다는 **보수적으로** (예: `lambda >= 0.85`) 시작하여 gold chunk가 top-k 밖으로 밀리지 않는지 실측.
- same article cluster 억제가 gold_citation_hit 60/60을 깨뜨리면 즉시 롤백.
- citation 다양성, 질문 커버리지, 중복 제거를 함께 본다. 무조건 많이 넣지 않는다.
- 현재 landed path에서는 이 단계가 필요하지 않았으므로, 후속 세션에서도 **재현 없이는 도입하지 않는다.**

## Stepwise Gates

각 단계는 아래 gate를 **동시에** 만족해야 다음 단계로 진행한다. "Must hold"는 회귀가 곧 롤백 사유다. "Allowed trade-off"는 의사결정 편의를 위해 허용되는 변동폭이다.

| Step | Must hold (회귀 금지) | Allowed trade-off |
|---|---|---|
| Step 0 — SCN-004 재현 확인 | 없음 (측정 단계) | — |
| Step 1 — phrasing normalization | `citation_grounding_clean = 60/60`, `gold_citation_hit = 60/60`, `JSON/schema failure = 0`, `timeout = 0` | `hit@1` ±1 허용, baseline 137/153 유지 또는 개선 |
| Step 2 — answer-side hardening | `citation_grounding_clean = 60/60`, `gold_citation_hit = 60/60`, `JSON/schema failure = 0`, `timeout = 0` | `hit@1 / hit@3 / hit@5` 동일 유지 (retrieval 변경 아님), baseline 137/153 유지 또는 개선 |
| Step 3 — conditional rerank | `gold_citation_hit = 60/60`, `citation_grounding_clean = 60/60`, `hit@3` 동일 유지 | `hit@1` -1 허용 (단, `hit@3` 유지), baseline 137/153 유지 |
| Step 4 — selective decomposition | `citation_grounding_clean = 60/60`, `gold_citation_hit = 60/60`, `JSON/schema failure = 0`, `timeout = 0` | trigger 미발동 질의에는 영향 없어야 함. trigger 발동 질의의 latency 증가 허용 |

단계별 실행은 single change → baseline 60 재측정 + scenario smoke 재측정 → gate 통과 확인 → 다음 단계 진행 순서를 지킨다.

---

## Non-Goals For Next Session

다음 세션에서 기본적으로 하지 않을 것:

- 모델 교체
- embedding model 교체
- BM25 / hybrid retrieval 대규모 도입
- frontend 대규모 확장
- OCR / 추가 문서 타입 확장
- 새로운 broad schema 변경

판단 이유:

- `gemini-2.5-pro`는 live A/B에서 더 느리고 timeout이 많았으며 품질 우위가 없었다.
- retrieval miss보다 answer-side clause selection과 (일부) query composition 문제가 더 뚜렷하다.
- 현재는 시스템을 다시 뒤집기보다 retrieval-grounding-answer 연결부의 정보 선택 품질을 정교하게 만드는 편이 수익이 크다.

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

## Success Criteria For Future Follow-up Session

성공 기준은 **baseline 60문항 eval**과 **scenario smoke** 두 개의 독립 측정축으로 분리해서 본다. 두 축은 측정 대상이 다르므로 한쪽 성과로 다른 쪽을 대체해 판정하지 않는다.

### 측정축 1 — Baseline 60 eval

- `expected_point_strict_coverage`: current `137/153`, `16 partial`보다 개선
- `citation_grounding_clean = 60/60` 유지
- `gold_citation_hit = 60/60` 유지 (단일 gold 지표 한계는 "Current Baseline" 각주 참조)
- `JSON/schema failure = 0` 유지
- `timeout = 0` 유지

### 측정축 2 — Scenario smoke (demo question sets)

baseline 60에는 직접 반영되지 않는 scenario-specific 관찰이므로 별도 판정한다.

- `SCN-001`: Before / After 분리 없이 Full 질의 안정성 개선
- `SCN-004`: `근로기준법 제23조` 등 실체적 조문의 multi-citation survival 개선 — Step 0에서 재현 확인된 경우에 한해 판정
- `SCN-005`: 가족돌봄 질의에서 `서면 통보`, `불리한 처우 금지` 포인트 surface 개선

즉, 후속 세션 목표는 **"안전성(측정축 1의 grounding/gold 유지)을 유지한 채 baseline coverage(측정축 1의 137/153)와 복합 시나리오 coverage(측정축 2)를 함께 올리는 것"**이다.

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
- RAG refinement landing complete (`2026-04-16` clean pass)
- SCN-004 document draft backend complete
- SCN-004 After frontend implementation complete through Phase 3B
- current baseline verified:
  - retrieval `51/60`, `59/60`, `60/60`
  - answer `137/153`, `16 partial`, grounding/gold/schema/timeout clean
- current landed path:
  - Step 1 phrasing normalization 적용
  - Step 2 answer-side deterministic hardening 적용
  - Step 3 미적용
  - Step 4는 일반 경로에는 미적용, `SCN-001 Full` demo path에는 `top_k >= 8` 조건부 selective decomposition 적용
- next (선택적 후속 작업):
  - QA에서 backend/frontend contract mismatch 또는 citation survival regression이 확인될 때만 좁게 수정
  - 남은 `16` partial에 대한 answer-side surface / completeness 보강은 선택적 후속
  - `SCN-001 Full` demo는 `top_k: 10`, `ef_search: 100`을 명시하는 경로로 운영
  - `SCN-002`는 설명형 Before 데모 범위로 유지
  - 신규 RAG architecture 확장은 현재 QA 전 범위에서 진행하지 않음
