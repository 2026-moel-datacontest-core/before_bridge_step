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
  - `SCN-001`: covered, `top_k=10` demo path stable
  - `SCN-002`: partial, extra source / structured data 필요
  - `SCN-003`: covered after minimal data addition (`+9 chunks`)
  - `SCN-004`: covered, demo ready
  - `SCN-005`: covered, demo ready

---

## Next Step

현재 RAG refinement는 landing 완료 상태로 본다. 다음 단계의 중심은 RAG를 더 넓히는 것이 아니라, 이미 검색된 법령 근거와 사용자의 사건 사실을 묶어 제출 가능한 문서 초안으로 전환하는 것이다.

### Step 0. Baseline freeze / 운영 기준 고정

- 현재 RAG 기준선을 고정한다.
  - retrieval full 60: `hit@5 = 60/60`
  - answer full 60: `citation_grounding_clean = 60/60`, `gold_citation_hit = 60/60`, `expected_point_strict_coverage = 137/153`
- 일반 API 기본값은 `top_k=5`, `ef_search=100`으로 유지한다.
- `SCN-001 Full` demo / scenario smoke에서는 `top_k=10`, `ef_search=100`을 명시한다.
- `SCN-001`, `SCN-004`, `SCN-005`를 After 핵심 시나리오로 관리한다.
- `SCN-002`, `SCN-003`은 After 핵심 데모 안정화 범위 밖으로 둔다.
- 이후 RAG 수정은 regression이 확인되거나 문서 초안 생성에 필요한 근거가 명확히 부족할 때만 좁게 진행한다.

### Step 1. Document generation scope 확정

- 문서 생성은 바로 전체 자동화를 목표로 하지 않고, 시나리오별 문서 타입을 분리한다.
- 1순위: `SCN-004`
  - 문서 타입: 노동청 진정서 초안, 노동위원회 부당해고 이유서 초안
  - 이유: 해고, 서면통지, 해고예고, 임금체불, 퇴직금 지급 문제가 현재 RAG에서 안정적으로 grounding된다.
- 2순위: `SCN-005`
  - 문서 타입: 육아휴직/가족돌봄 재신청서, 거절 사유 서면 요청서, 내용증명 초안
  - 이유: 바로 신고보다 재신청 및 서면 증거 확보 흐름이 더 자연스럽다.
- 3순위: `SCN-001`
  - 문서 타입: 외국인근로자 사업장 변경 사유 정리서, 상담용 사건 요약서
  - 이유: 계약, 기숙사, 차별, 사업장 변경 사유를 한 문서로 정리하는 데 적합하다.
- 진정서 작성 기능은 법률 판단 자동 확정이 아니라, 사용자 사실관계와 grounded legal basis를 정리하는 보조 기능으로 정의한다.

### Step 2. Case intake schema 설계

- `/api/v1/answer` 응답은 법령 근거와 행동 안내를 제공하지만, 진정서 작성에 필요한 사건 사실관계 데이터는 아직 별도 구조로 수집하지 않는다.
- 다음 단계에서는 `case dossier` 또는 `case intake` 구조를 먼저 설계한다.
- 최소 필드:
  - `scenario_id`: `SCN-004`, `SCN-005`, `SCN-001` 등
  - `document_type`: 진정서, 이유서, 재신청서, 내용증명, 상담용 요약서
  - `worker_info`: 신청인 이름, 연락처, 체류/고용 관련 정보는 MVP에서는 optional 또는 placeholder
  - `employer_info`: 회사명, 대표자, 사업장 주소, 연락처
  - `employment_info`: 입사일, 퇴사일, 직무, 임금, 근무시간, 근로계약서 유무
  - `incident_timeline`: 날짜별 사건 경위
  - `claims`: 해고, 임금체불, 퇴직금, 가족돌봄 거절, 차별, 사업장 변경 사유 등
  - `evidence_items`: 카카오톡, 문자, 이메일, 급여명세서, 통장내역, 근로계약서, 출퇴근기록, 사진, 녹취 등
  - `requested_actions`: 조사 요청, 미지급 임금 지급 요청, 퇴직금 지급 요청, 부당해고 구제, 서면 답변 요청 등
  - `legal_basis`: RAG 응답의 `cited_articles`, `grounded_context_ids`, 핵심 조문 요약
  - `missing_fields`: 문서 작성 전에 사용자에게 추가로 물어봐야 할 항목
- 개인정보는 MVP에서 최소 수집 원칙을 유지하고, 데모에서는 placeholder를 우선 사용한다.

### Step 3. Document draft API / service 설계

- 기존 `/api/v1/answer`를 무리하게 확장하지 않는다.
- 별도 문서 초안 endpoint 또는 service를 둔다.
  - 예: `POST /api/v1/documents/draft`
- 입력은 `case_dossier`와 RAG legal basis를 받는다.
- 출력은 문서 초안과 검증 정보를 함께 반환한다.
  - `title`
  - `recipient`
  - `parties`
  - `facts`
  - `legal_basis`
  - `request`
  - `evidence_checklist`
  - `missing_fields`
  - `cautions`
  - `cited_articles`
