# Quickstart — Seamless Telegram Auth (feature 001)

This quickstart explains how to run and exercise the minimal API for the Seamless Telegram Auth MVP.

Prerequisites

- Docker & docker-compose (project provides `docker-compose.yml` to boot backend + db + frontend)
- Environment variables to set in `.env` (or your local env):
  - TELEGRAM_BOT_TOKEN — bot token used to send notifications (optional for local dev but required to notify users)
  - DATABASE_URL — postgres connection string (docker-compose provides one by default)
  - INITDATA_EXPIRATION_SECONDS — optional threshold for how old initData may be (default: 120)

Run locally

1) Start services using docker-compose from the repo root:

```bash
docker-compose up --build
```

1) Backend will be available at `http://localhost:8000` by default.

Exercising the API

- Verify Mini App initData (server must validate per Telegram docs):
  - POST `/miniapp/auth` with JSON body `{ "init_data": { ... } }` where `init_data` is the parsed initData object.
  - If the Telegram ID is already linked, response includes `linked: true` and `user` object.
  - If not linked, response includes `linked: false` and the frontend should show a short request form.

- Submit request form (unlinked user):
  - POST `/requests` with body `{ "telegram_id": 12345, "first_name": "Ivan", "note": "I am a researcher" }`.
  - Server returns `201` with the created request object.

- Admin actions (requires Administrator privileges):
  - GET `/admin/requests?status=pending` to list pending requests.
  - POST `/admin/requests/{request_id}/action` with body `{ "action": "accept", "role": "Researcher" }` to accept and create a new SOSenki user.

Testing notes

- Tests should be written test-first:
  - Contract tests that exercise `contracts/openapi.yaml` (ensure server matches contract).
  - Unit tests for initData signature verification and timestamp validation.
  - Integration tests for create-on-accept flow: create request -> admin accept -> SOSenkiUser created -> notification enqueued/sent.

Next steps

- Generate Phase 2 tasks and scaffold failing tests that implement the contract and data-model.
