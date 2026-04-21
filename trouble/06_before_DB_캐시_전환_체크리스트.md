# Before DB 캐시 전환 체크리스트

기준일: `2026-04-21`

공통 전제:

- 모든 수정은 현재 사용자에게 보이는 UI 구조와 기존 기능 동작을 유지하는 범위에서만 진행한다.
- 정리, 안정화, 저장소 전환이 필요하더라도 현재 확인 가능한 화면 흐름과 기능 결과를 바꾸지 않는 것을 우선한다.

연결 문서:

- [03_DB_로컬_데이터_전환_가능성.md](/home/minsoo/after_pipeline/law_main_road/trouble/03_DB_로컬_데이터_전환_가능성.md:1)
- [클라우드런_데이터_저장_구조.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/클라우드런_데이터_저장_구조.md:1)

목적:

- `before`의 법령 source를 파일에서 PostgreSQL로 옮기기 위한 실제 수정 순서를 체크리스트로 관리
- `before`의 기존 retrieval semantics와 UI를 유지한 채 startup memory cache 전략으로 전환
- 로컬에서 `file`/`db` 모드를 비교 검증한 뒤에 기본값 전환까지 진행

## 범위

이번 체크리스트는 아래 범위만 다룬다.

1. `law_chunks` source를 파일 기반에서 DB 기반으로 전환
2. `before` startup 시 전체 `law_chunks`를 메모리 캐시로 적재
3. 로컬에서 file/db parity 검증

이번 문서에서 의도적으로 제외하는 항목:

- `standard_map.json`, `minimum_wage.yaml`의 DB 이전
- `before` job 상태의 DB 테이블화
- artifact의 GCS 이전
- Cloud Run queue / worker 구성

## 핵심 원칙

- `before`의 키워드 / citation matching / extra 조항 탐색 규칙은 유지한다.
- `before`를 `after`의 vector retrieval 로직으로 바꾸지 않는다.
- `before`는 DB를 source of truth로 사용하되, 요청 시점에는 startup cache를 사용한다.
- 로컬 실험 단계에서는 `file`과 `db`를 모두 지원해 비교 가능하게 만든다.

## 진행 체크리스트

### Phase 1. 설정 분기 추가

목표:

- `before`가 파일 로딩과 DB 로딩을 선택할 수 있는 최소 설정 지점 추가

대상 파일:

- [backend/app/before_stack/core/settings.py](/home/minsoo/after_pipeline/law_main_road/backend/app/before_stack/core/settings.py:1)

체크리스트:

- [x] `BEFORE_LAW_SOURCE=file|db` 환경변수 추가
- [x] 기본값은 기존 동작 보존을 위해 `file`로 설정
- [x] `standard_map.json`, `minimum_wage.yaml`는 기존 파일 로딩 유지
- [x] 설정 값이 잘못된 경우 명확한 예외 또는 fallback 처리 방침 결정

완료 조건:

- 설정만으로 `before` law source를 `file` 또는 `db`로 선택할 수 있다.

확인 방법:

- [x] `settings.py`에서 `BEFORE_LAW_SOURCE`가 선언됐는지 확인
- [x] `file`, `db` 외 값 입력 시 동작 방침이 코드상 명확한지 확인
- [x] 환경변수를 주지 않았을 때 기본값이 `file`인지 확인
- [x] backend import가 기존처럼 성공하는지 확인

### Phase 2. DB 캐시 로더 추가

목표:

- PostgreSQL `law_chunks` 전체를 읽어 `before`가 사용할 `list[dict]` 캐시를 생성

대상 파일:

- 신규 파일 `backend/app/before_stack/services/law_chunk_cache.py`
- [backend/app/models/law_chunk.py](/home/minsoo/after_pipeline/law_main_road/backend/app/models/law_chunk.py:1)
- [backend/app/db.py](/home/minsoo/after_pipeline/law_main_road/backend/app/db.py:1)

체크리스트:

