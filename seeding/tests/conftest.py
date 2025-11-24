"""Pytest configuration for seeding tests - applies migrations automatically.

Database Strategy for Seeding/Data Integrity Tests:
- Uses: sosenki.db (main seeded database)
- Purpose: Data integrity tests verify that Google Sheets data is correctly imported
- Workflow: make seed → populates sosenki.db → make test-seeding → verifies data integrity
- Note: For unit/integration tests, see tests/conftest.py which uses test_sosenki.db for isolation
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Set test database URL BEFORE any imports from src
# For data integrity tests: use the main seeded database (sosenki.db)
# For other tests: they should use test isolation separately
os.environ["DATABASE_URL"] = "sqlite:///./sosenki.db"

# Set dummy test token for TELEGRAM_BOT_TOKEN (required by bot config validation)
# This is only used for unit/contract tests that don't make actual API calls
os.environ["TELEGRAM_BOT_TOKEN"] = "test_token_1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Set test mini app URL (required for application startup)
os.environ["MINI_APP_URL"] = "http://localhost:3000/mini-app/"

# Set seeding config path (required for seeding tests)
os.environ["SEEDING_CONFIG_PATH"] = "seeding/config/seeding.json"

# Get the project root directory
project_root = Path(__file__).parent.parent.parent

# Apply migrations immediately on test startup
try:
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "DATABASE_URL": "sqlite:///./sosenki.db"},
    )

    if result.returncode != 0:
        print(
            f"WARNING: Alembic migration failed with return code {result.returncode}",
            file=sys.stderr,
        )
        print("STDOUT:", result.stdout, file=sys.stderr)
        print("STDERR:", result.stderr, file=sys.stderr)
    else:
        print("✓ Applied migrations to test database", file=sys.stderr)
except subprocess.TimeoutExpired:
    print("WARNING: Alembic migration timed out", file=sys.stderr)
except Exception as e:
    print(f"WARNING: Failed to apply migrations: {e}", file=sys.stderr)


@pytest.fixture
def db() -> Session:
    """Provide a database session for tests - uses seeded main database for integrity tests."""
    engine = create_engine(
        "sqlite:///./sosenki.db",
        connect_args={"check_same_thread": False},
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
