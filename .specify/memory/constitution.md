<!--
Sync Impact Report

Version change: 0.1.0 → 0.2.0

Modified principles:
- (no principle renames) — clarified Development Workflow & Quality Gates to require a single maintainer review (removed any requirement for two reviewers)

Added sections:
- Preferred Telegram bot library: python-telegram-bot (constraints)
- Preferred local package manager/execution: uv (development workflow)

Removed sections:
- Explicit requirement for two-maintainer PR approvals (relaxed to single-maintainer review)

Templates requiring updates:
- .specify/templates/plan-template.md: ✅ reviewed — no change required
- .specify/templates/spec-template.md: ✅ reviewed — no change required
- .specify/templates/tasks-template.md: ✅ reviewed — no change required
- .specify/templates/checklist-template.md: ✅ reviewed — no change required
- .specify/templates/agent-file-template.md: ✅ reviewed — no change required

Follow-up TODOs:
- Ensure CI / CODEOWNERS (if present) reflect single-reviewer policy where applicable.
-->

# SOSenki Constitution

## Core Principles

### Spec-First Development

All features MUST be specified in `/specs/` before implementation work begins. A valid spec
MUST include user scenarios, measurable success criteria, and an explicit test plan. Rationale:
spec-first reduces rework, ensures testability, and makes acceptance criteria objective.

### Business Logic in Services (Separation of Concerns)

All non-trivial business logic MUST live in `backend/app/services/` (or equivalent service modules).
Route handlers/HTTP controllers MUST remain thin and delegate to services. Data models belong in
`backend/app/models/` and validation/serialization belongs in `backend/app/schemas/`. Rationale:
this keeps logic testable and portable across interfaces (CLI, HTTP, background jobs).

### Test-First (TDD, NON-NEGOTIABLE)

Tests MUST be authored before implementation for all new behaviors (unit, contract, integration as
applicable). Tests MUST fail initially, then be made to pass (Red-Green-Refactor). Minimum test
requirements: unit tests for services, contract tests for public API changes, and integration tests for
cross-component behavior. Rationale: prevents regressions and documents expected behavior.

### Integration & Contract Testing

Any change that affects inter-service contracts, database schemas, or public APIs MUST include
contract tests and an integration test matrix covering critical workflows. Backwards-incompatible
contract changes MUST follow the versioning policy in Governance and include migration plans.

### Observability, Versioning & Simplicity

Services MUST emit structured logs and capture errors with context. Metrics and basic tracing
MUST be present for production services. Versioning for public APIs and contracts MUST follow
semantic versioning (MAJOR.MINOR.PATCH):

- MAJOR: incompatible breaking changes to public contracts or governance principles
- MINOR: new features that are backwards-compatible
- PATCH: clarifications, wording, docs, and non-semantic fixes
Design choices MUST favor simplicity and YAGNI; avoid premature generalization.

## Constraints & Security Requirements

- Primary stack: Python 3.11+, FastAPI for HTTP services, SQLAlchemy + PostgreSQL for persistence.
- Preferred Telegram bot library: `python-telegram-bot` for bot implementation where applicable.
- Preferred local package manager and task runner: `uv` (use `uv run <task>` for local test/commands).
- Secrets MUST NOT be hard-coded. Use environment variables and `.env` files locally. Production
  credentials MUST be stored in a secure secrets store.
- Any external integration (e.g., Telegram Bot API, Yandex Cloud) MUST have documented scopes,
  retry/backoff strategies, and simulated tests where possible.

## Development Workflow & Quality Gates

- Spec-first: every feature folder in `/specs/` is required before implementation branches are
  opened.
- Pull requests MUST reference a spec and include the test plan. PRs MUST be reviewed and
  approved by at least one repository maintainer and pass CI (lint, tests, spec-kit checks)
  before merge. (Policy change: the prior requirement for two-maintainer approvals has been
  removed; single-maintainer review is sufficient unless repository owners configure stricter
  rules in CODEOWNERS or CI.)
- Linting/formatting: backend uses `black` and `flake8`; frontend uses `prettier` and `eslint` (see
  repo docs). Use `uv run` for local test/task execution when available (e.g., `uv run pytest`).

## Governance

Amendments: Changes to this constitution MUST be proposed as a spec under `/specs/governance/`
and implemented via a PR that includes:

1. The proposed text change and rationale.
2. A migration or compliance plan for affected projects (if applicable).
3. Tests or checks demonstrating how the change will be enforced.

Approval: Constitutional amendments MUST be approved by at least one repository maintainer. For
material changes (principle additions/removals or governance redefinitions) the bump MUST be a
MAJOR version. Non-material clarifications are PATCHes.

Versioning policy (summary):

- MAJOR version: Backwards-incompatible governance or principle removals/redefinitions. Requires
  a migration plan and maintainer approval.
- MINOR version: New principle or materially expanded guidance which changes requirements for
  projects.
- PATCH version: Non-semantic clarifications, typo fixes, or wording changes.

Compliance review: Project maintainers MUST run a constitution compliance check during major
releases and when specs are merged that affect cross-cutting concerns. The `/speckit.plan` and
`/speckit.spec` workflows MUST reference this constitution and fail the Constitution Check if
required gates are not satisfied.

**Version**: 0.2.0 | **Ratified**: 2025-11-02 | **Last Amended**: 2025-11-03