- guardrail:
  - 검색된 조문 밖의 법적 근거를 새로 만들지 않는다.
  - 사용자가 말하지 않은 사실을 단정하지 않는다.
  - 금액, 날짜, 사업장명, 당사자명은 입력값이 없으면 placeholder 또는 `확인 필요`로 둔다.
  - `위법 확정`보다 `위반 가능성`, `다툴 수 있음`, `확인 필요` 표현을 우선한다.

### Step 4. SCN-004 문서 초안 MVP 먼저 구현

- 첫 구현 대상은 `SCN-004`로 제한한다.
- 목표 문서:
  - 고용노동청 임금체불 진정서 초안
  - 지방노동위원회 부당해고 구제신청 이유서 초안
- 필수 법령 근거:
  - `근로기준법 제23조`
  - `근로기준법 제26조`
  - `근로기준법 제27조`
  - `근로기준법 제28조`
  - `근로기준법 제36조`
  - `근로자퇴직급여 보장법 제9조`
  - 필요 시 `근로기준법 제37조`
- 검증 기준:
  - RAG citation grounding 유지
  - 문서 초안에 사실관계 / 법적 근거 / 요청사항 / 증거 목록이 분리되어 출력
  - 입력되지 않은 사실은 생성하지 않고 `missing_fields`로 반환
  - SCN-004 smoke에서 제23조 survival 유지

### Step 5. SCN-005 / SCN-001 문서 타입 확장

- `SCN-005`는 신고서보다 재신청서와 내용증명 초안이 우선이다.
  - 가족돌봄 또는 육아휴직 신청 사실
  - 회사의 거절 또는 사직 압박
  - 서면 답변 요청
  - 불리한 처우 금지 근거
  - 증거 보존 안내
- `SCN-001`은 사업장 변경 사유 정리서 또는 상담용 사건 요약서가 우선이다.
  - 표준근로계약서 / 서면 명시 문제
  - 기숙사 제공 또는 숙소비 문제
  - 외국인 차별 또는 폭언
  - 사업장 변경 사유
  - 1개월 / 3개월 기준
- 각 문서 타입은 별도 template / prompt / validation case로 관리한다.

### Step 6. Draft eval / smoke 체계 추가

- answer eval과 별도로 문서 초안 eval을 만든다.
- 최소 smoke 대상:
  - `SCN-004`: 노동청 진정서 초안
  - `SCN-004`: 노동위원회 이유서 초안
  - `SCN-005`: 재신청서 또는 내용증명 초안
  - `SCN-001`: 사업장 변경 사유 정리서
- 평가 항목:
  - 필수 섹션 존재 여부
  - citation grounding 유지 여부
  - 입력되지 않은 사실 hallucination 여부
  - missing field가 적절히 표시되는지
  - 증거 체크리스트가 시나리오와 맞는지
  - 과도한 단정 표현이 없는지
- 문서 초안 기능을 수정할 때는 SCN smoke를 우선 돌리고, RAG service를 건드린 경우에만 full 60을 재실행한다.

### Step 7. Demo flow / agent 연결

- 문서 초안 API가 안정화되면 데모 흐름을 정리한다.
- 권장 데모 흐름:
  - 사용자 자유진술 입력
  - RAG answer로 권리와 근거 확인
  - 부족한 사실관계 질문 생성
  - 사용자가 추가 정보 입력
  - 진정서 / 이유서 / 재신청서 초안 생성
  - 증거 체크리스트 출력
- agent는 처음부터 복잡한 loop로 만들지 않는다.
- MVP에서는 fixed flow orchestration으로 충분하다.

### Step 8. Frontend 구현은 마지막에 진행

- backend 문서 초안 API와 smoke가 안정화된 뒤 frontend를 만든다.
- frontend 우선순위:
  - After 입력 화면
  - RAG answer 결과 화면
  - 추가 질문 / missing fields 입력 화면
  - 문서 초안 결과 화면
  - cited_articles / evidence checklist 표시
- demo stability를 위해 SCN preset 버튼을 제공한다.
  - `SCN-001 Full`: `top_k=10`, `ef_search=100`
  - `SCN-004`: `top_k=10`, `ef_search=100`
  - `SCN-005`: `top_k=10`, `ef_search=100`
- 일반 사용자의 기본 API 호출은 계속 `top_k=5`, `ef_search=100` 기준을 따른다.

### Step 9. 후순위 / 하지 말아야 할 것

- 남은 answer eval partial 16개는 현재 데모 blocker가 아니므로 문서 초안 작업보다 우선하지 않는다.
- hybrid retrieval, reranker, broad decomposition은 현재 baseline을 유지한 채 필요성이 확인될 때만 검토한다.
- `SCN-002` 자동 산재 판정형 데모에 필요한 추가 source 또는 structured data 설계는 계속 범위 밖으로 둔다.
- frontend polishing, 로그인, 관리자 기능, 운영 보안 고도화는 문서 초안 MVP 이후로 미룬다.

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
