# Quick Start

## 목적

이 문서는 `law_main_road` 저장소를 새 환경에서 실행하는 가장 자세한 시작 가이드다.

이 문서의 목적은 아래 3가지다.

- 현재 저장소를 실제로 띄우는 순서를 한 번에 정리한다.
- 이후 추가할 `scripts/starting.sh`가 어떤 절차를 자동화해야 하는지 기준을 고정한다.
- 다른 채팅이나 다른 작업 세션에서 문제가 생겼을 때, 어떤 정보를 확인하고 전달해야 하는지 남긴다.

이 문서와 이후 추가할 `starting.sh`는 현재 구현을 실행하고 검증하기 위한 정리이며, 기존 `RAG`, `map`, `before/after` 처리 로직은 변경하지 않는다.

## 현재 프로젝트 개요

이 저장소는 크게 두 흐름으로 구성된다.

- `before`: 근로계약서 업로드 후 OCR/계약 검토 결과를 반환하는 흐름
- `after`: 노동 문제를 입력하면 법령 검색, 답변, 문서 초안을 생성하는 흐름

현재 핵심 데이터 구조는 아래와 같다.

- 법령 source of truth: `backend/data/law_chunks/all_chunks.json`
- 검색/임베딩/법령 메타데이터 저장: PostgreSQL + pgvector
- `before` 사용자 업로드 결과 저장: 로컬 artifact + DB job 상태
- `after` 사용자 입력/결과 저장: 로컬 artifact + DB 메타데이터

## 실행 전에 알아야 할 핵심 경로

### 설정 및 실행

- backend env: [backend/.env.example](/home/minsoo/after_pipeline/law_main_road/backend/.env.example:1)
- backend entry: [backend/main.py](/home/minsoo/after_pipeline/law_main_road/backend/main.py:1)
- frontend scripts: [frontend/package.json](/home/minsoo/after_pipeline/law_main_road/frontend/package.json:1)
- PostgreSQL readiness helper: [backend/verify/ensure_postgres_ready.py](/home/minsoo/after_pipeline/law_main_road/backend/verify/ensure_postgres_ready.py:1)

### 법령 데이터

- source corpus: [backend/data/law_chunks](/home/minsoo/after_pipeline/law_main_road/backend/data/law_chunks)
- upstream submodule: [data/legalize-kr](/home/minsoo/after_pipeline/law_main_road/data/legalize-kr)

### before 관련 저장 위치

- before assets: [backend/data/before_assets](/home/minsoo/after_pipeline/law_main_road/backend/data/before_assets)
- before artifacts: [backend/data/before_artifacts/runs](/home/minsoo/after_pipeline/law_main_road/backend/data/before_artifacts/runs)
- before 설정: [backend/app/before_stack/core/settings.py](/home/minsoo/after_pipeline/law_main_road/backend/app/before_stack/core/settings.py:1)

### after 관련 저장 위치

- after artifacts: [backend/data/after_artifacts/runs](/home/minsoo/after_pipeline/law_main_road/backend/data/after_artifacts/runs)
- after artifact store: [backend/app/services/after_artifact_store.py](/home/minsoo/after_pipeline/law_main_road/backend/app/services/after_artifact_store.py:1)

## 현재 구조 기준으로 유지되는 것

이 문서를 따라 실행해도 아래 구조는 그대로 유지된다.

- 기존 RAG 검색 구조
- 기존 `law_chunks` corpus
- 기존 `before`의 `standard_map.json`, `minimum_wage.yaml`
- 기존 `before`의 DB source + startup cache
- 기존 `after` retrieval / answer / document draft 흐름
- 기존 `before` / `after` artifact 저장 구조

즉, 이 문서는 새 구조를 도입하는 문서가 아니라, 현재 구조를 안전하게 실행하기 위한 문서다.

## 준비물

### 필수 소프트웨어

- WSL Ubuntu 또는 호환되는 Linux shell
- `conda`
- Python
- `pip`
- Node.js / npm
- PostgreSQL
- `pgvector`

### 필수 저장소 상태

- repo clone 완료
- submodule 초기화 완료
- `backend/.env` 생성 완료
- PostgreSQL 접근 가능

## 1. 저장소 준비

### clone

```bash
git clone <repo-url>
cd law_main_road
```

### submodule 초기화

```bash
git submodule update --init --recursive
```

확인 포인트:

- `data/legalize-kr/`가 비어 있지 않아야 한다.

문제가 생기면:

- 증상: `data/legalize-kr`가 비어 있음
- 확인:
  ```bash
  git submodule status
  ```
- 해결:
  ```bash
  git submodule update --init --recursive
  ```

## 2. Python / Node 환경 준비

### Python env