- [x] `load_all_chunks_from_file()` 구현
- [x] `load_all_chunks_from_db()` 구현
- [x] DB row를 현재 `before`가 기대하는 dict shape로 변환
- [x] 최소 필드가 아니라 현재 사용 가능성이 있는 주요 필드를 넓게 보존
- [x] 반환 shape가 file 모드와 최대한 동일한지 점검

완료 조건:

- file/db 양쪽 모두 `list[dict]` 형태의 `all_chunks`를 생성할 수 있다.

확인 방법:

- [x] file loader 반환 타입이 `list[dict]`인지 확인
- [x] db loader 반환 타입이 `list[dict]`인지 확인
- [x] 대표 필드(`chunk_id`, `citation_label`, `content_normalized`, `law_name`, `doc_type`, `tier`)가 포함되는지 확인
- [x] DB row → dict 변환 시 누락 필드가 없는지 샘플 1~2건 확인

메모:

- 현재 file source(`before_assets`)는 `1724`, DB `law_chunks`는 `1722`로 개수 차이가 있다.
- 이 차이는 loader shape 문제가 아니라 source of truth drift 문제로 보고, Phase 5 parity에서 다시 확인한다.

### Phase 3. startup cache 연결

목표:

- `before` 앱 startup 시 설정에 따라 file/db source를 읽어 `app.state.all_chunks`에 캐시 적재

대상 파일:

- [backend/app/before_stack/main.py](/home/minsoo/after_pipeline/law_main_road/backend/app/before_stack/main.py:1)

체크리스트:

- [x] `_ensure_runtime_loaded()`에서 직접 `LAW_CHUNKS_PATH`를 읽는 코드 제거
- [x] 새 cache loader를 통해 `app.state.all_chunks` 적재
- [x] `app.state.all_chunks_source` 같은 진단용 상태 추가 여부 결정
- [x] startup / lifespan 경로에서 1회만 적재되도록 확인
- [x] 기존 `before_jobs`, `standard_map`, `min_wage` 초기화 흐름 유지

완료 조건:

- `before`는 startup 시 선택된 source로부터 `all_chunks`를 메모리에 적재한다.

확인 방법:

- [x] `BEFORE_LAW_SOURCE=file`에서 startup 후 `app.state.all_chunks`가 로드되는지 확인
- [x] `BEFORE_LAW_SOURCE=db`에서 startup 후 `app.state.all_chunks`가 로드되는지 확인
- [x] 필요 시 `app.state.all_chunks_source` 또는 health/debug 응답으로 source 확인 가능하게 했는지 확인
- [x] startup이 요청마다 재실행되지 않고 1회 적재 흐름인지 확인

### Phase 4. law_retriever 파일 의존 제거

목표:

- `law_retriever`가 내부적으로 파일을 다시 읽지 않고, 외부에서 주입된 `all_chunks`만 사용하도록 정리

대상 파일:

- [backend/app/before_stack/services/law_retriever.py](/home/minsoo/after_pipeline/law_main_road/backend/app/before_stack/services/law_retriever.py:1)

체크리스트:

- [x] `LAW_CHUNKS_PATH` import 제거
- [x] `_chunks_cache` 제거
- [x] `_load_chunks()` 제거
- [x] `build_extra_law_map(..., all_chunks=None)` fallback 정책 정리
- [x] 내부 호출이 startup cache 기준으로만 동작하도록 조정

완료 조건:

- `law_retriever`는 startup cache 또는 명시적 `all_chunks` 주입만 사용한다.

확인 방법:

- [x] `law_retriever.py`에 `LAW_CHUNKS_PATH` import가 남아 있지 않은지 확인
- [x] `_chunks_cache` 및 `_load_chunks()`가 제거됐는지 확인
- [x] `build_extra_law_map()`가 `all_chunks` 주입 기준으로 정상 동작하는지 확인
- [x] extra 조항 처리에서 파일 fallback이 몰래 남아 있지 않은지 확인

### Phase 5. 로컬 parity 검증 추가

목표:

