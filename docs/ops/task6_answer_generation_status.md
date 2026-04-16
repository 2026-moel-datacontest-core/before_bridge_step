# Task 6 Answer Generation Status

기준일: `2026-04-16`

## 목적

- Task 6 answer generation MVP의 현재 구현 상태를 고정
- 실제 검증 결과와 남은 약점을 한 문서에 정리
- 이후 RAG 수정 세션에서 재사용할 기준선을 남김

---

## 현재 스냅샷

- source of truth: `backend/data/law_chunks/all_chunks.json`
- selected_as_of: `2026-04-11`
- total chunks: `1722`
- PostgreSQL + pgvector local DB 구성 완료
- `law_chunks` ingestion 완료
- embedding populated: `1722 / 1722`
- sample embedding dimension: `768`
- HNSW index 생성 완료
- alembic head: `20260413_000003`

retrieval MVP는 유지 중이며, answer generation MVP와 그 후속 안정화 작업이 완료된 상태다.

현재 기본 모델:

- answer model: `gemini-2.5-flash`
- embedding model: `gemini-embedding-001`

`gemini-2.5-pro`는 live A/B 결과에서 더 느리고 timeout이 많았으며, coverage 개선 근거가 부족해 default로 채택하지 않았다.

---

## 구현 완료 범위

### 1. Answer Route / Service

- `POST /api/v1/answer` 구현
- retrieval 결과를 입력으로 사용하는 grounded answer generation 구현
- `cited_articles` 포함 응답 고정
- retrieval 결과 밖 citation 인용 금지 구조 구현
- answer text에 대한 explicit citation grounding 검증 구현
- `grounded_context_ids` 기준 citation leak 차단 구현
- article / clause exactness 유지
- `cited_context_ids` fail-closed 처리

### 2. 안정성 / 운영성 보강

- Vertex embedding / answer generation 경로에 hard wall-clock timeout 추가
- provider timeout을 제어된 예외로 변환
- router에서 provider timeout / provider unavailable / contract failure를 구분 매핑
- `ensure_postgres_ready.py`를 실제 DB connection + `SELECT 1` polling 기반 readiness helper로 보강
- answer / retrieval router에 최소 구조화 로그 추가

### 3. Verify / Eval 보강

- `backend/verify/check_answer_generation.py`에 grounding smoke 검증 추가
- `eval/run_answer_eval.py`에 explicit citation grounding 검사 추가
- eval runner에 per-item bounded execution 추가
- targeted eval ID 실행 경로 추가
- failure bucket / partial coverage / schema failure 요약 추가
- `backend/verify/debug_answer_selection.py` 추가
- raw / expanded / grounded / citation postprocess 흐름을 verify 경로에서 분리 확인 가능하게 보강

### 4. Coverage 보강

answer-side에서 다음 개선을 반영했다.

- grounded clause extraction을 문단 / 항목 단위로 재구성
- grounded clause ranking 추가
- 상위 chunk 우선 선택
- 제한적 adjacent expansion 추가
- 숫자 / 기간 / 비율 / 예외 / 범위 표현 surface 보강
- 출력 단계 citation-sanitizing 추가
- key points는 grounded clause를 우선 사용하도록 조정
- query hint normalization (`LEGAL_QUERY_HINT_RULES`) 확장
- focus-aware clause selection / narrow clause bias 추가
- incomplete answer 복원 및 targeted final summary 보강
- family-care sibling / procedure companion citation postprocess 추가
- `raw_cited_context_ids` / `expanded_cited_context_ids` / `grounded_context_ids` semantics 분리

### 5. Scenario Expansion Update

시나리오 검증/확장 결과 현재 corpus 상태는 다음과 같다.

- `SCN-001`: `Current Corpus Covered`
  - 데이터 추가 불필요
  - Before/After 분리 데모는 안정적
  - Full 단일 질의는 retrieval ranking 리스크 존재
- `SCN-002`: `Partial`
  - 법률 설명형 Before 데모는 가능
  - 자동 숫자 비교와 직종 자동 판정은 현재 범위 밖으로 둠
- `SCN-003`: `Current Corpus Covered`
  - 장애인 관련 조문 9개를 최소 범위로 추가
  - `backend/data/law_chunks/all_chunks.json`과 법령별 분리 JSON 갱신
  - PostgreSQL upsert 및 신규 9건 embedding 완료
- `SCN-004`: `Current Corpus Covered`
  - 데이터 추가 불필요
  - 부당해고/체불 After 시연 바로 가능
- `SCN-005`: `Current Corpus Covered`
  - 데이터 추가 불필요
  - `selected_as_of = 2026-04-11` corpus 기준으로 조문 체계 정렬 필요

현재 추가된 장애인 관련 법령:

- `장애인차별금지 및 권리구제 등에 관한 법률`
- `장애인고용촉진 및 직업재활법`

---

## 실제 검증 결과

### 기본 검증

실행 완료:

- `python -m compileall backend eval`
- `python -c "from backend.main import app; print('import_ok')"`
- `python backend/verify/ensure_postgres_ready.py --start-if-needed`
- `python backend/verify/check_answer_generation.py "<sample>" --top-k 5 --ef-search 100`

확인된 상태:

- import 정상
- PostgreSQL readiness 정상
- 샘플 answer generation 정상
- grounding 검증 정상

