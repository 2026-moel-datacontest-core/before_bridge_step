# Project Overview

## Project

- **Name:** K-Labor Shield
- **Goal:** 외국인 근로자를 위한 노동권 보호 통합 AI
- **Priority:** 제출 안정성 > 기능 추가

---

## One-line Summary

- 외국인 근로자가 계약서 또는 산업재해 상황을 입력
- AI가 관련 노동법·산재법 조문 검색
- 근거 기반 위험 신호 및 다음 행동 안내 제공

---

## Problem

- 외국인 근로자의 한국 노동법 이해도 부족
- 계약서 위험 조항 판단 어려움
- 산업재해 및 노동분쟁 대응 절차 이해 어려움
- 언어 장벽으로 제도 접근성 낮음
- 정보는 있어도 실제 상황과 연결해 해석하기 어려움

---

## Core Structure

### Before
- 근로계약서 분석
- 주요 항목 추출
- 위험 신호 탐지
- 관련 법령 조문 제시

### After
- 산업재해 / 노동분쟁 상황 입력
- 사건 정보 구조화
- 관련 법령 검색
- 다음 행동 안내

### Bridge
- Before 결과 저장
- After 분석 시 이전 위험 신호 연결
- 계약 단계에서 예견 가능했던 위험 제시

### Recovery
- 회복 및 전환 지원 단계
- 현재 MVP 핵심 범위는 아님
- 이후 확장 기능

---

## Main Users

### Primary Users
- 외국인 근로자
- 한국 노동법 및 산재 절차에 익숙하지 않은 사용자
- 계약서 및 사고 상황을 한국어/영어로 설명해야 하는 사용자

### Secondary Users
- 외국인 노동 지원 활동가
- 상담 보조 인력
- 공공기관 / 지원센터 실무자

---

## MVP Direction

- 법령 retrieval이 실제로 동작하는지 검증
- 질문 → 관련 조문 검색 → 근거 포함 응답 흐름 확인
- 복잡한 인프라보다 검색 품질과 응답 구조 우선
- 현재는 Gemini API 기반 MVP 우선
- 이후 필요 시 GCP + Ollama 기반 Local LLM 구조 확장

---

## Current Status

기준일: `2026-04-17`

- legalize-kr submodule 연결 완료
- 청킹 Step 1~10 완료
- 최종 산출물: `backend/data/law_chunks/all_chunks.json`
- chunking 기준일: `2026-04-11`
- 청크 수: `1722`
- backend Task 2, 3, 4, 5 완료
- PostgreSQL + pgvector 로컬 DB 구성 완료
- Alembic migration 적용 완료 (`20260413_000003`)
- `law_chunks` 테이블 생성 완료
- `law_chunks` 1722건 ingestion 완료
- `law_chunks.embedding` 1722건 저장 완료
- HNSW vector index (`idx_law_chunks_embedding`) 생성 완료
- embedding 최종 검증 완료: `NULL 0`, sample dimension `768`
- FastAPI retrieval app skeleton 구현 완료
- query embedding service (`RETRIEVAL_QUERY`, `768`) 구현 완료
- pgvector cosine retrieval + `SET LOCAL hnsw.ef_search` 구현 완료
- `POST /api/v1/retrieve` 구현 및 live HTTP 검증 완료
- retrieval 검증 스크립트 / eval runner 구현 완료
- retrieval eval baseline:
  - `hit@1 = 51/60 (85.00%)`
  - `hit@3 = 59/60 (98.33%)`
  - `hit@5 = 60/60 (100.00%)`
- grounded answer generation MVP 구현 완료
- `POST /api/v1/answer` 구현 및 live 검증 완료
- citation grounding / fail-closed / timeout / verify/eval 안정화 완료
- default answer model: `gemini-2.5-flash`
- default embedding model: `gemini-embedding-001`
- full 60 answer eval 기준:
  - `items_answered = 60/60`
  - `JSON/schema failure = 0`
  - `timed_out_ids = []`
  - `citation_grounding_clean = 60/60`
  - `gold_citation_hit = 60/60`
  - `expected_point_strict_coverage = 137/153`
  - `failures_or_partial_coverage = 16`
- scenario expansion / demo coverage 기준:
  - `SCN-001`: covered, `top_k=10` demo path stable
  - `SCN-002`: partial, extra source / structured data 필요
  - `SCN-003`: covered after minimal data addition (`+9 chunks`)
  - `SCN-004`: covered, frontend demo implemented
  - `SCN-005`: covered, demo ready
- RAG refinement landing 완료:
  - Step 1 phrasing normalization 적용
  - Step 2 answer-side deterministic hardening 적용
  - Step 3 rerank 미적용
  - Step 4 selective decomposition은 `SCN-001 Full` demo path에 한해 `top_k >= 8` 조건부 적용
- document draft MVP 완료:
  - `POST /api/v1/documents/draft`
  - `SCN-004` 노동청 임금체불 진정서 초안
  - `SCN-004` 노동위원회 부당해고 구제신청 이유서 초안
  - answer-derived legal basis fixture smoke 완료
- frontend MVP 완료:
  - Next.js `16.2.4`, React `19.2.5`
  - `/after`, `/after/result`, `/after/intake`, `/after/draft`
  - 실제 `/api/v1/answer`, `/api/v1/documents/draft` 연동
  - loading/error/a11y/route guard 및 copy/print 구현
  - Phase 3C 이후 확장 작업은 보류
