# 11. Backend Answer Generation Handoff

> Historical note: 이 문서는 retrieval 완료 시점의 handoff였다.
> Task 6 answer generation MVP와 후속 안정화 작업은 이후 세션에서 완료되었다.
> 최신 구현 상태와 검증 결과는 `docs/ops/README.md`와 루트 `README.md`를 기준으로 본다.
> Current live corpus는 scenario-driven minimal data addition 이후 `1722` chunks다.
> 이 문서 내부의 `1713` count는 retrieval 완료 시점의 historical snapshot이다.

## Current Meaning

현재는 historical handoff 문서이며, 다음 세션의 실질 기준선으로 쓰지 않는다.

다음 세션에서 우선 참고할 문서:

1. `docs/ops/README.md`
2. `docs/planning/13_document_draft_plan.md`
3. `docs/planning/14_frontend_implementation_handoff.md`
4. `docs/planning/02_rag_strategy.md`
5. `docs/planning/05_eval_plan.md`

---

## Historical Snapshot

- source of truth: `backend/data/law_chunks/all_chunks.json`
- selected_as_of: `2026-04-11`
- total chunks: `1713`
- PostgreSQL + pgvector local DB configured
- `law_chunks` ingestion complete
- `law_chunks.embedding`: `1713 / 1713` populated
- sample embedding dimension: `768`
- HNSW index: `idx_law_chunks_embedding`
- alembic head at that historical snapshot: `20260413_000003` (current repo head: `20260421_000005`)

retrieval MVP complete:

- FastAPI app skeleton implemented
- query embedding service implemented
- pgvector cosine retrieval implemented
- `POST /api/v1/retrieve` implemented
- `backend/verify/check_retrieval.py` implemented
- `eval/run_retrieval_eval.py` implemented

verified result:

- query embedding direct call: dim `768`
- `GET /` -> `200`
- `POST /api/v1/retrieve` -> `200`
- blank query -> `422`
- retrieval eval:
  - `hit@1 = 51/60 (85.00%)`
  - `hit@3 = 59/60 (98.33%)`
  - `hit@5 = 60/60 (100.00%)`

important implementation note at that time:

- `KLS-EVAL-019` miss was fixed by adding minimal query embedding hint normalization in `backend/app/services/embedding.py`
- router now maps Vertex / DB dependency failures to `503`

---

## Historical Next Scope

다음 세션의 1순위는 retrieval 이후의 **citation-grounded answer generation MVP**다.

권장 범위:

1. answer API skeleton 구현
2. retrieval 결과를 입력으로 사용하는 answer generation service 구현
3. `cited_articles` 강제
4. retrieval 결과에 없는 조문 인용 금지
5. answer eval 또는 최소 verification script 구현
6. agent / frontend는 가능하면 다음 단계로 미루기

비권장:

- retrieval 대규모 리팩토링
- BM25 / hybrid / reranker 추가
- frontend 대규모 변경
- agent 구조 확장

---

## Guardrails

- agent / frontend는 다음 세션의 기본 범위 밖
- 기존 migration `000001`, `000002`, `000003` 수정 금지
- 기존 DB schema / ingestion / embedding / retrieval 동작 깨지지 않게 유지
- `cited_articles` 없는 법률 응답 흐름으로 가지 말 것
- 검색 결과에 없는 조문 인용 금지
- 문서보다 실제 코드/실행 결과를 우선하되, 다르면 명시할 것

---

## Suggested Read Order

1. `AGENTS.md`
2. `CLAUDE.md`
3. `backend/CLAUDE.md`
4. `docs/planning/00_project_overview.md`
5. `docs/planning/02_rag_strategy.md`
6. `docs/planning/04_architecture.md`
7. `docs/planning/05_eval_plan.md`
8. `docs/planning/09_backend_embedding_plan.md`
9. `docs/planning/10_backend_retrieval_plan.md`
10. `docs/planning/11_backend_answer_generation_handoff.md`

그 다음 실제 코드:

- `backend/main.py`
- `backend/app/routers/retrieval.py`
- `backend/app/services/embedding.py`
- `backend/app/services/retrieval.py`
- `backend/app/schemas/retrieval.py`
- `backend/verify/check_retrieval.py`
- `eval/run_retrieval_eval.py`

---

## Archived Prompt

아래 프롬프트는 retrieval 완료 직후의 historical artifact다. 현재 상태에는 맞지 않으므로 그대로 재사용하지 않는다.

