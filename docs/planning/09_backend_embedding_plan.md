# 09. Backend Embedding Plan (Task 4 Complete)

## 현재 상태 (2026-04-13 실행 후)

| 항목 | 상태 |
|------|------|
| law_chunks 행 수 | 1722 (selected_as_of: 2026-04-11) |
| embedding 컬럼 | `Vector(768)`, nullable, **1722 / 1722 populated** |
| alembic head | `20260413_000003` |
| pgvector extension | enabled |
| 임베딩 대상 필드 | `embedding_text` (ORM: `LawChunk.embedding_text`) |
| Vertex AI SDK | `google-genai>=1.72` |
| 인증 방식 | ADC (`gcloud auth application-default login`) 또는 `GOOGLE_APPLICATION_CREDENTIALS` |
| ingestion 스크립트 | `backend/scripts/ingest_chunks.py` — embedding 컬럼 upsert 제외(안전) |
| 최종 인덱스 | `idx_law_chunks_embedding` (`hnsw`, `vector_cosine_ops`) |

현재 live note:

- 원래 Task 4 baseline은 `1713 / 1713` 완료 상태였다.
- 이후 `SCN-003` 대응으로 장애인 관련 조문 9개를 최소 범위로 추가했고, 신규 9건만 추가 임베딩하여 현재 live 상태는 `1722 / 1722`다.

---

## Historical Task 4 실행 결과

아래 수치는 Task 4 완료 당시의 historical snapshot이다. 현재 live 기준선은 문서 상단의 `1722 / 1722`를 따른다.

- `backend/scripts/embed_chunks.py` 구현 완료
- `backend/verify/check_embeddings.py` 구현 완료
- Vertex AI dry-run 검증 완료: `--dry-run --limit 10`
- 소량 저장 검증 완료: `--limit 20`
- 전체 실행 완료: 남은 `1693` rows 저장, historical final `1713 / 1713`
- 최종 검증 완료: `embedded_rows=1713`, `null_rows=0`, sample dimension `768`
- Alembic `20260413_000003` 적용 완료
- 최종 로그 상태: warning `1`, error `0`
- truncation warning `1`건:
  - `산업안전보건법시행령__제115조__ord01__mst284771__ca0ca963752d`

---

## 권장 Embedding 접근

**Provider:** Vertex AI  
**Model:** `gemini-embedding-001`  
**Dimension:** 768  
**Task type:** `RETRIEVAL_DOCUMENT`

**선택 근거:**
- `01_model_strategy.md`, `06_backend_db_foundation.md` 문서에서 이 모델로 확정
- retrieval miss가 현재 병목이라는 근거가 부족함
- GCP 환경변수(`GCP_PROJECT`, `GCP_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS`) 이미 `.env.example`에 정의
- ORM의 `Vector(768)`과 차원 일치

> **주의:** `gemini-embedding-001`의 기본 출력 차원은 3072.  
> `output_dimensionality=768`을 반드시 명시해야 pgvector INSERT 성공.

> **현재 상태 note:** runtime retrieval / answer path와 batch embedding path 모두 `google.genai` 기준으로 정리됨.

---

## 실행 전제조건

| 항목 | 확인 방법 |
|------|-----------|
| `.env` 파일 존재 | `ls backend/.env` |
| `DATABASE_URL` 설정 | `.env` 내 확인 |
| `GCP_PROJECT` / `GCP_LOCATION` 설정 | `.env` 내 확인 |
| ADC 또는 `GOOGLE_APPLICATION_CREDENTIALS` 유효 | `gcloud auth application-default login` 또는 `.env` 내 경로 확인 |
| GCP 계정 / service account — Vertex AI User 권한 | GCP IAM 콘솔 확인 |
| Vertex AI API 활성화 | GCP 콘솔: `aiplatform.googleapis.com` |
| conda 환경 활성화 | `conda activate <env>` |
| 패키지 설치 | `pip install -r requirements.txt` |
| DB 접근 가능 | `psql $DATABASE_URL -c "\dt"` |
| 실행 위치 | `backend/` 디렉토리 |

---

## 구현 대상 파일

### 1. `backend/scripts/embed_chunks.py` (신규)

**역할:** DB에서 `embedding IS NULL`인 행만 조회 → Vertex AI 호출 → embedding 업데이트

**주요 설계 결정:**
- NULL 행만 처리. `--force` 없으면 기존 embedding 절대 덮어쓰지 않음
- `--batch-size N` (기본값 5): Vertex AI `get_embeddings()` API 배치 크기
- `--limit N`: 테스트/부분 실행용
- `--dry-run`: DB 쓰기 없이 API 호출만 확인
- 실패 시: 해당 batch를 `logs/embed_chunks.log`에 기록 후 skip, 재실행 시 자동 재처리
- `tqdm` 진행 표시

**처리 흐름:**
```
1. .env 로드 → Vertex AI init
2. DB에서 embedding IS NULL 행 조회 → (chunk_id, embedding_text) 목록
3. --limit 적용
4. batch로 분할 (batch_size=5)
5. 각 batch:
   a. TextEmbeddingInput 구성 (task_type="RETRIEVAL_DOCUMENT")
   b. model.get_embeddings(inputs, output_dimensionality=768)
   c. 차원 검증: len(vector) != 768 → skip + log
   d. UPDATE law_chunks SET embedding = :vec WHERE chunk_id = :id
   e. session.commit()
   f. exception 시: rollback + log chunk_ids + continue
6. 완료: 총 처리/skip/실패 건수 출력
```

