# Frontend Implementation Handoff — K-Labor Shield SCN-004 Demo

기준일: `2026-04-16`  
대상: Codex (Next.js frontend 구현 에이전트)  
범위: SCN-004 After flow (4 routes)

---

## 1. Backend Assumptions

### API 계약 — 절대 변경 금지

**POST /api/v1/answer**

```
Request:
  { "query": string, "top_k": number, "ef_search": number }

Response:
  {
    "query": string,
    "answer": string,
    "key_points": string[],
    "cautions": string[],
    "cited_articles": string[],
    "grounded_context_ids": number[],
    "retrieved_chunks": GroundedChunkResult[],
    "retrieval_total": number,
    "model_name": string
  }
```

**POST /api/v1/documents/draft**

```
Request:
  { "case_intake": CaseIntake, "legal_basis": LegalBasisInput }

Response:
  {
    "document_type": DocumentType,
    "title": string,
    "recipient": string,
    "language": string,
    "parties": {
      "worker": string,
      "employer": string,
      "representative_name": string | null,
      "workplace_address": string | null
    },
    "facts": string[],
    "legal_basis": LegalBasisSection[],
    "request": string[],
    "evidence_checklist": string[],
    "missing_fields": string[],
    "cautions": string[],
    "cited_articles": string[],
    "source_context_ids": number[],
    "missing_legal_basis": string[],
    "rendered_text": string
  }
```

### top_k / ef_search 규칙

| 상황 | top_k | ef_search |
|---|---|---|
| SCN demo preset (프리셋 버튼 사용 시) | 10 | 100 |
| 일반 자유 입력 | 5 | 100 |

ef_search는 항상 100. top_k만 분기.

### Backend 실행 주소

- 개발 환경: `http://localhost:8000`
- 환경 변수: `NEXT_PUBLIC_API_BASE_URL`

---

## 2. Product Scope

### 이번 구현 범위 (SCN-004 only)

- `/after` — 상황 입력 및 법령 검색
- `/after/result` — 검색 결과 및 문서 타입 선택
- `/after/intake` — 사건 정보 입력
- `/after/draft` — 문서 초안 결과

**Scope override note**: `frontend/CLAUDE.md`의 route 목록은 이전 MVP 범위 기준이다. SCN-004 After demo 구현에서는 이 문서의 4-route 범위를 최신 기준으로 따른다.

### 지원 문서 타입 (SCN-004)

- `labor_office_wage_complaint` — 고용노동청 임금체불 진정서 초안
- `labor_commission_unfair_dismissal_brief` — 노동위원회 부당해고 구제신청 이유서 초안

### 명시적 제외 범위

- 로그인 / 회원가입 / 사용자 계정
- OCR / 파일 업로드
- Before 화면 (`/before`, `/before/result`)
- Bridge 화면 (`/bridge`)
- SCN-001, SCN-005 문서 타입
- 서버 저장 / PDF 다운로드
- 실제 제출 기능
- Recovery 화면

---

## 3. UX Flow Summary

```
Step 1: /after
  사용자가 상황을 한국어로 자유 진술 입력
  또는 SCN-004 프리셋 버튼 클릭 (자동 입력 + top_k=10)
  "법 조문 찾기" 클릭 → POST /api/v1/answer

Step 2: /after/result
  answer, key_points, cautions, cited_articles 표시
  2개 문서 타입 중 1개 선택 (radio tile)
  "사건 정보 입력하기" 클릭

Step 3: /after/intake
  selected_document_type에 따라 입력 폼 분기
  빈 필드 허용 (missing_fields는 API 응답이 처리)
  "문서 초안 생성하기" 클릭 → POST /api/v1/documents/draft

Step 4: /after/draft
  rendered_text 전체 초안 표시
  missing_fields / cautions / evidence_checklist / cited_articles 표시
  복사 / 인쇄 / 수정 / 다른 문서 타입 / 처음으로 돌아가기 제공
```

**핵심 UX 원칙**: 이 서비스는 "법률 판단 확정"이 아니라 "제출 전 검토용 초안 보조"다. 모든 화면에서 반복 노출.

---

## 4. Screen Specs Summary

### /after — 상황 입력

**목적**: 사용자가 상황을 자유 진술로 입력하고 법 조문 검색을 시작한다.

