# Ops README

## 목적

이 문서는 `docs/ops` 디렉터리의 진입 문서다.

현재 운영 문서가 무엇인지, 지금 프로젝트가 어디까지 정리되었는지, 다음으로 무엇을 해야 하는지를 한 번에 확인하기 위한 용도로 사용한다.

## 현재 진행 상태

기준일: `2026-04-21`

현재 `ops` 문서 기준으로 정리된 상태는 아래와 같다.

- 로컬 실행 시작 문서 정리 완료
- 로컬 시작 자동화 스크립트 `scripts/starting.sh` 추가 완료
- 스타팅 후 자체 테스트 문서 정리 완료
- 데이터 파이프라인 문서 정리 완료
- 디렉터리/파일 역할 문서 정리 완료
- Cloud Run 데이터 저장 구조 문서 유지 중
- troubleshooting 문서 유지 중

현재 코드/구조 기준으로 반영된 주요 상태:

- `before` law source: DB 기준으로 전환 완료
- `before` startup cache preload: parent app startup 기준 반영 완료
- `before` job 상태: DB 저장 전환 완료
- `after` artifact 로컬 저장 구조: 반영 완료
- frontend 실제 dev/start 포트: `5090`

## 이 디렉터리에서 먼저 볼 문서

### 1. 로컬 실행 시작

- [quick_start.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/quick_start.md:1)

새 환경에서 프로젝트를 처음 실행할 때 가장 먼저 보는 문서다.

### 2. 스타팅 후 검증

- [스타팅_후_자체_테스트.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/스타팅_후_자체_테스트.md:1)

서버가 뜬 뒤 현재 상태가 정상인지 점검하는 체크 문서다.

### 3. 데이터 흐름

- [데이터_파이프라인.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/데이터_파이프라인.md:1)

법령 데이터, DB 적재, embedding, `before` supplement, 클라우드 마이그레이션 시 주의점까지 포함한 문서다.

### 4. 저장소 구조

- [각_디렉터리_및_파일의_역할.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/각_디렉터리_및_파일의_역할.md:1)

repo 전체 구조와 핵심 파일 역할을 설명하는 저장소 지도 문서다.

### 5. 클라우드 전환

- [클라우드런_데이터_저장_구조.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/클라우드런_데이터_저장_구조.md:1)

Cloud Run / Cloud SQL / GCS 구조 전환을 염두에 둔 운영 설계 문서다.

### 6. 트러블슈팅

- [troubleshooting.md](/home/minsoo/after_pipeline/law_main_road/docs/ops/troubleshooting.md:1)

반복되는 문제와 해결책을 기록하는 운영 로그 문서다.

## 관련 실행 파일

- [starting.sh](/home/minsoo/after_pipeline/law_main_road/scripts/starting.sh:1)
- [demo_preflight.sh](/home/minsoo/after_pipeline/law_main_road/scripts/demo_preflight.sh:1)

역할:

- `starting.sh`
  - 로컬 개발 시작 자동화
  - DB readiness, migration, `before` supplement sync, backend/frontend 실행
- `demo_preflight.sh`
  - 발표 전 smoke / build / readiness 점검

## 앞으로의 우선 작업

현재 문서 정리 이후 다음 단계는 아래 순서가 적절하다.

1. `ops` 문서를 `README.md` 또는 상위 문서에서 바로 찾을 수 있도록 링크 정리
2. `starting.sh` 기준 실제 실행 예시/출력 예시를 `quick_start.md`에 보강
3. `before` artifact의 GCS 전환 설계 구체화
4. `after` artifact의 향후 GCS 전환 기준 정리
5. Cloud Run 마이그레이션 시 필요한 환경 변수/시크릿 목록 별도 문서화

## 현재 남아 있는 큰 기술 작업

문서 작업과 별개로, 구조상 남아 있는 큰 전환 포인트는 아래다.

- `before` artifact 저장을 로컬 디스크에서 GCS로 전환
- `after` artifact 저장을 로컬 디스크에서 GCS로 전환
- Cloud Run 배포 시 signed URL 또는 인증 프록시 방식 결정
- 필요 시 `before` / `after` 운영 메타데이터 조회 문서 추가

## 문서 사용 원칙

- 실행 전: `quick_start.md`
- 실행 후 점검: `스타팅_후_자체_테스트.md`
- 구조 파악: `각_디렉터리_및_파일의_역할.md`
- 데이터 파악: `데이터_파이프라인.md`
- 클라우드 전환 검토: `클라우드런_데이터_저장_구조.md`
- 문제 발생 시: `troubleshooting.md`
