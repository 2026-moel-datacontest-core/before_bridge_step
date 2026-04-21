# Architecture Documentation

Status: scaffold index

## Purpose

`docs/architecture/` is reserved for cloud deployment and expansion architecture. It should explain target infrastructure, deployment topology, model-routing expansion, storage/logging/security services, and operational architecture.

Feature requirements, screen plans, API contracts, and data models belong in `docs/specs/`.

## Current File Classification

| File pattern | Role |
|---|---|
| `architecture_option4_*` | Follow-up Option 4 / self-hosted LLM expansion architecture. These files describe a target cloud deployment path, not the current local MVP. |
| `architecture_project_current.md` / `architecture_project_current.mmd` | Temporary current project reference that summarizes the current repo surfaces. Keep it for now as source material while `docs/specs/` is being filled out. After specs are complete, move/delete only if it becomes duplicate and there is an explicit follow-up task. |

## Planned Cloud Architecture Docs

- `cloud_overview.md`
- `cloud_overview.mmd`
- `cloud_detail.md`
- `cloud_detail.mmd`

## Principles

- Do not turn every feature state into an architecture diagram.
- Keep detailed feature behavior, screens, endpoint schemas, and data contracts in `docs/specs/`.
- Use architecture diagrams for cloud/service boundaries, deployment components, storage/logging/security paths, and future expansion options.
- Keep current MVP references clearly separated from Option 4 / self-hosted LLM target architecture.

