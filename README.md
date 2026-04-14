# K-Labor Shield

외국인 근로자를 포함한 취약 노동자를 위한 노동권 보호 통합 AI MVP입니다.  
현재 저장소 기준으로는 `retrieval + grounded answer generation + 시나리오별 corpus 검증`까지 완료된 상태이며, 다음 단계는 broad refactor가 아니라 `RAG refinement`와 데모 운영 범위 정리입니다.

## 현재 상태

기준일: `2026-04-14`

- source of truth: `backend/data/law_chunks/all_chunks.json`
- `selected_as_of = 2026-04-11`
- current live chunks: `1722`
- PostgreSQL `law_chunks`: `1722`
- embedding populated: `1722 / 1722`
- vector dimension: `768`
- HNSW index: `idx_law_chunks_embedding`
- alembic head: `20260413_000003`
- answer model: `gemini-2.5-flash`
- embedding model: `gemini-embedding-001`

핵심 상태:

- retrieval MVP 완료
- grounded answer generation MVP 완료
- `cited_articles` 강제 및 retrieval 밖 citation 금지 완료
- answer grounding 검증, hard timeout, eval 안정화 완료
- scenario expansion 검증 완료

## 지금까지 완료된 것

### 1. Data / DB / Embedding

- 법령 청킹 파이프라인 baseline 완료
- `backend/data/law_chunks/all_chunks.json` 운영 기준선 확정
- PostgreSQL + pgvector 로컬 DB 구성 완료
- `law_chunks` ingestion 완료
- embedding `1722 / 1722` 완료
- HNSW 인덱스 구성 완료

### 2. Retrieval

- `POST /api/v1/retrieve` 구현 완료
- pgvector cosine retrieval 구현 완료
- retrieval eval 기준:
  - `hit@1 = 51/60 (85.00%)`
  - `hit@3 = 59/60 (98.33%)`
  - `hit@5 = 60/60 (100.00%)`

### 3. Answer Generation

- `POST /api/v1/answer` 구현 완료
- retrieval 결과를 사용하는 grounded answer flow 구현 완료
- `cited_articles` 포함 응답 강제
- retrieval 결과 밖 citation 인용 금지
- answer text explicit citation grounding 검증 구현
- timeout / provider failure / malformed response 안정화 완료

현재 full 60 answer eval 기준:

- `items_answered = 60/60`
- `JSON/schema failure = 0`
- `timed_out_ids = []`
- `citation_grounding_clean = 60/60`
- `gold_citation_hit = 60/60`
- `expected_point_strict_coverage = 117/153`
- `failures_or_partial_coverage = 26`

### 4. Scenario Expansion

현재 시나리오 기준선:

- `SCN-001`: covered
  - 외국인 근로자 계약/기숙사/차별/사업장 변경
  - 데이터는 충분하고, 남은 이슈는 Full 복합 질의 retrieval ranking
- `SCN-002`: partial
  - 최저임금/수습 꼼수 설명형은 가능
  - 현재는 설명형 Before 데모 범위로 고정
- `SCN-003`: covered
  - 장애인 관련 조문 9개 최소 추가 + 재임베딩 완료
- `SCN-004`: covered
  - 카톡 해고/임금·퇴직금 체불 After 시연 가능
- `SCN-005`: covered
  - 육아휴직/가족돌봄휴가 부당 거절 After 시연 가능

## 현재 데모 자산

### 시나리오 문서

- [docs/planning/12_scenario_expansion_plan.md](docs/planning/12_scenario_expansion_plan.md)

### 시나리오 질문 세트

- [eval/scenario_demo_question_sets_v1.json](eval/scenario_demo_question_sets_v1.json)

포함 시나리오:

- `SCN-001`
- `SCN-004`
- `SCN-005`

이 파일은 baseline 60문항 eval과 별개로, 발표 시연이나 retrieval/answer smoke용으로 바로 재사용할 수 있게 만든 질문 세트입니다.

## 다음 작업

현재 우선순위는 아래 순서입니다.

### 1. RAG refinement

