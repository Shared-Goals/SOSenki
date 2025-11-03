# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature implements an MVP flow for seamless Telegram authentication and onboarding via
sosenkibot. When a user opens the Mini App the backend verifies Telegram Web App `initData` and
checks whether the Telegram ID is linked to an existing `SOSenkiUser`. If linked, the Mini App
shows a welcome page. If not linked, the Mini App offers a short request form (max 280 chars)
which is sent to the configured Admin Group Chat. Administrators with the `Administrator` role
can accept or reject requests; on accept the admin selects a role (Administrator, Tenant,
Owner, Investor) and the backend creates a new `SOSenkiUser` with `telegram_id` set. Duplicate
`telegram_id` creation is rejected with a `user_already_exists` error. MVP requires `initData`
authentication (no deep-link fallback in MVP).

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (per constitution)  
**Primary Dependencies**: FastAPI (backend), `python-telegram-bot` (bot), standard HTTP client for Telegram WebApp interactions; frontend is a lightweight static Mini App.  
**Storage**: PostgreSQL (existing project default)  
**Testing**: pytest for backend services; contract tests for API endpoints; integration tests for bot<->backend flows  
**Target Platform**: Linux server for backend + Telegram Web Mini App (mobile/desktop Telegram clients)  
**Project Type**: Web backend + lightweight frontend Mini App  
**Performance Goals**: Low throughput (admin notifications); prioritize reliability and timely delivery (admin notif within 30s per success criteria)  
**Constraints**: Must follow constitution constraints (secrets in env, business logic in services, test-first). Admin actions must be authorized via SOSenki roles.  
**Scale/Scope**: Initial rollout targets normal user volumes; feature is a control-plane flow delivered to small admin group, not a high-rate data path.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The plan was evaluated against the repository constitution (`.specify/memory/constitution.md`). Below
is the post-design pass/fail summary and notes.

**Pass/Fail Summary (post-Phase1)**:

- Spec-First: PASS — a complete spec exists at `/specs/001-seamless-telegram-auth/spec.md` with user scenarios, acceptance criteria and clarifications.
- Business Logic in Services: PASS — plan and data model place business logic in backend services (`backend/app/services/`).
- Test-First: NEEDS ACTION — tests must be authored before implementation; this plan generates test tasks but tests are not yet present.
- Integration & Contract Testing: PARTIAL — an OpenAPI contract (`contracts/openapi.yaml`) has been generated which enables contract testing, but contract tests themselves still need to be implemented.
- Observability & Secrets: PASS — constraints documented; implementation must follow secrets and observability requirements.

**Notes / Required Actions**:

- Before implementation, author unit tests for service logic and contract tests for the endpoints in `contracts/openapi.yaml` (Phase 2 tasks). These are required by the constitution's Test-First gate.
- Ensure CI (or `uv run` tasks) will run the contract and integration tests; add `uv` commands to CI job scripts where appropriate.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: Implement as a Web application using the repository's existing layout:

- backend/app/  — FastAPI app, models, services, API routes for auth, requests, admin actions
- backend/tests/ — unit, integration and contract test harnesses (pytest)
- frontend/src/  — Mini App static site (HTML/JS) served by backend when requested from Telegram
- specs/        — design artifacts (this folder)

This structure follows the repository conventions (business logic in services, tests co-located under backend/tests).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