---

### 2. `backend/verify/check_embeddings.py` (신규)

**역할:** 저장된 embedding 검증

**검증 항목:**
- 전체 row 수 vs embedding != NULL 수
- 임의 5행 샘플 → 차원 수 확인 (== 768)
- historical 출력 예시: `총 1713행 / embedding 완료 N행 / NULL 남은 M행`
- current live 기대값: `총 1722행 / embedding 완료 1722행 / NULL 0행`

---

### 3. `backend/alembic/versions/20260413_000003_add_embedding_hnsw_index.py` (신규)

**역할:** 모든 embedding 채운 뒤 HNSW 벡터 인덱스 추가

```sql
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_law_chunks_embedding
ON law_chunks USING hnsw (embedding vector_cosine_ops);
```

**중요:**
- `CREATE INDEX CONCURRENTLY`는 트랜잭션 안에서 실행 불가
- migration 파일에서 `op.get_context().autocommit_block():` 사용 (alembic 1.13+)
- **이 migration은 embedding 100% 완료 후 실행할 것**

**HNSW 선택 이유:**
- 원 Task 4 baseline 1713행 규모에서도 학습 불필요, 설정 간단
- current live 1722행에서도 같은 판단 유지
- IVFFlat는 `lists` 파라미터 튜닝 + 최소 행수 조건 있음
- MVP 안정성 우선

---

## 검증 순서

```bash
# Step 1: dry-run (API 연결 확인)
python3 scripts/embed_chunks.py --dry-run --limit 10

# Step 2: 소량 실행 + 검증
python3 scripts/embed_chunks.py --batch-size 5 --limit 20
python3 verify/check_embeddings.py

# Step 3: 전체 실행
python3 scripts/embed_chunks.py --batch-size 5

# Step 4: 최종 검증
python3 verify/check_embeddings.py
# historical 기대: 전체 1713행 / embedding 완료 1713행 / NULL 0행
# current live 기대: 전체 1722행 / embedding 완료 1722행 / NULL 0행

# Step 5: 벡터 인덱스 추가 (embedding 완료 후)
alembic upgrade head
```

---

## 실제 검증 결과

```bash
python3 scripts/embed_chunks.py --dry-run --limit 10
python3 scripts/embed_chunks.py --batch-size 5 --limit 20
python3 scripts/embed_chunks.py --batch-size 5
python3 verify/check_embeddings.py --require-complete --require-index
alembic current
```

Observed result:

- `dry-run` 10건 성공
- 소량 저장 20건 성공
- historical 전체 저장 성공: `1713 / 1713`
- `check_embeddings.py` 결과:
  - historical `embedded_rows = 1713`
  - `null_rows = 0`
  - sample dimension `768`
  - `hnsw_index_exists = True`
- `alembic current` = `20260413_000003 (head)`

Current live note:

- 이후 `SCN-003` 대응으로 장애인 관련 조문 9개를 최소 범위로 추가했다.
- `backend/scripts/ingest_chunks.py` 재실행 후 current live row count는 `1722`다.
- `backend/scripts/embed_chunks.py`로 신규 9건만 추가 임베딩하여 current live `embedded_rows = 1722` 상태다.

---

## 리스크

| 리스크 | 대응 |
|--------|------|
| `output_dimensionality=768` SDK 미지원 | 현재는 `google.genai` 경로 기준으로 검증 완료. SDK 변경 시 재검증 필요 |
| Vertex AI API 할당량 초과 (429) | batch_size=5 + 실패 시 log + 재실행 전략 |
| `embedding_text` 길이 초과 (max ~2048 tokens) | article 단위 청킹으로 대부분 안전. 초과 시 WARNING 로그 |
| CONCURRENTLY migration 트랜잭션 오류 | `autocommit_block()` 패턴 사용 |
| WSL 환경 service account 경로 | `/mnt/c/...` 또는 WSL 내 절대 경로 확인 |
| SDK import 경로 변경 | 구현 세션에서 설치 버전 기준으로 재확인 필요 |

---

## 다음 액션

1. embedding baseline은 현재 유지
2. 다음 단계는 embedding 교체가 아니라 RAG refinement
3. scenario data expansion이 필요한 경우에도 frozen snapshot 정합성을 우선 유지
3. retrieval / grounding / answer 연결 품질 개선 후 embedding 재평가 여부 결정
4. latest end-to-end status는 `docs/ops/task6_answer_generation_status.md` 기준

---

## 수정 불필요 파일

| 파일 | 이유 |
|------|------|
| `backend/app/models/law_chunk.py` | `Vector(768)` 이미 정의됨 |
| `backend/scripts/ingest_chunks.py` | embedding upsert 제외 이미 구현됨 |
| `backend/requirements.txt` | `google-genai` / runtime dependency 기준으로 정리됨 |
| `backend/.env.example` | ADC / service account 둘 다 지원하도록 최소 수정됨 |
