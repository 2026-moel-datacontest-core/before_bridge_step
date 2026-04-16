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
  - `SCN-001`: covered, retrieval ranking issue
  - `SCN-002`: partial, extra source / structured data 필요
  - `SCN-003`: covered after minimal data addition (`+9 chunks`)
  - `SCN-004`: covered, demo ready
  - `SCN-005`: covered, demo ready

---

## Next Step

- 현재 landing 완료 상태이며 immediate mandatory work는 없음
- 후속이 필요하면 남은 partial에 대한 answer-side surface / completeness cleanup 우선
- `SCN-001` decomposition은 demo 필요성이 다시 생길 때만 별도 검토
- `SCN-002` 자동 판정형 데모에 필요한 추가 source 또는 structured data 설계는 계속 범위 밖
- agent / frontend 연결은 이 기준선 위에서 후속 진행
- hybrid / reranker는 현재 baseline을 유지한 채 필요성 측정 후 결정

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
