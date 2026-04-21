# After Artifacts 도입 체크리스트

기준일: `2026-04-21`

공통 전제:

- 모든 수정은 현재 사용자에게 보이는 UI 구조와 기존 기능 동작을 유지하는 범위에서만 진행한다.
- 저장 계층은 추가할 수 있지만, `after`의 현재 API contract와 화면 흐름은 바꾸지 않는다.

연결 문서:

- [클라우드런_데이터_저장_구조.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/클라우드런_데이터_저장_구조.md:1)
- [로컬 시작 가이드.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/로컬%20시작%20가이드.md:1)

목적:

- `after`의 사용자 입력과 결과를 로컬 artifact 형태로 저장
- 나중에 `local filesystem -> GCS` 전환 시 저장 backend만 교체할 수 있게 준비
- 현재 `after`의 answer / draft API contract는 그대로 유지

## 범위

이번 체크리스트는 아래 범위만 다룬다.

1. `backend/data/after_artifacts/runs/` 로컬 저장 루트 추가
2. `after` answer / draft 단계별 artifact 저장
3. 최소 DB 메타데이터 row 추가

이번 문서에서 의도적으로 제외하는 항목:

- GCS 실제 업로드 구현
- signed URL 또는 다운로드 프록시
- frontend 저장 구조 변경
- after 실행 이력 조회 UI

## 저장 원칙

- `after`는 현재 answer와 draft가 독립 API 호출이므로, 첫 단계에서는 단일 통합 세션보다 단계별 run 저장을 우선한다.
- answer 호출은 `answer` stage run으로 저장한다.
- draft 호출은 `draft` stage run으로 저장한다.
- 저장 실패가 현재 API 응답 자체를 깨뜨리지 않도록 best-effort 저장을 우선한다.

## 권장 로컬 폴더 구조

- `backend/data/after_artifacts/runs/<run_id>/`

answer stage 예시:

- `user_statement.txt`
- `answer_request.json`
- `answer_response.json`

draft stage 예시:

- `user_statement.txt`
- `draft_request.json`
- `case_intake.json`
- `legal_basis.json`
- `draft_response.json`

## 권장 최소 DB 스키마

테이블 예시:

- `after_artifact_runs`

권장 컬럼:

- `run_id` TEXT PK
- `stage` TEXT
- `status` TEXT
- `query_hash` TEXT NULL
- `document_type` TEXT NULL
- `artifact_root` TEXT
- `error` TEXT NULL
- `created_at` TIMESTAMPTZ
- `updated_at` TIMESTAMPTZ

## 진행 체크리스트

### Phase 1. 체크리스트와 저장 단위 고정

목표:

- 어떤 시점에 무엇을 저장할지 결정

체크리스트:

- [x] answer / draft 저장 단위 분리 결정
- [x] 로컬 저장 루트 경로 확정
- [x] GCS 전환 시 저장 backend만 교체한다는 원칙 명시

확인 방법:

- [x] 체크리스트 문서 생성

### Phase 2. 최소 스키마 추가

목표:

- after artifact run 메타데이터를 담는 최소 DB 테이블 추가

체크리스트:

- [x] `after_artifact_runs` migration 추가
- [x] ORM model 추가
- [x] 인덱스 최소 검토

확인 방법:

- [x] `alembic upgrade head` 후 테이블 생성 확인

### Phase 3. 로컬 artifact 저장 계층 추가

목표:

- 저장 backend를 라우터 밖으로 분리

대상 파일:

- 신규 `backend/app/services/after_artifact_store.py`

체크리스트:

- [x] answer stage 저장 함수
- [x] draft stage 저장 함수
- [x] run 디렉터리 생성 함수
- [x] DB metadata row 생성/갱신 함수

확인 방법:

- [x] 단위 호출로 `backend/data/after_artifacts/runs/...` 생성 확인
- [x] 저장 파일 이름과 JSON shape 확인

### Phase 4. answer / draft 라우터 연결

목표:

- 현재 API contract를 유지한 채 artifact 저장 연결

대상 파일:

- [backend/app/routers/answer.py](/home/minsoo/after_pipeline/law_main_road/backend/app/routers/answer.py:1)
- [backend/app/routers/document_draft.py](/home/minsoo/after_pipeline/law_main_road/backend/app/routers/document_draft.py:1)

체크리스트:

- [x] `/api/v1/answer` 성공 시 answer artifact 저장
- [x] `/api/v1/documents/draft` 성공 시 draft artifact 저장
- [x] 저장 실패는 로그만 남기고 API 응답은 유지하는지 결정

확인 방법:

- [x] answer 호출 후 answer artifact run 생성 확인
- [x] draft 호출 후 draft artifact run 생성 확인

### Phase 5. 로컬 검증 및 문서 반영

목표:

- 실제 `after` 흐름 한 번으로 파일 저장과 DB row를 확인

체크리스트:

- [x] `after_artifacts` 경로 `.gitignore` 반영
- [x] 로컬 시작 가이드에 migration / 저장 루트 메모 반영
- [x] 저장 결과 예시 확인

확인 방법:

- [x] backend import 확인
- [x] `npm run build` 확인
- [x] 최신 run 디렉터리와 DB row 확인

메모:

- 현재 로컬 `after` 저장 루트는 `backend/data/after_artifacts/runs/` 이다.
- answer stage는 `user_statement.txt`, `answer_request.json`, `answer_response.json`를 저장한다.
- draft stage는 `user_statement.txt`, `draft_request.json`, `case_intake.json`, `legal_basis.json`, `draft_response.json`를 저장한다.
- DB 메타데이터는 `after_artifact_runs` 테이블에 저장된다.

## 진행 기록

- [x] 체크리스트 문서 생성 완료
- [x] Phase 1 완료
- [x] Phase 2 완료
- [x] Phase 3 완료
- [x] Phase 4 완료
- [x] Phase 5 완료