- file 모드와 db 모드의 결과를 비교해 동작 차이를 통제

대상 파일:

- 신규 파일 `backend/verify/check_before_law_source_parity.py`

체크리스트:

- [x] chunk 총 개수 비교
- [x] 대표 `citation_label` exact match 비교
- [x] fallback 대상 비교
- [x] extra 조항 키워드 예시 비교
- [x] 차이가 나면 어떤 필드가 다른지 출력

완료 조건:

- 로컬에서 `file`과 `db` 결과 차이를 빠르게 확인할 수 있다.

확인 방법:

- [x] parity 스크립트가 실행되는지 확인
- [x] chunk 수 비교 결과가 출력되는지 확인
- [x] 대표 `citation_label` 비교 결과가 출력되는지 확인
- [x] extra 조항 예시 비교 결과가 출력되는지 확인
- [x] 차이가 날 때 어떤 필드가 다른지 사람이 읽을 수 있게 표시되는지 확인

메모:

- 현재 parity 결과는 `behavioral_parity_ok: True`
- source count는 `1724` vs `1722`로 다르며, file source에만 수동 보강 2건이 남아 있다.

### Phase 6. 기본값 전환

목표:

- parity 확인 후 `before`의 기본 source를 DB로 전환

대상 파일:

- [backend/app/before_stack/core/settings.py](/home/minsoo/after_pipeline/law_main_road/backend/app/before_stack/core/settings.py:1)
- 필요 시 관련 문서

체크리스트:

- [ ] parity 확인 완료
- [ ] 기본값을 `db`로 전환할지 결정
- [ ] file fallback을 유지할지 제거할지 결정
- [ ] 로컬 시작 가이드 / 운영 문서에 반영 여부 확인

완료 조건:

- `before`의 기본 law source가 DB 기준으로 동작한다.

확인 방법:

- [x] 환경변수를 주지 않았을 때 기본 source가 의도대로 동작하는지 확인
- [ ] `/before` 실제 흐름에서 결과가 기존과 크게 달라지지 않는지 확인
- [x] parity 검증이 통과한 상태에서만 기본값을 바꿨는지 확인
- [x] 관련 운영 문서와 로컬 실행 가이드 반영 필요 여부를 확인

메모:

- 기본 source는 `db`로 전환했다.
- `before_law_chunk_supplements` 테이블에 수동 보강 2건을 동기화한 뒤 parity를 다시 확인했다.
- 현재 parity 결과는 `behavioral_parity_ok: True`, `source_count_match: True`다.
- parent app `lifespan`에서 `before_app` preload를 명시적으로 호출하도록 반영했고, `TestClient` 기준 첫 `/api/v1/before/health` 응답에서 `runtime_loaded=true`, `all_chunks_source=db`, `all_chunks_count=1724`를 확인했다.

## 권장 진행 순서

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5
6. Phase 6

이 순서를 권장하는 이유:

- 설정 분기 없이 바로 DB 전환을 시작하면 기존 동작 비교가 어렵다.
- startup cache가 준비되기 전에는 `law_retriever` 파일 의존을 제거하면 안 된다.
- parity 검증 없이 기본값을 바꾸면 extra 조항이나 citation 매칭 차이를 놓칠 수 있다.

## 이번 작업의 확인 명령

backend import:

```bash
python -c "from backend.main import app; print('import_ok')"
```

frontend build:

```bash
cd frontend
npm run build
```

권장 추가 검증:

```bash
python backend/verify/check_before_law_source_parity.py
```

## 진행 기록

- [x] 체크리스트 문서 생성 완료
- [x] Phase 1 시작
- [x] Phase 1 완료
- [x] Phase 2 시작
- [x] Phase 2 완료
- [x] Phase 3 시작
- [x] Phase 3 완료
- [x] Phase 4 시작
- [x] Phase 4 완료
- [x] Phase 5 시작
- [x] Phase 5 완료
- [x] Phase 6 시작
- [x] Phase 6 완료