```bash
conda activate law_main_road
pip install -r backend/requirements.txt
```

### frontend env

```bash
cd frontend
npm install
cd ..
```

문제가 생기면:

- 증상: `conda activate` 실패
- 원인: non-interactive shell 또는 conda hook 미로딩
- 해결 예시:
  ```bash
  source <conda-install>/etc/profile.d/conda.sh
  conda activate law_main_road
  ```

- 증상: `npm` 없음
- 확인:
  ```bash
  node -v
  npm -v
  ```
- 해결:
  - Node 설치 또는 `nvm` 설정 확인

## 3. backend/.env 준비

기본 파일 생성:

```bash
cp backend/.env.example backend/.env
```

최소 예시:

```dotenv
DATABASE_URL=postgresql://postgres@localhost:5432/klabor
GCP_PROJECT=your-gcp-project-id
GCP_LOCATION=us-central1
VERTEX_ANSWER_MODEL=gemini-2.5-flash
```

필수/중요 변수:

- `DATABASE_URL`
- `GCP_PROJECT` 또는 `GCP_PROJECT_ID`
- `GCP_LOCATION`
- 필요 시 `GOOGLE_APPLICATION_CREDENTIALS`

문제가 생기면:

- 증상: backend import 실패
- 원인 후보:
  - `DATABASE_URL` 없음
  - 잘못된 GCP credential
- 확인:
  ```bash
  cat backend/.env
  ```

## 4. PostgreSQL 준비

현재 프로젝트는 PostgreSQL + pgvector를 사용한다.

기본 확인:

```bash
python backend/verify/ensure_postgres_ready.py
```

필요 시 로컬 postgres 시작 시도:

```bash
python backend/verify/ensure_postgres_ready.py --start-if-needed
```

이 스크립트는 아래를 확인한다.

- `DATABASE_URL` 존재
- 실제 DB connection 가능 여부
- `SELECT 1` probe 성공 여부
- 필요 시 `backend/.pgdata` 기준 로컬 postgres 시작 시도

문제가 생기면:

- 증상: `DATABASE_URL is not set`
- 해결:
  - `backend/.env`에 `DATABASE_URL` 추가

- 증상: `not_ready`
- 확인:
  ```bash
  python backend/verify/ensure_postgres_ready.py --start-if-needed
  ```
- 추가 확인:
  ```bash
  pg_isready -h 127.0.0.1 -p 5432
  ```

- 증상: local cluster 자체가 없음
- 해결 후보:
  - PostgreSQL cluster 초기화
  - 또는 외부 PostgreSQL 서버 사용

## 5. DB schema 최신화

실행:

```bash
cd backend
alembic upgrade head
cd ..
```

현재 기준 alembic head는 로컬 확인 시 `20260421_000005`다.

확인:

```bash
cd backend
alembic current
cd ..
```

문제가 생기면:

- 증상: head mismatch
- 해결:
  ```bash
  cd backend
  alembic upgrade head
  cd ..
  ```

- 증상: migration 중 DB 에러
- 확인 정보:
  - `alembic current`
  - `DATABASE_URL`
  - 오류 메시지 전체

## 6. before supplement sync

현재 `before`는 DB source를 사용하며, 수동 보강 2건을 DB supplement로 합친 상태를 기대한다.

실행:

```bash
python backend/scripts/sync_before_manual_chunks_to_db.py
```

이 단계의 목적:

- `before_assets`에만 있던 수동 보강 chunk를 DB로 반영
- `before` startup cache parity 유지

문제가 생기면:

- 증상: `before` parity mismatch
- 확인:
  ```bash
  python backend/verify/check_before_law_source_parity.py
  ```

## 7. backend 실행

실행:

```bash
python -m uvicorn backend.main:app --reload
```

접속 주소:

- health: `http://localhost:8000/health`
- before health: `http://localhost:8000/api/v1/before/health`

현재 기대 상태:

- backend import 성공
- `before` preload 완료
- `all_chunks_source = db`
- `all_chunks_count = 1724`

기본 smoke:

```bash
python -c "from backend.main import app; print('import_ok')"
```

문제가 생기면:

- 증상: import 실패
- 확인:
  ```bash
  python -c "from backend.main import app; print('import_ok')"
  ```
- 같이 전달할 정보:
  - 전체 traceback
  - `backend/.env`
  - `alembic current`

- 증상: `before` health에서 `runtime_loaded=false`
- 확인:
  - parent app startup이 정상으로 돌았는지
  - `/api/v1/before/health` 응답 전체

## 8. frontend 실행

실행:

```bash
cd frontend
npm run dev
```

현재 실제 포트:

- `http://localhost:5090`

중요:

- 현재 frontend는 `3000`이 아니라 `5090`을 사용한다.

