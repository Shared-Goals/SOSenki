"""Unit tests for UserStatusService.get_represented_user method."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.user_service import UserStatusService


@pytest.mark.asyncio
async def test_get_represented_user_with_valid_representative():
    """Test get_represented_user returns represented user when representative_id exists."""
    mock_session = AsyncMock()

    # Create mock users using MagicMock to avoid SQLAlchemy relationship issues
    mock_representing_user = MagicMock()
    mock_representing_user.id = 1
    mock_representing_user.representative_id = 2

    mock_represented_user = MagicMock()
    mock_represented_user.id = 2
    mock_represented_user.telegram_id = "456"
    mock_represented_user.representative_id = None

    # Mock session.get to return the correct user based on ID
    async def mock_get(model, user_id):
        if user_id == 1:
            return mock_representing_user
        elif user_id == 2:
            return mock_represented_user
        return None

    mock_session.get = AsyncMock(side_effect=mock_get)

    service = UserStatusService(mock_session)
    result = await service.get_represented_user(1)

    assert result is not None
    assert result.id == 2
    assert result.telegram_id == "456"


@pytest.mark.asyncio
async def test_get_represented_user_no_representative_id():
    """Test get_represented_user returns None when user has no representative_id."""
    mock_session = AsyncMock()

    # Mock a user with representative_id=None
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.representative_id = None

    async def mock_get(model, user_id):
        if user_id == 1:
            return mock_user
        return None

    mock_session.get = AsyncMock(side_effect=mock_get)

    service = UserStatusService(mock_session)
    result = await service.get_represented_user(1)

    assert result is None


@pytest.mark.asyncio
async def test_get_represented_user_user_not_found():
    """Test get_represented_user returns None when the representing user doesn't exist."""
    mock_session = AsyncMock()

    async def mock_get(model, user_id):
        return None

    mock_session.get = AsyncMock(side_effect=mock_get)

    service = UserStatusService(mock_session)
    result = await service.get_represented_user(999)

    assert result is None


@pytest.mark.asyncio
async def test_get_represented_user_represented_user_not_found():
    """Test get_represented_user returns None when represented user doesn't exist."""
    mock_session = AsyncMock()

    # Mock the representing user with representative_id pointing to non-existent user
    mock_representing_user = MagicMock()
    mock_representing_user.id = 1
    mock_representing_user.representative_id = 999

    async def mock_get(model, user_id):
        if user_id == 1:
            return mock_representing_user
        return None  # Represented user (ID 999) does not exist

    mock_session.get = AsyncMock(side_effect=mock_get)

    service = UserStatusService(mock_session)
    result = await service.get_represented_user(1)

    assert result is None