다음 개선 방향은 model swap보다 retrieval 구조 개선입니다.

우선 후보:

- query decomposition
- sub-query별 retrieval
- 결과 union / dedupe
- clause ranking 개선
- answer-side selection 개선

특히 `SCN-001` 같은 복합 질의는 데이터 부족보다 retrieval ranking이 병목으로 확인됐습니다.

### 2. SCN-002 범위 고정

- `SCN-002`는 당분간 설명형 Before 데모로만 사용
- 수습 감액 예외 오남용 설명과 계약서 경고 UX까지만 현재 범위에 포함
- 연도별 최저임금 액수 자동 비교나 단순노무 직종 자동 판정은 현재 단계 범위 밖으로 둔다

### 3. 데모 확장 기능

아직 후속 포인트로만 남아 있는 기능:

- 사업장 변경 사유서 자동 작성
- 노동청 제출용 진정서 초안 작성
- 육아휴직 / 가족돌봄 재신청서 또는 내용증명 초안 작성

현재 answer route 범위를 넘는 기능이므로, 별도 단계로 분리해서 보는 것이 맞습니다.

## 저장소 구조

| Path | Role |
|---|---|
| `backend/` | FastAPI, RAG, DB, verification |
| `frontend/` | Next.js UI |
| `scripts/` | 법령 전처리 / chunking pipeline |
| `data/legalize-kr/` | 법령 원본 submodule |
| `backend/data/law_chunks/` | chunk 산출물 및 `all_chunks.json` |
| `docs/planning/` | 기준 설계 문서 |
| `docs/ops/` | 운영 / 상태 문서 |
| `eval/` | baseline eval, scenario demo question sets |

## 빠른 참고 문서

작업을 이어갈 때 우선 보면 되는 문서:

1. [docs/ops/task6_answer_generation_status.md](docs/ops/task6_answer_generation_status.md)
2. [docs/planning/12_scenario_expansion_plan.md](docs/planning/12_scenario_expansion_plan.md)
3. [docs/planning/02_rag_strategy.md](docs/planning/02_rag_strategy.md)
4. [docs/planning/05_eval_plan.md](docs/planning/05_eval_plan.md)
5. [docs/planning/10_backend_retrieval_plan.md](docs/planning/10_backend_retrieval_plan.md)

## 실행 예시

### backend

```bash
uvicorn backend.main:app --reload
```

### retrieval smoke

```bash
/home/jongwon/anaconda3/envs/law_main_road/bin/python backend/verify/check_retrieval.py "입사할 때 회사가 임금, 근무시간, 휴일, 연차를 말로만 설명하고 서면은 안 줬어요. 법상 어떤 내용은 반드시 명시하고 서면으로 줘야 하나요?" --top-k 5 --ef-search 100
```

### answer smoke

```bash
/home/jongwon/anaconda3/envs/law_main_road/bin/python backend/verify/check_answer_generation.py "입사할 때 회사가 임금, 근무시간, 휴일, 연차를 말로만 설명하고 서면은 안 줬어요. 법상 어떤 내용은 반드시 명시하고 서면으로 줘야 하나요?" --top-k 5 --ef-search 100
```

### baseline retrieval eval

```bash
/home/jongwon/anaconda3/envs/law_main_road/bin/python eval/run_retrieval_eval.py --top-k 5 --ef-search 100 --show-failures 10
```

### baseline answer eval

```bash
/home/jongwon/anaconda3/envs/law_main_road/bin/python eval/run_answer_eval.py --top-k 5 --ef-search 100 --limit 60 --show-failures 20
```

## 주의

- `data/legalize-kr/`는 직접 수정하지 않습니다.
- frozen corpus 기준은 현재 `selected_as_of = 2026-04-11`입니다.
- raw source HEAD가 더 최신이어도, snapshot 재선정 없이 섞어 반영하면 안 됩니다.
- planning 문서의 오래된 숫자나 초안 조문은 항상 실제 `all_chunks.json`과 DB 상태로 재검증하는 것이 원칙입니다.
