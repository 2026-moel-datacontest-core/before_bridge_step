# Chunking Pipeline

## Completed
- Step 1~10 완료
- 최종 출력: `backend/data/law_chunks/all_chunks.json`
- 기준일: `2026-04-11`
- Step 1~10 baseline 산출물: `1713` chunks
- 현재 live source of truth: `1722` chunks

## Notes
- Step 1은 historical snapshot selection 수정 반영
- Step 4/5/6/7/8/9/10 정상 완료
- scripts intermediate json은 중간 산출물
- backend 작업은 현재 `all_chunks.json`을 고정 입력으로 사용
- 현재 retrieval / answer generation / eval은 모두 이 산출물을 기준으로 고정 검증 중
- 현재 `1722`는 원래 파이프라인 baseline `1713`에 더해, `SCN-003` 대응을 위한 최소 범위 장애인 관련 조문 9개가 script-compatible schema로 추가 반영된 상태다

## Current Role

- chunking 파이프라인은 현재 frozen 상태
- RAG refinement와 SCN-004 frontend/backend QA 정합성 검증은 완료 상태이며 다음 단계는 SCN-004 demo freeze 유지
- 이후 수정 세션에서도 기본 입력은 계속 `all_chunks.json`을 source of truth로 유지
