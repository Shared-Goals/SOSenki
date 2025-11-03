"""Pytest configuration and shared fixtures for backend tests."""
import pytest
from typing import Generator


@pytest.fixture
def test_telegram_id() -> int:
    """Provide a test Telegram ID."""
    return 123456789


@pytest.fixture
def test_init_data() -> dict:
    """Provide sample initData from Telegram Web App (not cryptographically valid, for test only)."""
    return {
        "user": {
            "id": 123456789,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "language_code": "en",
            "is_premium": False,
        },
        "auth_date": 1730629500,
        "hash": "test_hash_not_validated_in_unit_tests",
    }
