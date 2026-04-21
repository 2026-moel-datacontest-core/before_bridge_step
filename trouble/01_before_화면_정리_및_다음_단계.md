# Before Polish And Next Steps

기준일: `2026-04-21`

공통 전제:

- 모든 수정은 현재 사용자에게 보이는 UI 구조와 기존 기능 동작을 유지하는 범위에서만 진행한다.
- 정리, 보안 보강, 안정화, 리팩터링이 필요하더라도 현재 확인 가능한 화면 흐름과 기능 결과를 바꾸지 않는 것을 우선한다.

목적:

- 현재 `frontend/src/app/before` 상태에서 남아 있는 정리 항목을 기록한다.
- `before_web` 원본 UI와 비교했을 때 아직 다듬어야 할 부분을 빠르게 확인할 수 있게 한다.
- 다음 단계인 브라우저 QA와 API adapter 설계를 분리해서 볼 수 있게 한다.
- 특히 원본 `before_web`의 섹션 노출 순서를 기준으로 현재 `/before` 구조가 어디서 어긋났는지 남긴다.

---

## 1. 현재 상태 요약

현재 `/before`에는 아래 흐름이 main 안으로 1차 흡수되어 있다.

- 업로드 패널
- 로딩 패널
- 결과 패널
- 장애 특화 안내 패널

관련 주요 파일:

- `frontend/src/app/before/page.tsx`
- `frontend/src/app/before/page.module.css`
- `frontend/src/components/before/UploadPanel.tsx`
- `frontend/src/components/before/LoadingPanel.tsx`
- `frontend/src/components/before/ResultPanel.tsx`
- `frontend/src/components/before/AccessibilityPanel.tsx`
- `frontend/src/lib/before-api.ts`
- `frontend/src/types/before.ts`

검증 상태:

- `frontend`에서 `npm run build` 통과

---

## 2. 아직 정리해야 할 항목

### A. 구조 재정렬

현재 가장 큰 이슈는 시각 polish보다 구조다.

원본 `before_web`는 아래 순서로만 섹션이 나타난다.

1. hero
2. upload section
3. loading section
4. result section
5. result section 안의 accessibility panel

현재 `/before`는 업로드 단계에서도 오른쪽 `supportColumn`이 항상 보이고 그 안에 `AccessibilityPanel`이 들어가 있다.
이 구조는 원본과 다르다.

정리해야 할 핵심:

- 업로드 초기 화면에서는 `UploadPanel`만 보여야 한다.
- `LoadingPanel`은 분석 시작 후 업로드 섹션 아래에 별도 섹션으로 생성되어야 한다.
- `ResultPanel`은 결과가 생긴 뒤에만 생성되어야 한다.
- `AccessibilityPanel`은 결과 섹션 오른쪽에서만 나타나야 한다.
- 현재 상시 노출 중인 `supportColumn`과 상태별 안내 카드는 제거하거나 결과 단계로 재배치해야 한다.

### B. 브라우저 기준 시각 QA

코드상 구조는 붙었지만 실제 화면 확인이 더 필요하다.

- desktop에서 hero 높이와 feature card 균형 확인
- 구조 수정 후 upload / loading / result / accessibility 패널 사이 간격 확인
- 버튼 크기와 우선순위가 자연스러운지 확인
- `result` 상태에서만 좌우 컬럼이 보이는지 확인
- `result` 상태에서 좌우 컬럼 높이 차이가 과하지 않은지 확인
- evidence toggle 열고 닫을 때 시선 흐름이 자연스러운지 확인

### C. 모바일 레이아웃 QA

현재 CSS는 반응형 처리가 들어가 있지만 실제 화면 점검은 필요하다.

- `/before` hero 문구가 줄바꿈 없이 과도하게 길어지지 않는지
- 업로드 패널의 mock 버튼 3개가 모바일에서 눌리기 쉬운지
- 결과 패널의 status/severity badge가 줄바꿈 시 깨지지 않는지
- accessibility option chip 2열 배치가 좁은 화면에서 어색하지 않은지

### D. 결과 정보 밀도 보강 여부 판단

현재 result panel은 핵심 구조는 들어왔지만 원본 `before_web`보다 약간 단순화돼 있다.

