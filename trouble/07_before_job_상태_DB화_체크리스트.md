# Before Job 상태 DB화 체크리스트

기준일: `2026-04-21`

공통 전제:

- 모든 수정은 현재 사용자에게 보이는 UI 구조와 기존 기능 동작을 유지하는 범위에서만 진행한다.
- 정리, 안정화, 저장소 전환이 필요하더라도 현재 확인 가능한 화면 흐름과 기능 결과를 바꾸지 않는 것을 우선한다.

연결 문서:

- [06_before_DB_캐시_전환_체크리스트.md](/home/minsoo/after_pipeline/law_main_road/trouble/06_before_DB_캐시_전환_체크리스트.md:1)
- [클라우드런_데이터_저장_구조.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/클라우드런_데이터_저장_구조.md:1)

목적:

- `before` review job 상태를 기존 `app.state.before_jobs` 메모리 구조에서 PostgreSQL 테이블로 전환
- 로컬에서 먼저 polling 흐름을 DB 기준으로 검증
- Cloud Run 전환 전에 인스턴스 메모리 의존을 제거

## 범위

이번 체크리스트는 아래 범위만 다룬다.

1. `before_review_jobs` DB 테이블 추가
2. job 생성 / 상태 갱신 / 조회 로직을 DB 기반으로 전환
3. 기존 `/api/v1/before/review/jobs` API contract 유지

이번 문서에서 의도적으로 제외하는 항목:

- artifact의 GCS 이전
- signed URL 또는 다운로드 프록시 전환
- 비동기 queue 분리
- `before_job_files`, `before_job_results` 같은 세부 테이블 분리

## 핵심 원칙

- 프런트가 기대하는 job 응답 구조는 유지한다.
- 초기 단계에서는 단일 테이블로도 충분하면 단순하게 간다.
- 결과 payload와 step 상태는 JSON 컬럼으로 저장해 API contract를 최대한 그대로 유지한다.
- job 상태 DB화와 artifact GCS 전환을 한 패치에 섞지 않는다.

## 권장 최소 스키마

테이블 예시:

- `before_review_jobs`

권장 컬럼:

- `job_id` TEXT PK
- `status` TEXT
- `created_at` TIMESTAMPTZ
- `updated_at` TIMESTAMPTZ
- `run_directory` TEXT NULL
- `steps` JSONB
- `error` TEXT NULL
- `result` JSONB NULL

## 진행 체크리스트

### Phase 1. 스키마 추가

목표:

- `before` job 상태를 담을 최소 테이블 추가

대상 파일:

- 신규 alembic migration
- 필요 시 ORM model 파일

체크리스트:

- [x] `before_review_jobs` migration 추가
- [x] `job_id`, `status`, `created_at`, `updated_at`, `run_directory`, `steps`, `error`, `result` 컬럼 정의
- [x] JSONB 컬럼 타입 선택
- [x] 인덱스가 필요한지 최소 수준으로 검토

완료 조건:

- 로컬 DB에 `before_review_jobs` 테이블이 생성된다.

확인 방법:

- [x] `alembic upgrade head` 후 테이블 생성 확인
- [x] 스키마가 현재 API 응답 필드를 담을 수 있는지 확인

### Phase 2. job 저장 access layer 추가

목표:

- 메모리 dict 대신 DB row를 읽고 쓰는 함수 추가

대상 파일:

- 신규 파일 `backend/app/before_stack/services/job_store.py` 추천

체크리스트:

- [x] job 생성 함수
- [x] job 조회 함수
- [x] job 부분 업데이트 함수
- [x] `_serialize_job()`와 호환되는 반환 구조 정리

완료 조건:

- job CRUD의 최소 경로가 서비스 함수로 분리된다.

확인 방법:

- [x] create → get → update 흐름을 단위 호출로 확인
- [x] 반환 shape가 기존 메모리 job dict와 크게 다르지 않은지 확인

### Phase 3. API 로직 전환

목표:

- `/review/jobs` 생성/조회 및 background update를 DB 기반으로 전환

대상 파일:

- [backend/app/before_stack/main.py](/home/minsoo/after_pipeline/law_main_road/backend/app/before_stack/main.py:1)

체크리스트:

- [x] `app.state.before_jobs` 생성 제거
- [x] `create_review_job()`가 DB에 job row 생성
- [x] `_update_job()`가 DB 업데이트를 사용하도록 변경
- [x] `get_review_job()`가 DB에서 조회하도록 변경
- [x] `health()`의 `job_count`가 DB 기준으로 계산되는지 결정