- SCN-004 QA/content/frontend rehearsal 완료:
  - preset answer `cited_articles=6`, `grounded_context_ids=[1, 2, 3, 5, 10, 4]`
  - answer key points에 노동위원회와 3개월 이내 구제신청 표시
  - answer-derived document draft 2종 모두 `missing_legal_basis=[]`
  - manual browser rehearsal에서 `/after -> /after/result -> /after/intake -> /after/draft`, copy, print, direct URL guard 확인

---

## Next Step

현재 RAG refinement, SCN-004 문서 초안 backend, SCN-004 After frontend 구현, SCN-004 QA/content/frontend rehearsal은 완료 상태로 본다. 다음 단계의 중심은 기능 확장이 아니라 **demo freeze 유지와 제출 전 재현성 확인**이다.

### Step 0. Baseline freeze / 운영 기준 고정

- 현재 RAG 기준선을 고정한다.
  - retrieval full 60: `hit@5 = 60/60`
  - answer full 60: `citation_grounding_clean = 60/60`, `gold_citation_hit = 60/60`, `expected_point_strict_coverage = 137/153`
- 일반 API 기본값은 `top_k=5`, `ef_search=100`으로 유지한다.
- SCN demo preset은 `top_k=10`, `ef_search=100`을 명시한다.
- `SCN-004` After document draft flow를 제출 전 핵심 demo path로 관리한다.
- 이후 RAG 수정은 QA에서 regression이 확인되거나 필수 근거 누락이 재현될 때만 좁게 진행한다.

### Step 1. Backend contract 재확인

- `/api/v1/answer` 응답 schema와 frontend `AnswerResponse` 타입 정합성을 유지한다.
- `/api/v1/documents/draft` 응답 schema와 frontend `DocumentDraftResponse` 타입 정합성을 유지한다.
- `buildLegalBasis()`가 `grounded_context_ids`에 해당하는 `retrieved_chunks`만 전달하는지 유지 확인한다.
- `buildCaseIntake()`가 빈 문자열 row를 제거하고 기본 object/list를 채우는지 유지 확인한다.
- `check_document_draft.py`로 manual fixture와 answer-derived fixture smoke를 유지한다.

### Step 2. Frontend flow 재확인

- `/after` preset / 자유 입력의 `top_k` 분기를 유지한다.
- `/after/result` citation 없음 / grounded context 없음 guard를 유지한다.
- `/after/intake` 빈 필드 허용과 draft submit payload를 유지한다.
- `/after/draft` rendered_text, missing_fields, cautions, evidence_checklist, cited_articles 표시를 유지한다.
- direct URL guard:
  - `/after/result`에 state 없음 -> `/after`
  - `/after/intake`에 answer 없음 -> `/after`
  - `/after/intake`에 document_type 없음 -> `/after/result`
  - `/after/draft`에 draft 없음 -> `/after`
- copy / print 동작과 print disclaimer 확인

### Step 3. Scope freeze

- Phase 3C 이후 확장 작업은 보류한다.
  - sessionStorage backup/restore
  - transition animation
  - `/before`, `/bridge`, Recovery frontend 확장
  - 현재 SCN-004 freeze 작업 중 SCN-005 문서 타입 추가
  - 팀원 Before / Bridge contract 확인 없는 SCN-001 문서 타입 추가
- 개인정보 저장 금지 원칙을 유지한다.
- raw `user_statement`, `answer_response`, `case_intake`, `draft_response`는 Web Storage에 저장하지 않는다.

### Step 4. Demo readiness

- backend:
  - `python backend/verify/check_document_draft.py`
  - 필요 시 SCN-004 answer smoke
- frontend:
  - `npm run build`
  - local dev server에서 desktop/mobile smoke
- QA 통과 후 발표용 입력 문구, 기대 citation, fallback 문구를 문서화한다.

### Step 5. 후순위 / 하지 말아야 할 것

- 남은 answer eval partial 16개는 현재 데모 blocker가 아니므로 문서 초안 작업보다 우선하지 않는다.
- hybrid retrieval, reranker, broad decomposition은 현재 baseline을 유지한 채 필요성이 확인될 때만 검토한다.
- `SCN-002` 자동 숫자 판정형 데모에 필요한 추가 source 또는 structured data 설계는 계속 범위 밖으로 둔다.
- frontend 신규 화면, 로그인, 관리자 기능, 운영 보안 고도화는 QA 이후로 미룬다.

---

## Related Docs

### Planning
- `docs/planning/01_model_strategy.md`
- `docs/planning/02_rag_strategy.md`
- `docs/planning/03_chunking_pipeline.md`
- `docs/planning/04_architecture.md`
- `docs/planning/05_eval_plan.md`
- `docs/planning/06_backend_db_foundation.md`
- `docs/planning/07_backend_ingestion.md`
- `docs/planning/08_frontend_app_plan.md`
- `docs/ops/task6_answer_generation_status.md`

### Product
- `docs/product/before_flow.md`
- `docs/product/after_flow.md`
- `docs/product/bridge_flow.md`
- `docs/product/recovery_flow.md`
- `docs/product/mvp_scope.md`
