# Implementation Plan: Client Request Approval Workflow

**Branch**: `001-request-approval` | **Date**: 2025-11-04 | **Spec**: [Feature Specification](spec.md)
**Input**: Feature specification from `/specs/001-request-approval/spec.md`

## Summary

The Client Request Approval Workflow enables SOSenki to manage onboarding of new clients via Telegram. Clients submit access requests using `/request` command, the system notifies a predefined administrator, and the administrator approves or rejects with corresponding messages sent back to the client. This MVP focuses on simple text-based Telegram message handling with persistent request storage, enabling basic access control for the platform.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: FastAPI (HTTP service), python-telegram-bot (Telegram bot), SQLAlchemy (ORM), Alembic (migrations)  
**Storage**: SQLite (development), with migration path for production database  
**Testing**: pytest (unit and integration tests)  
**Target Platform**: Backend service running on Linux/cloud infrastructure  
**Project Type**: Single backend service (Telegram bot + API server)  
**Performance Goals**: Sub-second message delivery (< 1s), handle 100+ concurrent users  
**Constraints**: Real-time notification delivery, no more than 2-3 second latency for admin notifications  
**Scale/Scope**: MVP for single administrator, 10-100 initial users

## Constitution Check

✅ **PASSED**: All constitution principles satisfied:

| Principle | Check |
|-----------|-------|
| **YAGNI** | Feature scope tightly bounded: only request submission, approval, rejection. No bulk operations, filtering, or auto-expiration (out of scope). |
| **KISS** | Simple state machine (pending → approved/rejected). Text-only messages, no complex data structures. Single-table schema for MVP. |
| **DRY** | Request handling logic centralized in services, reusable across client/admin flows. Message templates defined once. |
| **Dependency Management** | All dependencies declared in pyproject.toml via uv. MCP Context7 used to validate python-telegram-bot API before implementation. |
| **Secret Management** | Admin Telegram ID stored in environment variable (ADMIN_TELEGRAM_ID), not hardcoded. |
| **Test-First** | Specs include contract tests for message workflows, integration tests for end-to-end flows. |

✅ **No violations**: Feature aligns with Python 3.11+, FastAPI stack, SQLite storage, uv package management, and test-first approach from constitution.

## Project Structure

### Documentation (this feature)

```text
specs/001-request-approval/
├── spec.md                    # Feature specification (completed)
├── plan.md                    # This file
├── research.md                # Phase 0: Library/API research (to be created)
├── data-model.md              # Phase 1: Database schema design (to be created)
├── quickstart.md              # Phase 1: Developer quickstart (to be created)
├── contracts/                 # Phase 1: API contracts (to be created)
│   ├── client_request.json
│   └── admin_response.json
└── tasks.md                   # Phase 2: Implementation tasks (to be created)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── request.py             # ClientRequest SQLAlchemy model
├── services/
│   ├── request_service.py     # Request creation, retrieval, state management
│   └── notification_service.py # Admin/client message sending
├── api/
│   └── telegram_handlers.py   # /request, admin reply handlers
├── bot/
│   └── telegram_bot.py        # Bot initialization, webhook setup
└── schemas/
    └── request_schema.py      # Pydantic models for validation

tests/
├── contract/
│   ├── test_client_submit_request.py
│   └── test_admin_approve_reject.py
├── integration/
│   ├── test_request_workflow.py
│   ├── test_approval_flow.py
│   └── test_rejection_flow.py
└── unit/
    ├── test_request_service.py
    ├── test_notification_service.py
    └── test_telegram_handlers.py

migrations/
└── versions/
    └── 001_create_requests_table.py # Alembic migration for ClientRequest table
```

**Structure Decision**: Single backend service with Telegram bot integrated directly into FastAPI application. The bot uses webhook mode (faster, more scalable than polling) to receive updates. Services layer abstracts business logic (requests, notifications) from Telegram-specific code.

## Data Model (Initial Design)

**ClientRequest** (SQLite table):

- `id` (PK, integer)
- `client_telegram_id` (integer, indexed)
- `request_message` (text)
- `submitted_at` (timestamp)
- `status` (enum: pending/approved/rejected)
- `admin_telegram_id` (integer, nullable—populated only if approved/rejected)
- `response_timestamp` (timestamp, nullable)
- `created_at`, `updated_at` (audit timestamps)

**Unique constraint**: (client_telegram_id, status) where status = 'pending' to prevent duplicate pending requests.

## Phases

### Phase 0: Research (This Plan)

✅ Completed: Feature specification and architecture review

**Remaining Phase 0 tasks**:

- [ ] Review python-telegram-bot documentation via MCP Context7 for webhook + message handling patterns
- [ ] Research FastAPI integration with Telegram bots (middleware, error handling)
- [ ] Document recommended message templates for welcome/rejection/confirmation

### Phase 1: Design & Setup

**Deliverables**:

- [ ] Database schema (data-model.md) with Alembic migration
- [ ] API contracts (requests/responses for client and admin flows)
- [ ] Quickstart guide for local development
- [ ] Project directory structure initialized

**Key design decisions**:

1. **Webhook vs polling**: Webhook mode for lower latency and scalability
2. **State machine**: Simple 3-state model (pending → approved OR rejected)
3. **Atomicity**: Use database transactions to ensure consistent state transitions
4. **Error handling**: Graceful degradation; if admin reply fails, request remains pending and can be retried

### Phase 2: Implementation

**Breakdown by user story** (to enable independent testing):

- **US1 (Client Request Submission)**: Request model, service, Telegram handler, tests
- **US2 (Admin Approval)**: Approval handler, welcome message, access grant, tests
- **US3 (Admin Rejection)**: Rejection handler, rejection message, tests

### Phase 3: Testing & Validation

- [ ] Contract tests validate message format/content
- [ ] Integration tests verify end-to-end workflows
- [ ] Manual testing with actual Telegram bot

## Complexity Justification

| Aspect | Justification |
|--------|--------------|
| **Async/await (FastAPI)** | Telegram API calls and database queries are I/O-bound; async enables handling multiple concurrent requests without thread overhead. |
| **SQLAlchemy ORM** | Ensures type safety, migration management, and auditing. Simpler than raw SQL queries for this schema size. |
| **Service layer abstraction** | Separates business logic (requests, notifications) from Telegram specifics; enables testability and future multi-channel support. |

## Dependencies & Assumptions

**Assumed to exist**:

- FastAPI application already initialized
- Telegram bot already created (BotFather token obtained)
- SQLite database configured
- Alembic migrations framework set up
- pytest configured for testing

**External integrations**:

- Telegram Bot API (python-telegram-bot library)
- Admin Telegram ID provided in environment (ADMIN_TELEGRAM_ID)

## Success Criteria (Revisited from Spec)

✅ Achievable with proposed architecture:

- SC-001: Sub-2-second request submission (FastAPI + SQLite performance)
- SC-002: Admin notification within 3 seconds (Telegram API + FastAPI performance)
- SC-003/004: Approval/rejection response within 5 seconds (database state transition + message send)
- SC-005: 100% request persistence (SQLite + transaction guarantees)
- SC-006: Atomic state transitions (database constraints + transaction handling)
- SC-007: Error-free operation (proper Telegram API error handling + logging)

## Next Steps

1. Execute Phase 0 research (library documentation review)
2. Create research.md documenting findings and decisions
3. Proceed to Phase 1 design (data-model.md, contracts, quickstart)
4. Generate tasks.md for implementation phase