문제가 생기면:

- 증상: 예전 문서나 습관대로 `localhost:3000`으로 열었는데 안 보임
- 해결:
  - `http://localhost:5090`으로 접속

- 증상: build 실패
- 확인:
  ```bash
  cd frontend
  npm run build
  ```

## 9. 현재 구조에서 어디에 무엇이 저장되는가

### before

사용자 업로드 원본과 결과 파일:

- 저장 루트: [backend/data/before_artifacts/runs](/home/minsoo/after_pipeline/law_main_road/backend/data/before_artifacts/runs)
- 각 run 폴더:
  - 업로드 원본 이미지/PDF
  - `ocr_output.json`
  - `review_result.json`
  - `user_explanation.md`

메타데이터:

- DB 테이블: `before_review_jobs`

### after

사용자 입력/응답 artifact:

- 저장 루트: [backend/data/after_artifacts/runs](/home/minsoo/after_pipeline/law_main_road/backend/data/after_artifacts/runs)

answer 단계 저장:

- `user_statement.txt`
- `answer_request.json`
- `answer_response.json`

draft 단계 저장:

- `user_statement.txt`
- `draft_request.json`
- `case_intake.json`
- `legal_basis.json`
- `draft_response.json`

메타데이터:

- DB 테이블: `after_artifact_runs`

## 10. 향후 `starting.sh`가 자동화할 범위

예정 경로:

- `scripts/starting.sh`

이 스크립트가 자동화해야 하는 범위:

- 현재 env 확인
- PostgreSQL readiness 확인
- `alembic upgrade head`
- `sync_before_manual_chunks_to_db.py`
- backend 실행
- frontend 실행
- 접속 주소 출력

이 스크립트가 기본 포함하면 안 되는 범위:

- 전체 chunking pipeline 재실행
- `embed_chunks.py` 실행
- DB 초기화/삭제
- Cloud Run 배포

## 11. 자주 생길 수 있는 트러블과 해결법

### 1. `conda activate`가 안 된다

증상:

- `CondaError`
- `conda: command not found`

해결:

```bash
source <conda-install>/etc/profile.d/conda.sh
conda activate law_main_road
```

### 2. PostgreSQL은 있는데 연결이 안 된다

확인:

```bash
python backend/verify/ensure_postgres_ready.py
```

해결 순서:

1. `backend/.env`의 `DATABASE_URL` 확인
2. `pg_isready -h 127.0.0.1 -p 5432`
3. `python backend/verify/ensure_postgres_ready.py --start-if-needed`

### 3. migration 상태가 오래됐다

확인:

```bash
cd backend
alembic current
cd ..
```

해결:

```bash
cd backend
alembic upgrade head
cd ..
```

### 4. before가 DB source를 안 쓰는 것 같다

확인:

```bash
curl http://localhost:8000/api/v1/before/health
```

정상 기대값:

- `runtime_loaded: true`
- `all_chunks_source: "db"`
- `all_chunks_count: 1724`

### 5. frontend는 떴는데 페이지가 이상하다

확인:

```bash
cd frontend
npm run build
```

그리고 브라우저 주소를 `5090`으로 확인한다.

### 6. after 실행 후 저장이 안 된 것 같다

확인:

- [backend/data/after_artifacts/runs](/home/minsoo/after_pipeline/law_main_road/backend/data/after_artifacts/runs)
- `after_artifact_runs` DB row

### 7. before 실행 후 저장이 안 된 것 같다

확인:

- [backend/data/before_artifacts/runs](/home/minsoo/after_pipeline/law_main_road/backend/data/before_artifacts/runs)
- `before_review_jobs` DB row

## 12. 다른 채팅/다른 세션에 전달할 정보

문제가 생겼을 때 아래 정보가 있으면 다음 세션에서 바로 이어서 보기 쉽다.

### 필수

- 실행한 명령어
- 전체 오류 메시지
- `git status -sb`
- `python -c "from backend.main import app; print('import_ok')"` 결과
- `cd backend && alembic current`
- `python backend/verify/ensure_postgres_ready.py` 결과

### before 관련이면 추가

- `curl http://localhost:8000/api/v1/before/health`
- 최근 run 폴더 경로
- `before_review_jobs` 최신 row 상태

### after 관련이면 추가

- 최근 `after_artifacts/runs/...` 경로
- `after_artifact_runs` 최신 row 상태
- answer/draft 어느 단계에서 실패했는지

## 13. 다음 문서

이 문서로 서버를 띄운 뒤에는 아래 순서로 보면 된다.

1. `스타팅 후 자체 테스트`
2. `데이터 파이프라인`
3. `각 디렉터리 및 파일의 역할`
