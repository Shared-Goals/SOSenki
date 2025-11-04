"""Contract tests for /webhook/telegram endpoint."""

import pytest
from fastapi.testclient import TestClient
from src.api.webhook import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestRequestEndpoint:
    """Contract tests for /request command endpoint."""

    def test_webhook_endpoint_exists(self, client):
        """Test that webhook endpoint is available."""
        # TODO: T025 - POST /webhook/telegram with /request update → returns 200
        pass

    def test_duplicate_request_rejection(self, client):
        """Test that duplicate pending requests are rejected."""
        # TODO: T026 - POST with /request from client with existing PENDING
        # → returns 200, error message
        pass