- 업로드 원본 이미지 preview를 다시 넣을지 결정
- summary notes 외에 추가 보조 카드가 필요한지 판단
- 결과 화면에서 contract info 블록을 더 상세히 보여줄지 검토

### E. 로딩 상태 polish

현재 mock step 진행은 동작하지만 실제 서비스처럼 보이도록 더 다듬을 수 있다.

- running step에 더 강한 시각 강조를 넣을지 검토
- 단계 전환 시간과 리듬이 자연스러운지 확인
- 분석 중 버튼/상태 메시지가 과하게 중복되는지 점검

### F. 접근성 패널 polish

현재 패널은 구조상 완성됐지만 카드 종류 차별화는 아직 최소 수준이다.

- `right`, `support`, `question`, `law` 카드별 시각 차이 강화 여부 검토
- 선택된 장애 유형 chip 강조 강도 점검
- `다음 단계` 카드에 실제 링크/행동 유도 요소를 넣을지 판단

---

## 3. 원본 before_web 대비 차이 메모

원본 `before_web`와 비교했을 때 아직 차이가 남아 있는 지점:

1. 가장 큰 차이는 섹션 노출 순서다.
2. 원본은 업로드 단계에서 `UploadPanel`만 보이는데, 현재는 오른쪽 보조 컬럼이 상시 노출된다.
3. 원본은 `AccessibilityPanel`이 결과 섹션 오른쪽에만 나오는데, 현재는 업로드 단계에서도 함께 보인다.
4. 상단 hero는 많이 가까워졌지만 원본의 독립 서비스 느낌을 100% 재현한 상태는 아님.
5. main 공통 `Masthead`를 쓰고 있어서 `before_web` 전용 navbar 감각은 줄어듦.
6. `lucide-react`, `framer-motion` 없이 옮긴 부분은 원본보다 정적인 인상이 남음.
7. 결과 패널에서 업로드 원본 미리보기는 현재 빠져 있음.
8. 실제 API polling이 아니라 mock step 진행 기반임.

즉 현재 `/before`는:

- 구조 통합: 완료
- 원본 순차 섹션 구조 재현: 미완료
- 사용자용 문구 정리: 1차 완료
- 원본 감도 재현: 부분 완료
- 실제 API 연결: 미완료

---

## 4. 다음 단계 우선순위

### 1순위: `/before` 구조 재배치

원본 `before_web`의 섹션 순서를 기준으로 `/before/page.tsx`와 `/before/page.module.css`를 먼저 다시 짠다.

- 업로드 섹션은 `UploadPanel` 단독 노출
- 로딩 상태는 업로드 아래 별도 섹션
- 결과 상태는 별도 결과 섹션
- `AccessibilityPanel`은 결과 섹션 오른쪽으로 이동
- 현재 `supportColumn` 제거 또는 결과 단계 전용으로 제한

### 2순위: 구조 수정 후 브라우저 QA

실제로 `/before`를 열고 아래를 확인한다.

- desktop
- mobile width
- loading -> result 전환
- accessibility 선택 상태
- 랜딩 `/`와 `/before` 사이 톤 일관성

### 3순위: 필요 시 시각 polish 추가

브라우저에서 어색한 부분이 발견되면 작은 패치로 정리한다.

- spacing
- typography
- button hierarchy
- empty/loading/result density

### 4순위: API adapter 설계 시작

UI 정리가 끝난 뒤 아래를 결정한다.

- `before_web/api-service`를 직접 연결할지
- main backend 안에 `/api/v1/contract/*` 성격을 새로 만들지
- 초기에는 mock + adapter만 유지할지

---

## 5. 추천 판단

지금 시점에서 가장 먼저 할 일은 **원본 `before_web`와 같은 순차 섹션 구조로 `/before`를 다시 배치하는 것**이다.

이유:

- 현재 문제의 핵심은 간격이나 색보다 섹션 노출 순서다.
- 업로드 단계에서 `AccessibilityPanel`이 보이는 구조는 원본 흐름과 다르다.
- 구조를 바로잡은 뒤에 브라우저 QA를 해야 실제 polish 기준이 생긴다.
