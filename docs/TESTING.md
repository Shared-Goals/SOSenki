# Testing Guide

## Overview

All features are implemented test-first (TDD). This guide covers running the test suite locally and understanding test organization.

## Quick start & test-first workflow

If you're working test-first (the repo follows TDD), expect contract tests to fail
initially. A minimal quick-start:

1. Install `uv` (macOS):

```bash
brew install uv
```

1. Sync dependencies:

```bash
uv sync --group dev
```

1. Run a contract test (it should FAIL in a test-first workflow):

```bash
uv run --group dev python -m pytest backend/tests/contract/test_miniapp_auth_contract.py -v
```

1. Run a unit test (also expected to fail at first):

```bash
uv run --group dev python -m pytest backend/tests/unit/test_initdata_validation.py -v
```

1. Implement minimal stubs using `/specify.implement` or by hand to make tests pass.

The repository also contains `backend/TESTING.md` with a short Russian quick-start; we've
merged its unique guidance into this document and removed the duplicate file.

## Test Structure

```text
backend/tests/
├── conftest.py                              # Shared fixtures & test configuration
├── unit/                                    # Unit tests (service logic, pure functions)
│   ├── test_initdata_validation.py         # US1: HMAC signature & auth_date validation
│   ├── test_request_dedup.py               # US2: Request deduplication logic
│   └── test_admin_action_audit.py          # US3: Admin action & audit creation
└── contract/                                # Contract/API tests (endpoint validation)
    ├── test_miniapp_auth_contract.py       # US1: POST /miniapp/auth endpoint
    ├── test_requests_contract.py           # US2: POST /requests endpoint
    └── test_admin_action_contract.py       # US3: GET/POST /admin/requests endpoints
```

## Running Tests

### All Tests

```bash
uv run --group dev python -m pytest backend/tests/ -v
```

Expected output: **31 passed** (all tests pass)

### By Category

**Unit tests only:**

```bash
uv run --group dev python -m pytest backend/tests/unit/ -v
```

Expected: 11 passed (6 US1 + 4 US2 + 5 US3)

**Contract tests only:**

```bash
uv run --group dev python -m pytest backend/tests/contract/ -v
```

Expected: 12 passed (4 US1 + 5 US2 + 7 US3)

### By Feature

**US1 (Mini App Auth):**

```bash
uv run --group dev python -m pytest backend/tests/ -k "miniapp or initdata" -v
```

Expected: 10 passed

**US2 (Request Submission):**

```bash
uv run --group dev python -m pytest backend/tests/ -k "requests" -v
```

Expected: 9 passed

**US3 (Admin Decisions):**

```bash
uv run --group dev python -m pytest backend/tests/ -k "admin" -v
```

Expected: 12 passed

### With Coverage

```bash
uv run --group dev python -m pytest backend/tests/ --cov=backend/app --cov-report=term-missing
```

## Test Database

Tests use **SQLite in-memory** database configured in `backend/tests/conftest.py`:

- No external DB required
- Automatic table creation/cleanup per test
- Test isolation via fixtures
- Fast execution (~0.1s for full suite)

## Test Fixtures (conftest.py)

### Available Fixtures

- **`test_db_session`** — SQLite in-memory database session with tables created
- **`client`** — FastAPI TestClient with injected test database
- **`test_telegram_id`** — Sample Telegram user ID (123456789)
- **`test_init_data`** — Sample Telegram Mini App initData payload

### Usage Example

```python
def test_example(client, test_db_session):
    """Example test using fixtures."""
    # client: FastAPI test client with test database
    response = client.post("/requests", json={"telegram_id": 111111111, ...})
    assert response.status_code == 201
    
    # test_db_session: Direct database access for assertions
    candidate = test_db_session.query(TelegramUserCandidate).first()
    assert candidate is not None
```

## Common Test Commands

**Run single test file:**

```bash
uv run --group dev python -m pytest backend/tests/unit/test_initdata_validation.py -v
```

**Run single test:**

```bash
uv run --group dev python -m pytest backend/tests/unit/test_initdata_validation.py::TestInitDataValidation::test_verify_initdata_signature_valid -v
```

**Run with output:**

```bash
uv run --group dev python -m pytest backend/tests/ -v -s
```

**Run with traceback:**

```bash
uv run --group dev python -m pytest backend/tests/ -v --tb=long
```

## Writing New Tests

### Unit Test Template

```python
"""Unit tests for new feature."""
import pytest
from backend.app.services.my_service import my_function

class TestMyFeature:
    """Unit tests for my feature."""
    
    def test_success_case(self, test_db_session):
        """Test happy path."""
        result = my_function(db=test_db_session, param="value")
        assert result is not None
    
    def test_error_case(self, test_db_session):
        """Test error handling."""
        with pytest.raises(MyError):
            my_function(db=test_db_session, param="invalid")
```

### Contract Test Template

```python
"""Contract tests for new endpoint."""
from fastapi.testclient import TestClient

class TestMyEndpoint:
    """Contract tests for new endpoint."""
    
    def test_endpoint_exists(self, client: TestClient):
        """POST /myendpoint exists and returns 200."""
        response = client.post("/myendpoint", json={"field": "value"})
        assert response.status_code == 200
    
    def test_response_schema(self, client: TestClient):
        """Response matches expected schema."""
        response = client.post("/myendpoint", json={"field": "value"})
        data = response.json()
        assert "id" in data
        assert "created_at" in data
```

## CI/CD Pipeline

Tests are automatically run on:

- **Push to `main` or `develop`**
- **Pull Requests to `main` or `develop`**

Workflows in `.github/workflows/`:

- `test-backend.yaml` — Unit & contract tests, linting (Python 3.11 & 3.12)
- `validate-migrations.yaml` — Alembic migration validation
- `validate-openapi.yaml` — OpenAPI contract validation

## Debugging Failing Tests

### Check test output

```bash
uv run --group dev python -m pytest backend/tests/unit/test_file.py::TestClass::test_method -v -s
```

### Use pdb breakpoint

```python
def test_something(test_db_session):
    import pdb; pdb.set_trace()  # Execution pauses here
    result = some_function()
    assert result == expected
```

### Inspect database state

```python
def test_database_state(test_db_session):
    from backend.app.models import SOSenkiUser
    users = test_db_session.query(SOSenkiUser).all()
    print(f"Users in DB: {len(users)}")
    for user in users:
        print(f"  - {user.telegram_id}: {user.username}")
```

## Troubleshooting

### Tests fail with "fixture not found"

- Ensure `backend/tests/conftest.py` exists
- Check fixture name spelling

### Import errors

- Run `uv sync --group dev` to install all dependencies
- Check Python path: `uv run --group dev python -c "import backend.app"`

### Database errors

- Tests use in-memory SQLite, no external DB needed
- Check that `BaseModel` is properly initialized in models

### Flaky tests

- Most tests are deterministic (in-memory DB)
- If flaky, check for test isolation issues (fixtures not cleaning up properly)

## Test Metrics

**Current coverage:**

- 31 tests total
- 11 unit tests (service logic)
- 12 contract tests (API endpoints)
- ~0.1s execution time

**By feature:**

- US1 (Mini App Auth): 10 tests
- US2 (Request Submission): 9 tests
- US3 (Admin Decisions): 12 tests

---

**Have questions about tests?** Check `backend/tests/conftest.py` or open an issue.
