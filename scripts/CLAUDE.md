# scripts/CLAUDE.md

## Scope
- 법령 전처리 / 청킹 파이프라인 전용

## Fixed Order
- Step 1 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10
- Step 2, 3 separate run 금지

## Rules
- Step 1 / 4 / 7은 수정 확정본 기준
- `data/legalize-kr/` 직접 수정 금지
- 기준일 재현성 우선: `--as-of 2026-04-10`
- `article_ordinal` 보존 필수
- Step 9 실패 시 다음 단계 진행 금지

## Output
- 결과 저장 위치: `backend/data/law_chunks/`

## Current Status
- chunking pipeline은 frozen 상태
- current source of truth는 `backend/data/law_chunks/all_chunks.json`
- current live chunks는 `1722`
- 다음 작업은 chunk 재생성이 아니라 SCN-004 frontend/backend QA 정합성 검증