완료 조건:

- review job lifecycle이 메모리 대신 DB에서 유지된다.

확인 방법:

- [x] job 생성 후 서버 재시작 전/후 상태 조회 가능 여부 확인
- [x] polling 응답 구조가 기존과 동일한지 확인
- [x] 실패 시 `error` 및 step 상태 갱신이 저장되는지 확인

### Phase 4. 로컬 검증

목표:

- 실제 `before` review job 요청을 보내 DB 상태 저장이 정상 동작하는지 확인

대상 파일:

- 기존 API
- 필요 시 검증 스크립트

체크리스트:

- [x] `/api/v1/before/review/jobs` 생성 확인
- [x] `/api/v1/before/review/jobs/{job_id}` polling 확인
- [x] 완료 후 DB row에 `result` 저장 확인
- [x] 실패 시 DB row에 `error` 저장 확인

완료 조건:

- 로컬에서 job lifecycle이 DB 기준으로 재현된다.

확인 방법:

- [x] 샘플 이미지 1건 업로드
- [x] 상태 전이 `queued -> running -> completed|failed` 확인
- [x] DB row와 API 응답이 일치하는지 확인

메모:

- 실제 샘플 이미지 업로드로 success path를 확인했고, 최종 상태는 `completed`였다.
- 새 `TestClient(app)` 인스턴스에서 같은 `job_id`를 다시 조회해 `completed`, `run_directory=True`, `result=True`를 확인했다.
- failure path는 `run_contract_review_pipeline` 예외 주입으로 검증했고, DB row에 `status=failed`, `error=forced-test-failure`, `ocr step failed`가 저장되는 것을 확인했다.

### Phase 5. 메모리 fallback 제거 및 문서 반영

목표:

- 메모리 기반 job 상태 경로를 제거하고 문서에 반영

대상 파일:

- [backend/app/before_stack/main.py](/home/minsoo/after_pipeline/law_main_road/backend/app/before_stack/main.py:1)
- 운영 문서 / 로컬 시작 가이드 필요 시 갱신

체크리스트:

- [x] `before_jobs` 메모리 의존 제거
- [x] health/debug 설명 갱신
- [x] 로컬 실행 문서에 migration 필요 여부 반영

완료 조건:

- `before` job 상태는 DB만 source of truth로 사용한다.

확인 방법:

- [x] 코드 grep으로 `app.state.before_jobs` 제거 확인
- [x] 관련 문서 갱신 확인

메모:

- 현재 `before` job 상태 source of truth는 `before_review_jobs` 테이블이다.
- `health()`의 `job_count`는 DB row count를 기준으로 계산한다.
- `python -c "from backend.main import app; print('import_ok')"` 확인 완료
- `TestClient(app)` 기준 `/api/v1/before/health` 응답에서 `runtime_loaded=True`, `all_chunks_source=db`, `all_chunks_count=1724`, `job_count=6` 확인 완료

## 권장 진행 순서

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 5

이 순서를 권장하는 이유:

- 스키마 없이 API 로직을 먼저 바꾸면 상태 저장 기준이 흔들린다.
- access layer 없이 `main.py`에 직접 SQL을 넣으면 이후 GCS/queue 전환 때 다시 엉킨다.
- 실제 요청 검증 전에는 메모리 fallback을 제거하면 안 된다.

## 이번 작업의 확인 명령

backend import:

```bash
python -c "from backend.main import app; print('import_ok')"
```

parity 유지 확인:

```bash
python backend/verify/check_before_law_source_parity.py
```

review job 실제 생성:

```bash
curl -X POST -F "image=@<sample.jpg>" http://127.0.0.1:8000/api/v1/before/review/jobs
```

## 진행 기록

- [x] 체크리스트 문서 생성 완료
- [x] Phase 1 시작
- [x] Phase 1 완료
- [x] Phase 2 완료
- [x] Phase 3 완료
- [x] Phase 4 완료
- [x] Phase 5 시작
- [x] Phase 5 완료
- [x] Phase 1 완료
- [x] Phase 2 시작
- [x] Phase 2 완료
- [x] Phase 3 시작
- [x] Phase 3 완료
- [x] Phase 4 시작
- [x] Phase 4 완료
- [ ] Phase 5 시작
- [ ] Phase 5 완료
