# SOSenki Feature Development & Contributing

This guide covers local development setup, running tests, and contributing to the
SOSenki project. It consolidates the canonical contributing guidance — the single
source of truth is `docs/CONTRIBUTING.md`.

## Quick Start

### Prerequisites

- Python 3.11+ (project constitution requirement)
- `uv` package manager ([https://docs.astral.sh/uv/](https://docs.astral.sh/uv/))
- PostgreSQL 12+ (for production; SQLite used in tests)

### Local Setup

1. Clone and install dependencies:

```bash
git clone https://github.com/Shared-Goals/SOSenki.git
cd SOSenki
uv sync --group dev
```

1. Set up environment variables:

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your local settings
```

1. Initialize the database (for local Postgres dev):

```bash
cd backend
uv run --group dev alembic upgrade head
cd ..
```

1. Run the development server:

```bash
uv run --group dev python -m uvicorn backend.app.main:app --reload
```

Server will be available at `http://localhost:8000` by default.

## Testing

Run all tests:

```bash
uv run --group dev python -m pytest backend/tests/ -v
```

Run specific categories:

- Unit tests only:

```bash
uv run --group dev python -m pytest backend/tests/unit/ -v
```

- Contract tests only:

```bash
uv run --group dev python -m pytest backend/tests/contract/ -v
```

- Integration tests (if present):

```bash
uv run --group dev python -m pytest backend/tests/integration/ -v
```

Run with coverage:

```bash
uv run --group dev python -m pytest backend/tests/ --cov=backend/app --cov-report=html
# Coverage report will be in htmlcov/index.html
```

## Code Quality

Format code:

```bash
uv run --group dev black backend/app backend/tests
```

Check formatting without modifying:

```bash
uv run --group dev black --check backend/app backend/tests
```

Lint:

```bash
uv run --group dev flake8 backend/app backend/tests
```

Type checking (optional):

```bash
uv run --group dev mypy backend/app
```

Run all quality checks:

```bash
./scripts/check-quality.sh  # If available
# Or manually:
uv run --group dev black --check backend/app backend/tests
uv run --group dev flake8 backend/app backend/tests
uv run --group dev python -m pytest backend/tests/ -v
```

## Database Migrations

Create a new migration:

```bash
cd backend
uv run --group dev alembic revision --autogenerate -m "descriptive_name"
cd ..
```

Apply migrations:

```bash
cd backend
uv run --group dev alembic upgrade head
cd ..
```

View migration history:

```bash
cd backend
uv run --group dev alembic history
cd ..
```

Rollback migrations:

```bash
cd backend
uv run --group dev alembic downgrade -1  # Downgrade one revision
# or
uv run --group dev alembic downgrade base  # Rollback all migrations
cd ..
```

## Project Structure

```text
SOSenki/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── config.py               # Configuration & environment
│   │   ├── database.py             # SQLAlchemy setup
│   │   ├── logging.py              # Logging configuration
│   │   ├── api/
│   │   │   ├── routes/             # API endpoints (miniapp, requests, admin_requests)
│   │   │   └── errors.py           # Error handlers
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic validation schemas
│   │   └── services/               # Business logic services
│   ├── migrations/                 # Alembic database migrations
│   ├── tests/
│   │   ├── unit/                   # Unit tests
│   │   ├── contract/               # Contract/API tests
│   │   ├── integration/            # Integration tests
│   │   └── conftest.py             # Pytest configuration & fixtures
│   └── pyproject.toml              # Project dependencies & config
├── specs/                          # Feature specifications
└── docs/                           # Documentation
```

## API Endpoints

### Mini App Authentication (US1)

- **POST /miniapp/auth** — Verify Telegram initData, return user status

### Request Submission (US2)

- **POST /requests** — Create a join request as unlinked user

### Admin Management (US3)

- **GET /admin/requests** — List pending requests
- **POST /admin/requests/{request_id}/action** — Accept/reject requests

For detailed API documentation, visit `/docs` or `/redoc` when the server is running.

## Commit & Branch Conventions

- **Branch naming:** `feature/short-description` or `fix/short-description`
- **Commit messages:** English, clear and concise (e.g., "Add user authentication endpoint")
- **One logical change per commit** — helps with review and cherry-picking

## Contributing Workflow

1. Create a feature branch:

```bash
git checkout -b feature/new-feature-name
```

1. Make your changes and test:

```bash
uv run --group dev python -m pytest backend/tests/ -v
uv run --group dev black backend/app
uv run --group dev flake8 backend/app
```

1. Commit your changes:

```bash
git add .
git commit -m "Descriptive commit message"
```

1. Push and create a Pull Request:

```bash
git push origin feature/new-feature-name
```

1. CI will automatically run tests, linting, and migration validation

## Troubleshooting

### "Module not found" errors

- Make sure you've run `uv sync --group dev` to install all dependencies.

### Database connection errors

- Check that `DATABASE_URL` in `backend/.env` is correct and the database server is running.

### Tests fail with "fixture not found"

- Ensure `backend/tests/conftest.py` exists and is properly configured.

### Alembic migration errors

- Run `uv sync --group dev` to ensure Alembic is installed
- Check that `alembic.ini` exists in the repo root
- Verify environment variables are set correctly

## Documentation & Specs

- API specification: `specs/001-seamless-telegram-auth/contracts/openapi.yaml`
- Feature tasks: `specs/001-seamless-telegram-auth/tasks.md`
- Data model: `specs/001-seamless-telegram-auth/data-model.md`
- Architecture decisions: `docs/ARCHITECTURE.md`

## Additional Resources

- [FastAPI docs](https://fastapi.tiangolo.com)
- [SQLAlchemy docs](https://docs.sqlalchemy.org)
- [Pydantic docs](https://docs.pydantic.dev)
- [Alembic docs](https://alembic.sqlalchemy.org)
- [uv docs](https://docs.astral.sh/uv/)

---

**Questions?** Open an issue on GitHub or check existing documentation in `docs/` folder.

**Thank you for helping grow SOSenki!** 🌲
