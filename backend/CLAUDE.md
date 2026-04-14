# CLAUDE.md — backend/

## 역할

FastAPI 애플리케이션, RAG 엔진, PostgreSQL/pgvector DB 연결, 임베딩 파이프라인을 담당하는 백엔드 루트.

## 디렉토리 구조

| 경로 | 역할 |
|------|------|
| `app/` | FastAPI 앱 코드 (라우터, 서비스, 스키마, 모델, DB 연결) |
| `app/models/` | SQLAlchemy ORM 모델 |
| `scripts/` | 운영 스크립트 (임베딩 생성 등) |
| `verify/` | 검증 스크립트 (임베딩 / retrieval 품질 체크 등) |
| `logs/` | 런타임 로그 (git 추적 제외) |
| `data/law_chunks/` | 청킹 파이프라인 출력물 (읽기 전용) |

## 수정 금지

- `data/law_chunks/` — 청킹 파이프라인 산출물. 직접 수정 금지. Step 10 재실행으로만 갱신.

## Task 진행 순서

임베딩 완료 상태와 retrieval 다음 단계 spec은 아래 문서 참조:

- `docs/planning/09_backend_embedding_plan.md`
- `docs/planning/10_backend_retrieval_plan.md`

| Task | 산출물 |
|------|--------|
| Task 1 | backend 폴더/최소 파일 구조 ✓ |
| Task 2 | `app/models/law_chunk.py` (ORM 모델) |
| Task 3 | Alembic + 마이그레이션 |
| Task 4 | `scripts/embed_chunks.py`, `verify/check_embeddings.py` ✓ |
| Task 5 | retrieval MVP (`main.py`, `services/`, `routers/`, `schemas/`, `verify/check_retrieval.py`, `eval/run_retrieval_eval.py`) ✓ |

## 환경변수

`.env.example` 참조. 실제 값은 `.env`에 작성 (git 추적 제외).
