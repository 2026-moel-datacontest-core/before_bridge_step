# CLAUDE.md — law_main_road

## Project

| Item | Value |
|---|---|
| Name | K-Labor Shield |
| One-liner | 외국인 근로자를 위한 노동권 보호 통합 AI |
| Goal | 공모전 제출 안정성 중심 MVP 완성 |
| Priority | 제출 안정성 > 기능 추가 > 리팩토링 |

## Structure

| Path | Role |
|---|---|
| `backend/` | FastAPI, RAG, agents, LLM routing, DB |
| `frontend/` | Next.js 웹앱, 한/영 UI |
| `scripts/` | 데이터 전처리 / 청킹 Step 1~10 |
| `data/legalize-kr/` | 법령 원본 git submodule |
| `backend/data/law_chunks/` | 전처리 결과 저장 위치 |
| `docs/planning/` | 확정 계획 문서 |
| `docs/product/` | Before / After / Bridge / Recovery 플로우 |
| `docs/demo/` | 발표 / 시연 자료 |
| `docs/ops/` | 환경 세팅 / 실행 가이드 |
| `eval/` | 평가셋 / 지표 측정 |

## Stack

| Area | Choice |
|---|---|
| Backend | FastAPI, PostgreSQL, pgvector |
| Local LLM | Ollama + Qwen3-14B |
| External LLM | Vertex AI Gemini 2.5 Flash |
| OCR | Vertex AI Gemini 2.5 Flash |
| Embedding | Vertex AI `gemini-embedding-001` |
| Reranker | BGE-reranker-v2-m3 |
| Frontend | Next.js |
| Deploy | GCP |
| Dev Env | WSL + conda |

## Global Rules

- `data/legalize-kr/` 직접 수정 금지
- 전처리 결과는 `backend/data/law_chunks/`에만 저장
- 청킹 파이프라인 순서 고정: `1 → 4 → 5 → 6 → 7 → 8 → 9 → 10`
- Step 2, 3은 별도 실행하지 않음
- 초안이 아니라 **수정 확정본** 기준으로 작업
- `docs/planning/`은 기준 문서. 상세 설계는 거기서 확인
- 개인정보 최소 수집 원칙 유지
- 로그인/이메일/전화번호 수집 기능 추가 금지
- Feature Freeze 이후 신규 기능 추가 금지
- 제출 안정성 우선. 막히면 범위 축소 허용
- API contract 임의 변경 금지
- 하위 디렉토리 작업 시 해당 디렉토리 `CLAUDE.md` 우선 확인

## Branch Rules

| Branch | Purpose |
|---|---|
| `main` | 안정 버전 / 제출 기준 |
| `dev` | 통합 개발 |
| `feature/*` | 기능 단위 작업 |

## Work Rules

- 작은 단위로 수정
- 불필요한 전역 리팩토링 금지
- 문서와 코드 정합성 유지
- 계획 변경 시 기존 기준 문서를 덮어쓰지 말고 새 문서 추가
- 작업 전 관련 문서 먼저 확인

## Read Order

1. `docs/planning/00_final_master_plan.md`
2. `docs/planning/01_rag_strategy.md`
3. `docs/planning/02_chunking_pipeline.md`
4. `docs/planning/03_architecture.md`
5. `docs/planning/04_eval_plan.md`
6. current directory `CLAUDE.md`
7. existing code

## Directory Notes

### `scripts/`
- 청킹/전처리 민감 구간
- Step 1/4/7 수정본 기준
- `article_ordinal` 충돌 방지 중요
- Step 9 실패 시 다음 단계 진행 금지

### `backend/`
- RAG 1차/2차/3차 계층 유지
- HIGH/MEDIUM 민감 작업은 local LLM 우선
- 환각 방지 규칙 유지
- cited_articles 없는 법률 답변 금지

### `frontend/`
- 한국어 메인 / 영어 보조
- 발표 데모 안정성 우선
- backend schema 확인 없이 응답 필드 가정 금지

## Do Not

- `data/legalize-kr/` 수정
- 초안 코드 재사용
- 계획 문서와 다른 방향으로 독단 수정
- 과도한 구조 변경
- 여러 feature 브랜치 동시 작업 전제 코드 작성

## Reminder

- root `CLAUDE.md`는 전역 요약본
- 상세 규칙은 하위 `CLAUDE.md`와 `docs/planning/*` 참조
- 현재 목표는 “완벽한 구조”가 아니라 “안정적으로 제출 가능한 결과물”