**주요 컴포넌트**:
- 다크 masthead (height: 48px, bg: #161616)
- 서비스 intro band (Gray 10 surface)
- 메인 입력 textarea (min-height: 160px, 10자 미만 soft warning)
- SCN-004 프리셋 버튼 (ghost 스타일, 클릭 시 고정 텍스트 자동 입력 + is_scn_demo_preset = true)
- "법 조문 찾기" primary CTA (10자 이상일 때 활성)
- 하단 disclaimer band

**상태**:
- `idle_empty`: textarea 비어 있음, CTA disabled
- `editing_short`: 1~9자, soft warning 표시, CTA disabled
- `editing_valid`: 10자 이상, CTA 활성
- `preset_selected`: 프리셋 텍스트 채워짐, CTA 활성
- `answer_loading`: CTA spinner, form locked
- `answer_error`: error notification, retry 가능

**CTA**: "법 조문 찾기 →" (primary, 48px height)

**a11y**: 
- textarea: `aria-label`, `aria-describedby` (soft warning)
- 로딩 중: `aria-busy="true"` on form
- error: `role="alert"`

---

### /after/result — 검색 결과

**목적**: answer 응답을 표시하고 사용자가 문서 타입을 선택한다.

**주요 컴포넌트**:
- masthead (sticky)
- 검색 요약 band (user_statement 첫 100자 표시)
- answer 섹션 (접힘/펼침 가능, 긴 답변)
- key_points 섹션 (bullet list)
- cautions 섹션 (Yellow 10 background)
- cited_articles 섹션 (pill 스타일, 24px radius)
- document_type 선택 섹션 (2개 radio tile)
- "사건 정보 입력하기" CTA (문서 타입 선택 전: `aria-disabled="true"`)

**상태**:
- `result_loaded`: 정상
- `no_answer_state`: answer 없음 (fallback 메시지)
- `document_type_unselected`: CTA aria-disabled
- `document_type_selected`: CTA 활성
- `navigating_to_intake`: 전환 중

**CTA**: "사건 정보 입력하기 →" (primary, 문서 타입 선택 시 활성)

**a11y**:
- document_type tile: `role="radio"` in `role="radiogroup"`, `aria-checked`
- keyboard: 스페이스/엔터로 선택 가능

---

### /after/intake — 사건 정보 입력

**목적**: 선택된 문서 타입에 맞는 사건 정보를 수집한다.

**주요 컴포넌트**:
- masthead (sticky)
- 문서 타입 badge band
- 섹션 A: 당사자 정보 (기본 접힘, "비워두면 [확인 필요]로 표시됩니다")
- 섹션 B: 근무 기간 및 해고 정보
- 섹션 C: 미지급 금품 (wage_complaint 타입만)
- 섹션 D: 증거 목록
- sticky action bar (bottom: 0, height: 80px, "문서 초안 생성하기 →")

**document_type별 필드 분기**:

`labor_office_wage_complaint`:
- unpaid_wage_amount, unpaid_severance_amount
- days_since_separation_over_14
- unpaid_period_start, unpaid_period_end

`labor_commission_unfair_dismissal_brief`:
- dismissal_notice_date, dismissal_effective_date
- reinstatement_requested, monetary_compensation_requested
- employee_count_over_5

**공통 conditional field**:
- notice_method === "written" → written_notice_received 체크박스 노출
- employee_count_over_5 === false → inline caution 노출

**빈 필드 정책**: 블로킹 없음. 모든 필드 optional. 빈 채로 제출 가능.

**상태**:
- `intake_loaded`: 정상
- `editing`: 입력 중
- `draft_submitting`: CTA spinner, form opacity 0.5 + pointer-events none
- `draft_error`: error notification in sticky bar

**CTA**: "문서 초안 생성하기 →" (primary, 항상 활성)

**a11y**:
- 섹션별 `fieldset` + `legend`
- 조건부 필드: `aria-expanded` on toggle
- 로딩 중: `aria-busy="true"`, form `aria-disabled`

---

### /after/draft — 문서 초안 결과

**목적**: 생성된 문서 초안을 검토하고 부족한 정보와 증거 체크리스트를 확인한다.

**주요 컴포넌트**:
- masthead (sticky)
- draft header band: 제목, document_type badge, recipient, disclaimer
- disclaimer band: "이 문서는 제출 전 검토용 초안입니다." (Yellow 10 bg)
- document preview: rendered_text를 `<article>` 안에 IBM Plex Mono로 표시 (white surface)
- "복사" 버튼 (article 우상단)
- missing_fields panel (Yellow Amber bg, 빈 필드 목록)
- cautions panel (static note, list semantics)
- evidence_checklist panel (체크박스, 로컬 상태만, 저장 안 됨)
- legal basis panel (cited_articles pills, source_context_ids는 debug disclosure 안에 숨김)
- missing_legal_basis panel (있을 때만 표시)
- action bar: primary "다른 문서 타입으로 생성하기", ghost "사건 정보 수정하기", ghost "처음으로 돌아가기"

**상태**:
- `draft_loaded`: 정상
- `direct_url_access`: draft_response 없음 → `/after`로 redirect
- `rendered_text_empty`: "초안 본문을 생성하지 못했습니다" fallback
- `missing_fields_empty`: "추가로 표시된 확인 항목이 없습니다" 빈 상태
- `copy_pending` / `copy_success` / `copy_error`: 복사 상태
- `print_requested`: 브라우저 print 호출

**a11y**:
- rendered_text: `<article role="document">`
- copy success: `aria-live="polite"`
- missing_fields / cautions / evidence_checklist: `<ul>` semantics
- evidence_checklist: `<fieldset>` + `<legend>`
- print CSS: disclaimer 포함

---

## 5. Interaction Spec Summary

### State Machine (각 화면별 핵심 상태)

```
/after:
  idle_empty → editing_short (1자) → editing_valid (10자) → answer_loading → [/after/result | answer_error]
  preset_selected → answer_loading (top_k=10)

/after/result:
  result_loaded → document_type_selected → navigating_to_intake → [/after/intake]
  no_answer_state (answer 없음)

/after/intake:
  intake_loaded → editing → draft_submitting → [/after/draft | draft_error]

/after/draft:
  draft_loaded → [copy_pending → copy_success | print_requested]
  direct_url_access → redirect /after
```

### Screen Transitions

| From | To | Trigger | Focus Target |
|---|---|---|---|
| /after | /after/result | answer 성공 | `<h1>` |
| /after/result | /after/intake | CTA 클릭 | `<h1>` |
| /after/intake | /after/draft | draft 성공 | `<h1>` |
| /after/draft | /after/intake | "수정하기" 클릭 | intake form `<h1>` |
| /after/draft | /after/intake?type=other | "다른 문서 타입" 클릭 | document_type selector |
| any → /after | "처음으로" 클릭 | state reset | textarea |

### Route Guards

- `/after/result` 진입 시 `answer_response`가 없으면 → `/after`로 redirect
- `/after/intake` 진입 시 `answer_response`가 없으면 → `/after`; `selected_document_type`이 없으면 → `/after/result`
- `/after/draft` 진입 시 `draft_response`가 없으면 → `/after`로 redirect

### API Flow

**POST /api/v1/answer**:
1. FlowContext에 user_statement, is_scn_demo_preset 저장
2. top_k 결정: `is_scn_demo_preset ? 10 : 5`
3. payload: `{ query: user_statement, top_k, ef_search: 100 }`
4. 성공: `answer_response`를 FlowContext에 저장한다. 개인정보 최소 수집 원칙상 Phase 1에서는 sessionStorage에 원문 진술이나 응답을 저장하지 않는다.
5. 실패 503: "잠시 후 다시 시도해주세요" + retry 버튼
6. 실패 4xx: "입력 내용을 확인해주세요" + 이전으로 돌아가기

**AnswerResponse → LegalBasisInput 변환**:
```
answer_response.query       → legal_basis.answer_query
answer_response.answer      → legal_basis.answer
answer_response.key_points  → legal_basis.key_points
answer_response.cautions    → legal_basis.cautions
answer_response.cited_articles → legal_basis.cited_articles
answer_response.grounded_context_ids → legal_basis.source_context_ids
answer_response.retrieved_chunks → legal_basis.retrieved_chunks
```

**POST /api/v1/documents/draft**:
1. payload: `{ case_intake: CaseIntake, legal_basis: LegalBasisInput }`
2. 성공: `draft_response`를 FlowContext에 저장 (sessionStorage 저장 안 함)
3. 실패 422: "입력 값에 오류가 있습니다" + 필드 확인 안내
4. 실패 500: "초안 생성에 실패했습니다. 다시 시도해주세요" + retry

### Error Messages (사용자 노출 문구)

| 상황 | 메시지 | Retry |
|---|---|---|
| /api/v1/answer 503 | "서버가 일시적으로 응답하지 않습니다. 잠시 후 다시 시도해주세요." | O |
| /api/v1/answer 4xx | "입력 내용을 확인한 후 다시 시도해주세요." | O |
| /api/v1/documents/draft 422 | "입력 값에 오류가 있습니다. 내용을 확인해주세요." | O |
| /api/v1/documents/draft 500 | "문서 초안 생성에 실패했습니다. 다시 시도해주세요." | O |
| 네트워크 오류 | "연결을 확인하고 다시 시도해주세요." | O |
| route guard redirect | 화면 전환 없이 조용히 redirect | — |

---

## 6. Design System Tokens

### CSS Variables (전체 목록)

```css
:root {
  /* Background & Surface */
  --kl-bg: #ffffff;
  --kl-surface-01: #f4f4f4;
  --kl-surface-02: #e0e0e0;
  --kl-surface-warning: #fcf4d6;
  --kl-surface-info: #edf5ff;
  --kl-surface-success: #defbe6;
  --kl-surface-danger: #fff1f1;

  /* Text */
  --kl-text-primary: #161616;
  --kl-text-secondary: #525252;
  --kl-text-muted: #6f6f6f;
  --kl-text-placeholder: #8d8d8d;
  --kl-text-on-dark: #f4f4f4;
  --kl-text-on-primary: #ffffff;
  --kl-text-warning: #b28600;
  --kl-text-danger: #da1e28;
  --kl-text-success: #24a148;

  /* Interactive */
  --kl-primary: #0f62fe;
  --kl-primary-hover: #0353e9;
  --kl-primary-active: #002d9c;
  --kl-primary-light: #edf5ff;

  /* Status */
  --kl-warning: #f1c21b;
  --kl-danger: #da1e28;
  --kl-success: #24a148;

  /* Border */
  --kl-border: #c6c6c6;
  --kl-border-subtle: #e0e0e0;
  --kl-focus: #0f62fe;

  /* Masthead */
  --kl-masthead-bg: #161616;
  --kl-masthead-height: 48px;

  /* Typography */
  --kl-font-sans: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;
  --kl-font-mono: 'IBM Plex Mono', Menlo, 'Courier New', monospace;

  /* Font sizes */
  --kl-text-display: 2.625rem;    /* 42px, weight 300 */
  --kl-text-h1: 2rem;             /* 32px, weight 400 */
  --kl-text-h2: 1.5rem;           /* 24px, weight 400 */
  --kl-text-h3: 1.25rem;          /* 20px, weight 600 */
  --kl-text-body-lg: 1rem;        /* 16px, weight 400 */
  --kl-text-body: 0.875rem;       /* 14px, weight 400 */
  --kl-text-caption: 0.75rem;     /* 12px, weight 400 */
  --kl-text-mono: 0.875rem;       /* 14px */
  --kl-text-mono-sm: 0.75rem;     /* 12px */

  /* Line heights */
  --kl-lh-display: 1.19;
  --kl-lh-heading: 1.25;
  --kl-lh-body: 1.5;
  --kl-lh-body-short: 1.29;
  --kl-lh-caption: 1.33;
  --kl-lh-document: 1.8;

  /* Letter spacing */
  --kl-ls-body: 0.16px;    /* 14px text */
  --kl-ls-caption: 0.32px; /* 12px text */

  /* Spacing (8px grid) */
  --kl-space-1: 4px;
  --kl-space-2: 8px;
  --kl-space-3: 12px;
  --kl-space-4: 16px;
  --kl-space-6: 24px;
  --kl-space-8: 32px;
  --kl-space-12: 48px;
  --kl-space-16: 64px;
  --kl-space-24: 96px;

  /* Layout */
  --kl-max-width: 1312px;
  --kl-content-width: 800px;
  --kl-form-width: 640px;
  --kl-document-width: 720px;
  --kl-margin-desktop: 64px;
  --kl-margin-mobile: 16px;

  /* Interactive sizes */
  --kl-interactive-height: 48px;
  --kl-sticky-bar-height: 80px;

  /* Radius */
  --kl-radius-control: 0px;
  --kl-radius-card: 0px;
  --kl-radius-pill: 24px;

  /* Border styles */
  --kl-border-default: 1px solid var(--kl-border);
  --kl-border-subtle-line: 1px solid var(--kl-border-subtle);
  --kl-focus-ring: 2px solid var(--kl-focus);

  /* Z-index */
  --kl-z-masthead: 100;
  --kl-z-sticky-bar: 90;
  --kl-z-overlay: 200;

  /* Motion */
  --kl-duration-short: 100ms;
  --kl-duration-base: 200ms;
  --kl-duration-medium: 250ms;
  --kl-ease-enter: ease-out;
  --kl-ease-exit: ease-in;
}

@media (prefers-reduced-motion: reduce) {
  :root {
    --kl-duration-short: 0ms;
    --kl-duration-base: 0ms;
    --kl-duration-medium: 0ms;
  }
}
```

### 핵심 Component Rules

**Masthead**
- height: 48px, bg: #161616, color: white
- sticky top: 0, z-index: var(--kl-z-masthead)
- 서비스명 + 간단 nav

**Button — Primary**
- bg: var(--kl-primary), color: white
- height: 48px, padding: 0 24px
- radius: 0px
- hover: var(--kl-primary-hover)
- loading: inline spinner (16px) + 텍스트 "처리 중..." + pointer-events none
- disabled 시 `aria-disabled="true"` 사용 (실제 form disabled보다 선호)

**Button — Ghost**
- bg: transparent, color: var(--kl-primary)
- border: none
- hover: var(--kl-primary-light) bg

**Button — Tertiary**
- bg: transparent, color: var(--kl-primary)
- border: 1px solid var(--kl-primary)

**Textarea / Text input**
- border: none
- border-bottom: 2px solid var(--kl-border) (Carbon form pattern)
- bg: var(--kl-surface-01)
- focus: border-bottom 2px solid var(--kl-focus) + outline: none
- height: auto (textarea), 48px (input)
- padding: 12px 16px
- font: var(--kl-font-sans), 16px

**Select**
- 동일하게 bottom-border 스타일
- chevron icon right

**Radio tile (document type 선택용)**
- display: block, padding: 16px
- border: 2px solid var(--kl-border-subtle)
- selected: border: 2px solid var(--kl-primary), bg: var(--kl-primary-light)
- hover: bg: var(--kl-surface-01)
- role="radio", aria-checked
- keyboard: 스페이스/엔터로 선택

**Checkbox**
- 16x16px 체크박스
- checked: bg var(--kl-primary), checkmark white
- border: 1px solid var(--kl-border)
- focus: var(--kl-focus-ring)

**Citation pill**
- bg: var(--kl-surface-01), border: 1px solid var(--kl-border)
- border-radius: var(--kl-radius-pill) (24px — 유일하게 radius 허용)
- padding: 4px 12px
- font: var(--kl-font-mono), 12px
- display: inline-flex, align-items: center

**Disclaimer banner**
- bg: var(--kl-surface-warning) (#fcf4d6)
- border-left: 4px solid var(--kl-warning)
- padding: 16px
- text: var(--kl-text-warning), 14px

**Notification (warning/error/success/info)**
- warning: bg #fcf4d6, border-left 4px #f1c21b
- error: bg #fff1f1, border-left 4px #da1e28
- success: bg #defbe6, border-left 4px #24a148
- info: bg #edf5ff, border-left 4px #0f62fe
- 각각 icon + message + optional retry CTA

**Sticky action bar**
- position: sticky, bottom: 0
- height: 80px, bg: white
- border-top: 1px solid var(--kl-border)
- z-index: var(--kl-z-sticky-bar)
- padding: 0 64px (desktop), 0 16px (mobile)
- CTA 오른쪽 정렬

**Document paper (rendered_text)**
- bg: white, border: 1px solid var(--kl-border)
- padding: 48px (desktop), 24px (mobile)
- max-width: var(--kl-document-width)
- font: var(--kl-font-sans), 16px
- line-height: var(--kl-lh-document) (1.8)
- white-space: pre-wrap

**Missing fields panel**
- bg: var(--kl-surface-warning)
- border-left: 4px solid var(--kl-warning)

**Progress bar (masthead)**
- position absolute bottom of masthead
- height: 4px, bg: var(--kl-primary)
- indeterminate animation (translateX + scaleX), exact progress 표시 안 함
- display: none when not loading

**Spinner**
- 16px for inline (button), 32px for section-level
- color: currentColor (button) or var(--kl-primary) (section)
- `role="status"`, `aria-label="로딩 중"`

---

## 7. Tech Stack

| 항목 | 결정 |
|---|---|
| Framework | Next.js 14+ (App Router) |
| Language | TypeScript (strict) |
| Styling | CSS Modules + CSS Variables (`--kl-*` prefix) |
| UI Library | 없음 (Carbon React 설치 금지) |
| State | React Context + useReducer (FlowContext) |
| Font | Google Fonts 또는 직접 import (IBM Plex Sans, IBM Plex Mono) |
| API | native fetch (AbortController 포함) |
| 테스트 | 없음 (demo 안정성 중심, 복잡한 test setup 금지) |

**CSS Modules 선택 이유**: Next.js에 기본 내장, scoped className, CSS Variables와 완벽 호환, Tailwind 없이 Carbon 토큰 직접 사용 가능, 번들 사이즈 최소.

---

## 8. File Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # root layout (masthead, font, global CSS)
│   │   ├── globals.css             # :root CSS variables, reset
│   │   ├── page.tsx                # / (랜딩 또는 /after로 redirect)
│   │   └── after/
│   │       ├── page.tsx            # /after
│   │       ├── result/
│   │       │   └── page.tsx        # /after/result
│   │       ├── intake/
│   │       │   └── page.tsx        # /after/intake
│   │       └── draft/
│   │           └── page.tsx        # /after/draft
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Masthead.tsx
│   │   │   ├── Masthead.module.css
│   │   │   ├── StickyActionBar.tsx
│   │   │   └── StickyActionBar.module.css
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.module.css
│   │   │   ├── CitationPill.tsx
│   │   │   ├── CitationPill.module.css
│   │   │   ├── DisclaimerBanner.tsx
│   │   │   ├── Notification.tsx
│   │   │   ├── Spinner.tsx
│   │   │   └── SkipLink.tsx
│   │   ├── after/
│   │   │   ├── StatementInput.tsx
│   │   │   ├── PresetButton.tsx
│   │   │   └── AnswerResultSection.tsx
│   │   ├── result/
│   │   │   ├── DocumentTypeTile.tsx
│   │   │   └── DocumentTypeSelector.tsx
│   │   ├── intake/
│   │   │   ├── WageComplaintForm.tsx
│   │   │   ├── UnfairDismissalForm.tsx
│   │   │   └── EvidenceSection.tsx
│   │   └── draft/
│   │       ├── DocumentPreview.tsx
│   │       ├── MissingFieldsPanel.tsx
│   │       ├── CautionsPanel.tsx
│   │       ├── EvidenceChecklist.tsx
│   │       └── LegalBasisPanel.tsx
│   ├── context/
│   │   └── FlowContext.tsx         # FlowContext + useReducer + Provider
│   ├── lib/
│   │   ├── api.ts                  # fetchAnswer, fetchDraft, ApiError
│   │   └── session.ts              # optional Phase 3 only, privacy-safe helpers
│   └── types/
│       ├── api.ts                  # AnswerRequest, AnswerResponse, etc.
│       └── flow.ts                 # KLaborShieldFlowState, FlowAction
├── public/
│   └── fonts/                      # IBM Plex 폰트 파일 (선택)
├── next.config.js
├── tsconfig.json
└── package.json
```

---

## 9. TypeScript Types

### types/api.ts

```typescript
export type DocumentType =
  | 'labor_office_wage_complaint'
  | 'labor_commission_unfair_dismissal_brief';

export type EvidenceStatus = 'available' | 'needs_collection' | 'unknown';
export type EvidenceUiStatus = 'not_selected' | EvidenceStatus;

export type NoticeMethod =
  | 'written' | 'kakaotalk' | 'sms' | 'email' | 'verbal' | 'phone' | 'unknown';

export interface AnswerRequest {
  query: string;
  top_k: number;
  ef_search: number;
}

export interface GroundedChunkResult {
  context_id: number;
  chunk_id: string;
  citation_label: string;
  law_name: string;
  article_no: string;
  article_title: string;
  paragraph_no: number | null;
  content: string;
  similarity: number;
  tier: number;
  structure_path: string | null;
}

export interface AnswerResponse {
  query: string;
  answer: string;
  key_points: string[];
  cautions: string[];
  cited_articles: string[];
  grounded_context_ids: number[];
  retrieved_chunks: GroundedChunkResult[];
  retrieval_total: number;
  model_name: string;
}

export interface LegalBasisInput {
  answer_query: string;
  answer: string;
  key_points: string[];
  cautions: string[];
  cited_articles: string[];
  source_context_ids: number[];
  retrieved_chunks: GroundedChunkResult[];
}

export interface WorkerInfo {
  name_or_placeholder?: string | null;
  nationality?: string | null;
  preferred_language?: 'ko' | 'en' | null;
}

export interface EmployerInfo {
  company_name_or_placeholder?: string | null;
  representative_name?: string | null;
  workplace_address?: string | null;
  employee_count?: number | null;
  employee_count_over_5?: boolean | null;
  workplace_jurisdiction?: string | null;
}

export interface EmploymentInfo {
  start_date?: string | null;
  last_work_date?: string | null;
  job_title?: string | null;
  wage_terms?: string | null;
  wage_type?: WageType | null;
  employment_contract_exists?: boolean | null;
  wage_payment_day?: number | null;
  continuous_service_over_1_year?: boolean | null;
}

export interface DismissalInfo {
  dismissal_notice_date?: string | null;
  dismissal_effective_date?: string | null;
  notice_method?: NoticeMethod | null;
  written_notice_received?: boolean | null;
  dismissal_reason_provided?: boolean | null;
  dismissal_reason?: string | null;
  advance_notice_30_days?: boolean | null;
  reinstatement_requested?: boolean | null;
  monetary_compensation_requested?: boolean | null;
  opportunity_to_explain?: boolean | null;
  prior_disciplinary_action?: boolean | null;
}

export interface UnpaidWageInfo {
  final_wage_paid?: boolean;
  unpaid_wage_amount?: number | null;
  severance_paid?: boolean;
  unpaid_severance_amount?: number | null;
  days_since_separation_over_14?: boolean;
  unpaid_period_start?: string | null;
  unpaid_period_end?: string | null;
}

export interface EvidenceItem {
  type: EvidenceType;
  description: string;
  status: EvidenceStatus;
}

export type WageType =
  | 'hourly'
  | 'daily'
  | 'weekly'
  | 'monthly'
  | 'annual'
  | 'piece_rate'
  | 'other'
  | 'unknown';

export type EvidenceType =
  | 'message'
  | 'sms'
  | 'email'
  | 'paystub'
  | 'bank_statement'
  | 'employment_contract'
  | 'attendance_record'
  | 'work_schedule'
  | 'recording'
  | 'photo'
  | 'memo';

export type Claim =
  | 'unfair_dismissal'
  | 'no_written_dismissal_notice'
  | 'no_advance_dismissal_notice'
  | 'unpaid_final_wages'
  | 'unpaid_severance_pay'
  | 'delay_interest_possible';

export interface CaseIntake {
  scenario_id: 'SCN-001' | 'SCN-004' | 'SCN-005';
  document_type: DocumentType;
  language: 'ko' | 'en';
  worker_info: WorkerInfo;
  employer_info: EmployerInfo;
  employment_info: EmploymentInfo;
  dismissal_info?: DismissalInfo;
  unpaid_wage_info?: UnpaidWageInfo;
  incident_timeline?: Array<{ date: string | null; event: string; evidence_refs?: string[] }>;
  claims?: Claim[];
  evidence_items?: EvidenceItem[];
  requested_actions?: string[];
  intake_notes?: string | null;
}

export interface DocumentDraftRequest {
  case_intake: CaseIntake;
  legal_basis: LegalBasisInput;
}

export interface LegalBasisSection {
  citation_label: string;
  summary: string;
  source_context_ids: number[];
}

export interface DocumentDraftResponse {
  document_type: DocumentType;
  title: string;
  recipient: string;
  language: string;
  parties: {
    worker: string;
    employer: string;
    representative_name?: string | null;
    workplace_address?: string | null;
  };
  facts: string[];
  legal_basis: LegalBasisSection[];
  request: string[];
  evidence_checklist: string[];
  missing_fields: string[];
  cautions: string[];
  cited_articles: string[];
  source_context_ids: number[];
  missing_legal_basis: string[];
  rendered_text: string;
}

export interface ApiError {
  status: number;
  message: string;
  retryable: boolean;
}
```

### types/flow.ts

```typescript
import type {
  AnswerResponse,
  DocumentType,
  LegalBasisInput,
  CaseIntake,
  DocumentDraftResponse,
  EvidenceUiStatus,
} from './api';

export interface KLaborShieldFlowState {
  user_statement: string;
  is_scn_demo_preset: boolean;
  answer_response: AnswerResponse | null;
  selected_document_type: DocumentType | null;
  legal_basis: LegalBasisInput | null;
  case_intake: Partial<CaseIntake> | null;
  evidence_status_map: Record<string, EvidenceUiStatus>;
  draft_response: DocumentDraftResponse | null;
}

export type FlowAction =
  | { type: 'SET_STATEMENT'; payload: { statement: string; is_preset: boolean } }
  | { type: 'SET_ANSWER'; payload: AnswerResponse }
  | { type: 'SET_DOCUMENT_TYPE'; payload: DocumentType }
  | { type: 'SET_CASE_INTAKE'; payload: Partial<CaseIntake> }
  | { type: 'SET_EVIDENCE_STATUS'; payload: { key: string; status: EvidenceUiStatus } }
  | { type: 'SET_DRAFT'; payload: DocumentDraftResponse }
  | { type: 'RESET' };
```

---

## 10. API Client Spec

### lib/api.ts

```typescript
// fetchAnswer(request: AnswerRequest): Promise<AnswerResponse>
// - POST NEXT_PUBLIC_API_BASE_URL/api/v1/answer
// - timeout: 30000ms (AbortController)
// - 503 → ApiError { status: 503, message: "...", retryable: true }
// - network → ApiError { status: 0, message: "...", retryable: true }
// - 4xx → ApiError { status, message: "...", retryable: true }

// fetchDraft(request: DocumentDraftRequest): Promise<DocumentDraftResponse>
// - POST NEXT_PUBLIC_API_BASE_URL/api/v1/documents/draft
// - timeout: 60000ms (LLM 응답이 느릴 수 있음)
// - 422 → ApiError { status: 422, message: "...", retryable: true }
// - 500 → ApiError { status: 500, message: "...", retryable: true }

// buildLegalBasis(response: AnswerResponse, query: string): LegalBasisInput
// - AnswerResponse → LegalBasisInput 변환 pure function
// - answer_query = query
// - source_context_ids = grounded_context_ids
```

### lib/session.ts

```typescript
// Phase 1에서는 sessionStorage를 사용하지 않는다.
// 이유: user_statement와 AnswerResponse.query에는 개인 진술이 포함될 수 있고,
// 화면 copy가 "입력 내용은 저장되지 않습니다"라고 안내하기 때문이다.
//
// 선택적 Phase 3에서 새로고침 복구가 꼭 필요해질 때만 아래처럼 제한한다:
// saveNonSensitiveFlowHint({ selected_document_type, is_scn_demo_preset }): void
// loadNonSensitiveFlowHint(): { selected_document_type?: DocumentType; is_scn_demo_preset?: boolean } | null
// clearSession(): void
//
// 저장 금지: user_statement, answer_response, case_intake, draft_response
```

---

## 11. Implementation Phases

### Phase 1: Scaffold + 4 Screen 구현 (필수)

**목표**: SCN-004 전체 flow가 실제 API와 연동되어 동작하는 상태

**순서**:
1. Next.js 14 프로젝트 scaffold (npx create-next-app, TypeScript, App Router, CSS Modules)
2. `globals.css`에 CSS Variables 전체 추가, IBM Plex Sans/Mono 폰트 로드
3. `types/api.ts`, `types/flow.ts` 작성
4. `context/FlowContext.tsx` — FlowContext + useReducer + Provider
5. `lib/api.ts` — fetchAnswer, fetchDraft, buildLegalBasis
6. `lib/session.ts` — Phase 1에서는 생략 가능. 추가한다면 privacy-safe no-op 또는 selected_document_type 같은 비민감 hint만 다룬다.
7. `components/layout/Masthead.tsx` + `StickyActionBar.tsx`
8. `components/ui/` — Button, CitationPill, DisclaimerBanner, Notification, Spinner
9. `/after` page — textarea + preset + CTA + answer_loading state
10. `/after/result` page — answer 표시 + document type 선택
11. `/after/intake` page — WageComplaintForm + UnfairDismissalForm + EvidenceSection
12. `/after/draft` page — DocumentPreview + MissingFieldsPanel + CautionsPanel + EvidenceChecklist + LegalBasisPanel

### Phase 2: Error / Loading / a11y (필수)

**목표**: demo 시연 중 에러 상황에서도 안정적으로 동작

1. 모든 API error 상태 UI 연결
2. route guard 구현 (answer_response 없으면 /after로)
3. 로딩 중 masthead progress bar
4. focus management (route 전환 후 h1 focus)
5. aria-live, aria-busy, aria-disabled 전체 점검
6. skip link (`/components/ui/SkipLink.tsx`)
7. 모바일 반응형 (640px 이하 single column, sticky bar full width)

### Phase 3: Polish (선택, 시간 여유 시)

1. rendered_text 복사 버튼 (Clipboard API)
2. 인쇄 버튼 (window.print, print CSS에 disclaimer 포함)
3. evidence_checklist 로컬 체크 상태 동기화
4. sessionStorage backup/restore는 후순위이며, raw user_statement / answer_response / case_intake / draft_response는 저장하지 않는다.
5. transition animation (collapse, page entry)

---

## 12. Validation Plan

### npm 명령어

```bash
cd frontend
npm install
npm run build    # TypeScript 오류 0이어야 함
npm run dev      # 개발 서버 실행
```

### 수동 smoke test

1. `http://localhost:3000/after` 접근
2. 10자 이상 입력 → CTA 활성 확인
3. "법 조문 찾기" → 로딩 → `/after/result` 이동
4. document type 선택 → "사건 정보 입력하기" 활성
5. intake form 빈 채로 "문서 초안 생성하기" → `/after/draft` 이동
6. rendered_text 표시 확인
7. "처음으로 돌아가기" → state reset 확인
8. `/after/draft` 직접 접근 → `/after`로 redirect 확인

### Backend 연동 확인

```bash
# backend가 실행 중이어야 함
conda activate law_main_road
uvicorn backend.main:app --reload
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 13. Do Not List

- backend 코드 수정 금지 (`backend/` 파일 전체)
- `/api/v1/answer`, `/api/v1/documents/draft` contract 변경 금지
- 로그인 / 회원가입 / 사용자 계정 기능 추가 금지
- OCR / 파일 업로드 기능 추가 금지
- user_statement, answer_response, case_intake, draft_response를 sessionStorage / localStorage에 저장 금지
- `@carbon/react` 또는 다른 외부 UI 라이브러리 설치 금지
- Tailwind CSS 설치 금지
- SCN-001, SCN-005 문서 타입 구현 금지 (Phase 1 범위 아님)
- `/before`, `/bridge` 화면 구현 금지 (Phase 1 범위 아님)
- 법률 판단 확정 문구 하드코딩 금지 ("위법 확정", "반드시 승소" 등)
- cited_articles 없는 법률 답변을 결과 화면에 표시 금지
- 검색되지 않은 조문 인용 금지
- `data/legalize-kr/` 수정 금지

---

## 14. Final Codex Prompt

```
docs/planning/14_frontend_implementation_handoff.md를 읽고 Phase 1 frontend 구현을 시작해줘.
```

이 문서 한 장이 모든 context다. 추가 파일을 읽어야 한다면:
- `DESIGN.md` — 시각 스타일 상세
- `docs/planning/13_document_draft_plan.md` — CaseIntake schema 상세
- `backend/app/schemas/document_draft.py` — Pydantic schema 확인
- `frontend/CLAUDE.md` — frontend 규칙 확인

**구현 시작점**: `frontend/` 디렉토리에서 `npm run dev`가 동작하는 Next.js scaffold를 먼저 만들고, 위 Section 8의 파일 구조대로 진행한다.

---

*이 문서는 2026-04-16 기준 K-Labor Shield SCN-004 frontend demo를 위한 구현 handoff 문서다. backend 코드 및 API contract는 변경하지 않는다.*