### Scenario Data Verification

추가 확인 완료:

- PostgreSQL readiness 정상
- 현재 live corpus / DB 기준 `1722 / 1722`
- `SCN-001`, `SCN-004`, `SCN-005`는 데이터 추가 없이 source coverage 확인
- `SCN-003`은 최소 범위 데이터 보강 후 retrieval / answer smoke 재검증 완료
- `SCN-002`는 현재 source 범위만으로는 자동 숫자 판정이 어렵지만, 현재 계획에서는 설명형 Before 데모 범위로 유지

### Retrieval 기준 성능

- `hit@1 = 51/60 (85.00%)`
- `hit@3 = 59/60 (98.33%)`
- `hit@5 = 60/60 (100.00%)`

### Answer Eval 최종 기준선

full 60 live eval 기준:

- `items_answered = 60/60`
- `JSON/schema failure = 0`
- `timed_out_ids = []`
- `citation_grounding_clean = 60/60`
- `gold_citation_hit = 60/60`
- `expected_point_strict_coverage = 137/153`
- `failures_or_partial_coverage = 16`

coverage 개선 경과:

- full 60 strict coverage: `84/153 -> 107/153 -> 117/153 -> 122/153 -> 124/153 -> 126/153 -> 137/153`
- full 60 failures_or_partial_coverage: `36 -> 30 -> 26 -> 24 -> 23 -> 16`

### Targeted Improvement 결과

대표 targeted improvement:

- `KLS-EVAL-010`: `0/3 -> 3/3`
- `KLS-EVAL-017`: `0/2 -> 1/2` 후 substantive exclusion final surface 안정화
- `KLS-EVAL-058`: `0/3 -> 3/3`
- `SCN-005-Q3`: sibling + procedure companion citation survival 안정화
- long enumerated weak items (`KLS-EVAL-029`, `049`, `051`, `055`, `060`):
  - focused loop strict coverage `13/24 -> 24/24`
  - clean landing verification 후 full 60 기준 `137/153`, `16 partial`

landing verification:

- full 60 clean rerun: `timeout = 0`, `items_answered = 60/60`
- `KLS-EVAL-060` 단건 반복에서도 timeout 재현 안 됨
- 직전 timeout은 기능 회귀가 아니라 간헐적 provider/runtime variance로 판정

---

## 현재 약한 문항 / 패턴

현재 남은 partial IDs:

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

패턴별 메모:

- 현재 남은 약점은 retrieval miss보다 answer finalization / surface completeness 쪽에 더 가깝다.
- 숫자·기한·횟수·요건이 여러 개 열거된 조문에서 일부 항목이 answer 본문에 직접적으로 올라오지 않는 경우가 남아 있다.
- 일부 문항은 조문 선택 자체보다 answer 문장화가 strict coverage 친화적으로 정리되지 않는 문제가 남아 있다.

공통 패턴:

- 긴 조문 또는 하위 항목 열거형 조문에서
  - 숫자
  - 기간
  - 예외
  - 절차
  - 범위
  를 모두 안정적으로 끌어오는 능력이 아직 완전하지 않음

---

## 모델 선택 결론

### Answer Model

기본값 유지:

- `gemini-2.5-flash`

유지 이유:

- `gemini-2.5-pro`는 live A/B에서 더 느림
- `gemini-2.5-pro`는 hard timeout이 더 자주 발생
- coverage 개선이 실측으로 확인되지 않음
- 현재 병목은 retrieval miss보다 answer-side coverage와 clause selection에 가까움

### Embedding Model

기본값 유지:

- `gemini-embedding-001`

유지 이유:

- retrieval miss가 병목이라는 근거가 부족함
- answered item 기준 gold citation hit과 grounding clean이 안정적임
- 현재 남은 문제는 embedding보다 answer-side coverage임

---

## 운영상 주의

- sandbox 안에서는 localhost DB probe가 false negative를 낼 수 있어 unrestricted 실행이 필요할 수 있음
- eval runner는 partial coverage가 남으면 exit code `1`로 종료할 수 있음
- timeout / rate-limit / provider failure는 현재 bounded execution 안에서 제어되지만, 고부하 상황에서의 DSQ 리스크가 완전히 사라진 것은 아님
- `data/legalize-kr` working tree HEAD와 frozen corpus commit을 혼용하면 snapshot이 섞일 수 있음
  - 현재 서비스 기준은 `selected_as_of = 2026-04-11`
  - scenario-driven data addition도 이 기준에 맞춰 반영해야 함

---

## 다음 RAG 수정 세션 권장 방향

현재 landing은 완료 상태다. 즉시 필요한 answer/retrieval 구조 수정 세션은 없다.

후속 작업이 필요할 때만 아래 순서로 다시 보는 것이 합리적이다.

1. 남은 `16` partial에 대한 answer-side surface / completeness 보강
2. low-signal key point noise 정리
3. `SCN-001 Full` demo 필요성이 커질 때만 selective decomposition 별도 검토
4. citation survival 이슈가 다시 재현될 때만 Step 3 rerank 재검토
5. `SCN-002`는 설명형 Before 데모 범위로 유지

즉 현재 단계의 결론은 **"landing 완료, 후속은 선택적 answer-side cleanup만"**이다.
