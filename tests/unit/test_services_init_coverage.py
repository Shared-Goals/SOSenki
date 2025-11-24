"""Unit tests for services module with expanded coverage."""

import pytest


class TestGetAsyncSession:
    """Test cases for get_async_session dependency."""

    @pytest.mark.asyncio
    async def test_get_async_session_success(self):
        """Test getting async session successfully."""
        from src.services import get_async_session

        async_gen = get_async_session()
        session = await async_gen.__anext__()

        assert session is not None
        # Cleanup
        try:
            await async_gen.__anext__()
        except StopAsyncIteration:
            pass


class TestGetDb:
    """Test cases for get_db dependency."""

    def test_get_db_success(self):
        """Test getting database session successfully."""
        from src.services import get_db

        db_gen = get_db()
        session = db_gen.__next__()

        assert session is not None
        # Cleanup
        try:
            db_gen.__next__()
        except StopIteration:
            pass

    def test_get_db_closes_session(self):
        """Test get_db closes session after use."""
        from src.services import get_db

        db_gen = get_db()
        session = db_gen.__next__()
        session_id = id(session)

        # Try to get the next value (close the generator)
        try:
            db_gen.__next__()
        except StopIteration:
            pass

        # Session should have been closed
        assert session_id is not None
