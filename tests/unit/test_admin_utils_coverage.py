"""Unit tests for admin_utils with expanded coverage."""

from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from src.models.user import User
from src.services.admin_utils import get_admin_telegram_id, get_admin_user


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return MagicMock(spec=Session)


class TestGetAdminTelegramId:
    """Test cases for get_admin_telegram_id."""

    def test_get_admin_telegram_id_found(self, mock_db_session):
        """Test retrieving admin telegram ID successfully."""
        admin_user = User(id=1, name="Admin", telegram_id="123456789", is_administrator=True)
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = admin_user

        result = get_admin_telegram_id(mock_db_session)

        assert result == "123456789"
        mock_db_session.execute.assert_called_once()

    def test_get_admin_telegram_id_not_found(self, mock_db_session):
        """Test retrieving admin telegram ID when no admin exists."""
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = None

        result = get_admin_telegram_id(mock_db_session)

        assert result is None

    def test_get_admin_telegram_id_no_telegram_id(self, mock_db_session):
        """Test retrieving admin telegram ID when admin has no telegram_id."""
        admin_user = User(id=1, name="Admin", telegram_id=None, is_administrator=True)
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = admin_user

        result = get_admin_telegram_id(mock_db_session)

        assert result is None

    def test_get_admin_telegram_id_exception(self, mock_db_session):
        """Test exception handling when retrieving admin telegram ID."""
        mock_db_session.execute.side_effect = Exception("DB Error")

        result = get_admin_telegram_id(mock_db_session)

        assert result is None


class TestGetAdminUser:
    """Test cases for get_admin_user."""

    def test_get_admin_user_found(self, mock_db_session):
        """Test retrieving admin user successfully."""
        admin_user = User(id=1, name="Admin", telegram_id="123456789", is_administrator=True)
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = admin_user

        result = get_admin_user(mock_db_session)

        assert result is admin_user
        assert result.name == "Admin"
        mock_db_session.execute.assert_called_once()

    def test_get_admin_user_not_found(self, mock_db_session):
        """Test retrieving admin user when no admin exists."""
        mock_db_session.execute.return_value.scalars.return_value.first.return_value = None

        result = get_admin_user(mock_db_session)

        assert result is None

    def test_get_admin_user_exception(self, mock_db_session):
        """Test exception handling when retrieving admin user."""
        mock_db_session.execute.side_effect = Exception("DB Error")

        result = get_admin_user(mock_db_session)

        assert result is None
