# CLAUDE.md — law_main_road

## Project

| Item | Value |
|---|---|
| Name | K-Labor Shield |
| One-liner | 외국인 근로자를 위한 노동권 보호 통합 AI |
| Goal | 공모전 제출 안정성 중심 MVP 완성 |
| Priority | 제출 안정성 > 기능 추가 > 리팩토링 |

## Current Phase

기준일: `2026-04-17`

- RAG refinement landing 완료
- SCN-004 document draft backend 완료
- SCN-004 After frontend 4-route flow 완료
- Phase 3A/B 완료: rendered_text copy, browser print, print disclaimer
- SCN-004 QA 정합성 검증, content output 확인, manual browser rehearsal 통과
- 현재 작업 중심은 **SCN-004 demo freeze 유지와 제출 전 재현성 확인**
- 다음 확장 후보는 **SCN-005 After frontend / 문서 타입**이나, 별도 패치로만 진행
- SCN-001 frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 진행
- 현재 source of truth는 `backend/data/law_chunks/all_chunks.json`
- current live corpus: `1722` chunks, `selected_as_of = 2026-04-11`

## Structure

| Path | Role |
|---|---|
| `backend/` | FastAPI, retrieval / answer / document draft, LLM routing, DB |
| `frontend/` | Next.js SCN-004 After demo 웹앱 |
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
- 현재 frozen output metadata 기준은 `selected_as_of = 2026-04-11`
- current live source of truth는 SCN-003 최소 보강 `+9` chunks 포함 `1722` chunks
- 초안이 아니라 **수정 확정본** 기준으로 작업
- `docs/planning/`은 기준 문서. 상세 설계는 거기서 확인
- 개인정보 최소 수집 원칙 유지
- 로그인/이메일/전화번호 수집 기능 추가 금지
- SCN-004 freeze 기준을 깨는 신규 기능 추가 금지
- 현재 다음 단계는 SCN-004 demo freeze 유지와 제출 전 재현성 확인
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

1. `docs/planning/00_project_overview.md`
2. `docs/planning/02_rag_strategy.md`
3. `docs/planning/03_chunking_pipeline.md`
4. `docs/planning/04_architecture.md`
5. `docs/planning/05_eval_plan.md`
6. current directory `CLAUDE.md`
7. existing code

## Directory Notes

### `scripts/`
- 청킹/전처리 민감 구간
- Step 1/4/7 수정본 기준
- pipeline 재실행 command는 `--as-of 2026-04-10` 기준으로 재현성 우선
- 현재 frozen output metadata 기준은 `selected_as_of = 2026-04-11`
- current live source of truth는 `1722` chunks
- `article_ordinal` 충돌 방지 중요
- Step 9 실패 시 다음 단계 진행 금지

### `backend/`
- `POST /api/v1/retrieve`, `POST /api/v1/answer`, `POST /api/v1/documents/draft` 구현 완료
- 일반 `/api/v1/retrieve`와 `/api/v1/answer` 기본값은 `top_k=5`, `ef_search=100`
- SCN demo / scenario smoke는 `top_k=10`, `ef_search=100` 명시
- HIGH/MEDIUM 민감 작업은 local LLM 우선
- 현재 implemented answer / embedding path는 Vertex AI Gemini 기준
- 환각 방지 규칙 유지
- cited_articles 없는 법률 답변 금지
- `/api/v1/documents/draft`는 `/api/v1/answer` legal basis 안의 근거만 사용
- draft service는 retrieval / answer_generation service를 직접 호출하지 않음
- 사용자가 입력하지 않은 사실은 단정하지 않고 placeholder 또는 `missing_fields`로 남김
- SCN-005 After 문서 타입 확장은 SCN-004 freeze 기준을 유지한 별도 패치에서 진행 가능
- SCN-001 문서 타입 / Before-Bridge-After 확장은 팀원 Before / Bridge 코드와 contract 확인 후 검토

### `frontend/`
- 한국어 메인 / 영어 보조
- 발표 데모 안정성 우선
- backend schema 확인 없이 응답 필드 가정 금지
- 현재 구현 범위는 SCN-004 After 4-route flow: `/after`, `/after/result`, `/after/intake`, `/after/draft`
- `/before`, `/bridge`, Recovery 확장은 현재 freeze 범위에서 진행하지 않음
- 현재 SCN-004 demo freeze 유지 작업과 SCN-005 문서 타입 frontend 확장을 한 패치에 섞지 않음
- SCN-005 After frontend / 문서 타입 확장은 SCN-004 freeze 기준을 유지한 별도 패치에서 진행 가능
- SCN-001 `Before -> Bridge -> After` frontend 확장은 팀원 Before / Bridge 코드와 contract 확인 후 별도 단계에서 검토
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response`는 Web Storage에 저장하지 않음
- SCN-004 preset은 `top_k=10`, 자유 입력은 `top_k=5`, 항상 `ef_search=100`

## Do Not

- `data/legalize-kr/` 수정
- 초안 코드 재사용
- 계획 문서와 다른 방향으로 독단 수정
- 과도한 구조 변경
- 여러 feature 브랜치 동시 작업 전제 코드 작성
- API contract를 frontend 편의만으로 변경
- RAG / answer / retrieval behavior 변경 없는 doc-only 작업에서 broad full eval 실행
- raw case facts 또는 full answer/draft payload를 browser storage에 저장

## Reminder

- root `CLAUDE.md`는 전역 요약본
- 상세 규칙은 하위 `CLAUDE.md`와 `docs/planning/*` 참조
- 현재 목표는 “완벽한 구조”가 아니라 “안정적으로 제출 가능한 결과물”
- 2026-04-17 기준 RAG refinement, SCN-004 document draft backend, SCN-004 After frontend Phase 3A/B, SCN-004 content QA, manual browser rehearsal까지 완료됨. 다음 실질 작업은 SCN-004 demo freeze 유지이며, 이후 후보는 SCN-005 After frontend / 문서 타입 확장
