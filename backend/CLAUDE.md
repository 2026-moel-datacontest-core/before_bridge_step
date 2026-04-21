# CLAUDE.md — backend/

## 역할

FastAPI 애플리케이션, RAG 엔진, PostgreSQL/pgvector DB 연결, 임베딩 파이프라인, SCN-004 문서 초안 API를 담당하는 백엔드 루트.

## 디렉토리 구조

| 경로 | 역할 |
|------|------|
| `app/` | FastAPI 앱 코드 (라우터, 서비스, 스키마, 모델, DB 연결) |
| `app/models/` | SQLAlchemy ORM 모델 |
| `scripts/` | 운영 스크립트 (임베딩 생성 등) |
| `verify/` | 검증 스크립트 (임베딩 / retrieval / answer / document draft 품질 체크 등) |
| `logs/` | 런타임 로그 (git 추적 제외) |
| `data/law_chunks/` | 청킹 파이프라인 출력물 (읽기 전용) |

## 수정 금지

- `data/law_chunks/` — 청킹 파이프라인 산출물. 직접 수정 금지. Step 10 재실행으로만 갱신.

## Task 진행 순서

임베딩 / retrieval / answer / document draft 상태는 아래 문서 참조:

- `docs/planning/09_backend_embedding_plan.md`
- `docs/planning/10_backend_retrieval_plan.md`
- `docs/ops/README.md`
- `docs/planning/13_document_draft_plan.md`

| Task | 산출물 |
|------|--------|
| Task 1 | backend 폴더/최소 파일 구조 ✓ |
| Task 2 | `app/models/law_chunk.py` (ORM 모델) |
| Task 3 | Alembic + 마이그레이션 |
| Task 4 | `scripts/embed_chunks.py`, `verify/check_embeddings.py` ✓ |
| Task 5 | retrieval MVP (`main.py`, `services/`, `routers/`, `schemas/`, `verify/check_retrieval.py`, `eval/run_retrieval_eval.py`) ✓ |
| Task 6 | grounded answer generation, citation grounding, answer eval ✓ |
| Task 7 | SCN-004 document draft API, fixtures, smoke ✓ |

## 현재 상태

- `POST /api/v1/retrieve` 구현 완료
- `POST /api/v1/answer` 구현 완료
- `POST /api/v1/documents/draft` 구현 완료
- RAG refinement landing 완료
- SCN-004 answer completeness 보강과 document draft smoke 통과
- SCN-004 demo freeze와 presentation-local fixed answer frontend path 확인 완료
- full 60 answer evidence report 기준 `FAIL=0`, citation grounding / context id clean 확인 완료
- 다음 backend 작업은 기능 확장이 아니라 SCN-004 demo freeze 유지와 regression 발생 시 좁은 수정

## Document Draft 규칙

- draft service는 retrieval / answer_generation service를 직접 호출하지 않음
- request로 받은 `legal_basis.cited_articles`, `source_context_ids`, `retrieved_chunks` 안에서만 근거 사용
- 사용자가 입력하지 않은 사실은 단정하지 않고 placeholder 또는 `missing_fields`로 남김
- `SCN-005` 문서 타입 확장은 SCN-004 freeze 기준을 유지한 별도 패치에서 진행 가능
- `SCN-001` 문서 타입 확장은 팀원 Before / Bridge code / contract 확인 전 추가하지 않음
- presentation fixed answer fixture는 frontend code에 있으며 backend API contract를 변경하지 않는다.

## 환경변수

`.env.example` 참조. 실제 값은 `.env`에 작성 (git 추적 제외).
