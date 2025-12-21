# follow **every** rule exactly; report any violation instead of silently fixing it.
# SOSenki AI Playbook (concise)

- Stack: Telegram bot + FastAPI backend + Mini App. Key dirs: src/api (FastAPI + webhook + MCP), src/bot (handlers + config), src/services (auth/balance/bills/period/transaction/llm/localizer/locale/audit), src/static/mini_app (vanilla JS + translations.json), alembic/versions (migrations), tests/{unit,contract,integration}.
- Runtime commands (non-negotiable): make serve & (start, auto-stop prior, spawns ngrok), make stop, make test (all suites), uv run pytest tests/path -v (targeted only), make format, make coverage, make check-i18n, make seed (dev only, app offline), make backup/restore (prod). Never run python/uvicorn/pytest directly; never kill ports manually.
- Environments: .env sets ENV=dev|prod; dev DB sosenki.dev.db, prod sosenki.db, tests test_sosenki.db. make serve writes /tmp/.sosenki-env with WEBHOOK_URL/MINI_APP_URL; DOMAIN presence skips ngrok for LAN. make install derives URLs + configures Caddy/systemd (prod).
- Auth pattern (src/services/auth_service.py): validate Telegram init_data (Authorization: tma <data> or x-telegram-init-data) via HMAC-SHA256 with bot token; produce AuthorizedUser (user, target, admin flags). Admins may switch target via target_telegram_id; use authorize_account_access for permission checks.
- LLM/MCP (src/api/mcp_server.py, src/services/llm_service.py): tools get_balance, list_bills, get_period_info, create_service_period (admin). get_user_tools vs get_admin_tools gated by ctx.is_admin; execute_tool routes into services; Ollama model default qwen2.5:1.5b.
- i18n: single source src/static/mini_app/translations.json with flat prefixes btn_/empty_/err_/hint_/label_/msg_/prompt_/status_/title_. Use t(key, **kwargs) in Python (src/services/localizer.py); JS uses t() after translations load; HTML via data-i18n attr. Run make check-i18n after user-facing changes.
- Locale helpers: src/services/locale_service.py (format_currency, format_local_datetime, get_currency_symbol); parsing in src/utils/parsers.py (parse_russian_decimal, parse_russian_currency). Reuse instead of custom formatting/parsing.
- Audit logging: src/services/audit_service.py; call after session.flush in service layer (not handlers) with entity_type (snake_case), action (create/update/delete/close/approve/reject), actor_id, optional changes. Coverage: transactions, bills, service_periods, electricity_readings, access_requests; user lifecycle deferred.
- Notifications: reuse src/services/notification_service.py.
- Data model roles (src/models/user.py): flags is_active, is_administrator, is_owner, is_stakeholder (requires owner), is_investor (needs active), is_tenant. Combine as needed.
- Migrations: uv run alembic revision --autogenerate -m "msg"; apply with uv run alembic upgrade head; check with uv run alembic current. After schema change in dev: uv run alembic upgrade head && make seed. No speculative fields (YAGNI).
- Testing: tests/conftest.py sets up test_sosenki.db via alembic upgrade head. Contract tests validate API schemas/MCP tools/handler registration; integration covers bot+API flows; unit for services/utilities. Markers @pytest.mark.{contract,integration,unit}. Use make test before merge.
- Style: Python 3.11+, type hints mandatory, async for I/O, Pydantic models, SQLAlchemy ORM patterns, docstrings for public APIs, ruff enforced (make format). Vanilla JS in Mini App (no frameworks).
- Security: no secrets or absolute paths in code; use env vars. Pending hardening (from Makefile): auth_date expiration check, hmac.compare_digest, rate limiting (slowapi), CORS allow_credentials=False.

# When in doubt
- Prefer simplest implementation (KISS) and avoid speculative work (YAGNI); deduplicate (DRY).
- If adding user-facing strings or data formatting, route through localizer/locale helpers and update translations.json.
- Ask for confirmation before risky ops; if instructions conflict, stop and ask.

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
