# AGENTS.md — law_main_road

## Purpose

실행 중심 작업 가이드.  
전역 규칙은 `CLAUDE.md`, 상세 설계는 `docs/planning/*`, 영역별 규칙은 하위 `CLAUDE.md` 참조.

## Read Order

1. `CLAUDE.md`
2. related file under `docs/planning/`
3. local `CLAUDE.md` in current directory
4. existing code
5. this file

## Repo Layout

| Path | Use |
|---|---|
| `backend/` | FastAPI, RAG, agents, DB |
| `frontend/` | Next.js UI |
| `scripts/` | preprocessing / chunking pipeline |
| `data/legalize-kr/` | source submodule |
| `backend/data/law_chunks/` | preprocessing outputs |
| `docs/` | planning / product / demo / ops |
| `eval/` | eval set / metrics |

## Environment

| Item | Value |
|---|---|
| OS | WSL Ubuntu |
| Python env | conda |
| Main env | project-specific env, not `base` |
| Package manager | `pip` inside conda env |
| Node | frontend only |

## Setup

### Python / repo
```bash
conda activate law_main_road
git status
````

### if repo is not initialized

```bash
git init
mkdir -p data scripts backend/data/law_chunks
git submodule add https://github.com/legalize-kr/legalize-kr.git data/legalize-kr
git submodule update --init --recursive
pip install python-frontmatter
```

## Core Commands

### chunking pipeline

```bash
python scripts/step1_select_effective_snapshots.py --as-of 2026-04-10
python scripts/step4_chunk_articles.py
python scripts/step5_normalize.py
python scripts/step6_split_long_articles.py
python scripts/step7_finalize_metadata.py
python scripts/step8_dedupe_and_validate.py
python scripts/step9_quality_check.py
python scripts/step10_finalize.py
```

### backend

```bash
uvicorn backend.main:app --reload
```

### frontend

```bash
cd frontend
npm install
npm run dev
```

## Working Rules

* 작은 단위로 수정
* 관련 문서 먼저 읽고 작업
* 기존 구조 존중
* 불필요한 전역 리팩토링 금지
* 스키마 변경은 최소화
* 문서와 코드 정합성 유지
* 불확실하면 TODO 또는 note 남기기

## Chunking Rules

* Step order fixed: `1 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10`
* Step 2, 3 do not run separately
* Step 1 / 4 / 7 are patched versions
* `--as-of 2026-04-10` 기준으로 재현성 우선
* Step 9 실패 시 다음 단계 진행 금지
* `article_ordinal` 보존
* `data/legalize-kr/` 직접 수정 금지

## Backend Rules

* HIGH / MEDIUM 민감 작업: local LLM 우선
* LOW 작업: Vertex AI 허용
* 법률 답변에는 `cited_articles` 필요
* 검색 결과에 없는 조문 인용 금지
* API contract 임의 변경 금지

## Frontend Rules

* Korean primary, English secondary
* demo stability first
* backend schema 확인 없이 응답 필드 가정 금지

## Git Rules

| Branch      | Use                 |
| ----------- | ------------------- |
| `main`      | stable / submission |
| `dev`       | integration         |
| `feature/*` | focused task branch |

### commit style

* small commits
* prefix with phase when relevant
* use: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Do Not

* edit `data/legalize-kr/`
* revive deprecated draft scripts
* add new major features after freeze
* collect personal identity info
* change planning docs in-place without reason
* mix unrelated changes in one patch

## Preferred Task Flow

1. read docs
2. inspect current code
3. modify smallest valid scope
4. run relevant command/test
5. summarize what changed
6. leave next step clear

## References

* `docs/planning/00_final_master_plan.md`
* `docs/planning/01_rag_strategy.md`
* `docs/planning/02_chunking_pipeline.md`
* `docs/planning/03_architecture.md`
* `docs/planning/04_eval_plan.md`


