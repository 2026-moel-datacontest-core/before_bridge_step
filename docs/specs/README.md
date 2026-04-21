# Specs Documentation

Status: current specs index

## Purpose

`docs/specs/` is the home for feature-level requirements, screen plans, API specs, and data model documents. It describes product behavior and implementation contracts for the current Before/Begin and After surfaces, while `docs/architecture/` and architecture-focused planning docs stay focused on cloud deployment and expansion architecture.

Current state:

- `before_begin/` detailed specs are completed/reviewed against the current `z_before_begin/web` implementation.
- `after/` detailed specs are completed/reviewed against the current main `frontend/` + `backend/` implementation.
- `integrated/` documents are candidate/placeholder documents only. They are not a final source of truth until team merge is complete and the real integrated contracts are confirmed.

## Scope Split

| Folder | Current status | Scope |
|---|---|---|
| `before_begin/` | Current implementation reference, detailed spec completed/reviewed | `z_before_begin/web` contract upload and review app: upload, OCR, contract review, explanation, artifact output, accessibility recommendations. |
| `after/` | Current implementation reference, detailed spec completed/reviewed | Main `frontend/` + `backend/` SCN-004 After/RAG app: legal question, retrieval, grounded answer, intake, deterministic document draft. |
| `integrated/` | Candidate/placeholder only, not final source of truth before team merge | Future unified service that may connect Before/Begin, Bridge, and After after actual team integration contracts are known. |

## Document Types

| File | Role |
|---|---|
| `requirements.md` | 요구정의서: functional scope, user goals, guardrails, privacy/model boundary notes, acceptance criteria, and requirement TODOs. |
| `screen_plan.md` | 화면 기획서: route/screen flow, user interaction states, major components, and screen-planning TODOs. |
| `api_spec.md` | API 명세서: endpoint inventory, request/response contracts, status/error behavior, integration notes, and schema TODOs. |
| `data_model.md` | 데이터 모델/ERD 또는 artifact/data-flow model: runtime data, artifacts, state, corpus/assets, storage boundaries, and ERD/data contract TODOs. |

## Writing And Review Order

1. Use `before_begin/*` as the current code-based spec set for `z_before_begin/web`.
2. Use `after/*` as the current code-based spec set for main `frontend/` + `backend`.
3. Keep `integrated/*` as candidate/placeholder material until team merge is complete.
4. After team merge, rewrite/finalize the integrated requirements, screen plan, API spec, and data model from the actual unified frontend/backend contracts.
5. Keep cloud deployment and expansion architecture in `docs/architecture/` or architecture-focused planning docs, not in feature specs unless a feature contract directly depends on it.

## Boundary Notes

- Privacy and Vertex AI boundaries must be explained per feature area, not as one global project claim.
- Before/Begin contract upload/review may include personal or workplace information and currently can use Vertex AI OCR/LLM paths.
- After live retrieve/answer paths can use Vertex query embedding and Gemini answer generation.
- The After document draft endpoint is a no-Vertex deterministic path and uses only request `case_intake` and `legal_basis`.
- Do not claim that all project personal data avoids Vertex AI.
- Keep API contracts aligned with code. Do not extend or reinterpret an endpoint contract in docs without backend/schema review.
