"""Contract tests for admin handlers."""

import pytest
from fastapi.testclient import TestClient
from src.api.webhook import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestAdminHandlers:
    """Contract tests for admin approval/rejection handlers."""

    def test_admin_approval_handler(self, client):
        """Test admin approval response handler."""
        # TODO: T036 - POST /webhook/telegram with "Approve" reply → returns 200, status updated
        pass

    def test_approval_with_invalid_request(self, client):
        """Test approval when request doesn't exist."""
        # TODO: T037 - POST with "Approve" when request doesn't exist → returns 200, error message
        pass

    def test_admin_rejection_handler(self, client):
        """Test admin rejection response handler."""
        # TODO: T047 - POST /webhook/telegram with "Reject" reply → returns 200, status updated
        pass

    def test_rejection_with_invalid_request(self, client):
        """Test rejection when request doesn't exist."""
        # TODO: T048 - POST with "Reject" when request doesn't exist → returns 200, error message
        pass