```text
Task 6 answer generation MVP를 end-to-end로 진행해줘. 계획만 말하지 말고, 구현하고, 가능한 범위까지 직접 실행/검증까지 해줘.

먼저 읽을 문서:
1. AGENTS.md
2. CLAUDE.md
3. backend/CLAUDE.md
4. docs/planning/00_project_overview.md
5. docs/planning/02_rag_strategy.md
6. docs/planning/04_architecture.md
7. docs/planning/05_eval_plan.md
8. docs/planning/09_backend_embedding_plan.md
9. docs/planning/10_backend_retrieval_plan.md
10. docs/planning/11_backend_answer_generation_handoff.md

그 다음 실제로 확인할 파일/상태:
- backend/main.py
- backend/app/routers/retrieval.py
- backend/app/services/embedding.py
- backend/app/services/retrieval.py
- backend/app/schemas/retrieval.py
- backend/verify/check_retrieval.py
- eval/run_retrieval_eval.py
- 현재 PostgreSQL law_chunks 상태
- 현재 retrieval API 상태
- 현재 GCP/Vertex answer generation 실행 가능성

현재 확정 상태:
- source of truth: backend/data/law_chunks/all_chunks.json
- selected_as_of: 2026-04-11
- chunk 수: 1713
- PostgreSQL + pgvector 로컬 DB 구성 완료
- law_chunks ingestion 완료
- embedding 완료: 1713 / 1713
- sample vector dimension = 768 확인 완료
- HNSW index 생성 완료
- historical alembic head at that time = `20260413_000003`; current repo head = `20260421_000005`
- retrieval MVP 구현 완료
- POST /api/v1/retrieve 구현 및 검증 완료
- retrieval eval 결과:
  - hit@1 = 51/60 (85.00%)
  - hit@3 = 59/60 (98.33%)
  - hit@5 = 60/60 (100.00%)
- KLS-EVAL-019는 query embedding hint normalization으로 보정 완료
- historical note: 이 시점에는 agent / frontend가 다음 단계의 기본 범위 밖이었음

이번 세션 목표:
1. answer generation service 구현
2. retrieval 결과를 사용하는 grounded answer route 구현
3. cited_articles 강제
4. retrieval 결과에 없는 citation 인용 금지 구조 구현
5. 가능한 범위의 verification script 또는 eval runner 구현
6. 가능한 범위까지 실제 실행/검증
7. 마지막에 변경 사항과 검증 결과 정리

중요 제약:
- agent / frontend는 기본적으로 건드리지 말 것
- retrieval / embedding / ingestion / DB schema 기존 동작 깨지지 않게 할 것
- cited_articles 없는 법률 응답 흐름으로 가지 말 것
- 검색 결과에 없는 조문 인용 금지 원칙을 answer generation 구조에 반영할 것
- 문서보다 실제 코드/실행 결과를 우선하되, 문서와 다르면 명시할 것

구현 시 주의:
- answer generation은 retrieval response의 cited_articles만 사용 가능하게 설계할 것
- retrieval 결과 chunk 내용을 prompt context로 사용할 때 출처 추적이 가능해야 함
- 법률 응답은 단정적 판정 대신 주의/가능성 중심 표현 유지
- 가능하면 기존 retrieval service를 재사용하고 불필요한 전역 리팩토링은 하지 말 것

실행/검증 기대:
- answer route 기동 확인
- retrieval -> answer 흐름 직접 호출 확인
- cited_articles 포함 응답 확인
- 검색 결과에 없는 citation이 응답에 섞이지 않는지 확인
- 가능하면 eval payload의 expected_points를 일부 활용한 간이 검증

blocker 처리 규칙:
- GCP 인증, Vertex 권한, API 비활성화 등으로 answer generation 실행이 막히면
  1. 구현은 가능한 범위까지 완료
  2. 정확한 blocker를 짧고 구체적으로 보고
  3. 어떤 명령/환경값이 더 필요한지 명시
- 애매하면 멈추지 말고 먼저 로컬에서 확인 가능한 부분을 최대한 진행할 것

작업 방식:
- 먼저 현재 상태를 5줄 이내로 요약
- 그 다음 바로 구현
- 중간중간 실제 실행 결과를 반영해서 진행
- 마지막에는
  1. 변경 파일
  2. 실제 실행한 검증
  3. 완료 상태
  4. 남은 blocker/리스크
  를 짧게 정리해줘
```

---

## Current Next Step

- answer generation 자체는 완료됨
- RAG refinement도 `2026-04-16` clean pass 기준 landing 완료됨
- SCN-004 document draft API와 frontend After flow도 구현 완료됨
- SCN-004 QA 정합성 검증과 content rehearsal도 통과됨
- 다음 실질 과제는 신규 backend feature가 아니라 demo freeze 유지
- QA에서 answer / draft / frontend contract mismatch 또는 citation survival regression이 재현될 때만 좁게 수정

## Historical Success Criteria

- retrieval를 재사용하는 answer generation 경로가 실제로 동작
- 응답에 `cited_articles` 포함
- 응답 citation이 retrieval 결과 밖으로 벗어나지 않음
- 최소한 단건 verification이 통과
- 가능하면 answer-level eval의 초기 골격까지 확보
