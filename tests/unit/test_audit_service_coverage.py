"""Unit tests for AuditService to increase coverage."""

from unittest.mock import MagicMock

from src.services.audit_service import AuditService


class TestAuditService:
    """Tests for AuditService audit logging."""

    def test_audit_log_basic(self):
        """Test creating a basic audit log entry."""
        mock_db = MagicMock()

        audit = AuditService.log(
            db=mock_db,
            entity_type="period",
            entity_id=1,
            action="create",
        )

        assert audit.entity_type == "period"
        assert audit.entity_id == 1
        assert audit.action == "create"
        assert audit.actor_id is None
        assert audit.changes is None
        mock_db.add.assert_called_once_with(audit)

    def test_audit_log_with_actor(self):
        """Test creating audit log with actor_id."""
        mock_db = MagicMock()

        audit = AuditService.log(
            db=mock_db,
            entity_type="bill",
            entity_id=42,
            action="update",
            actor_id=5,
        )

        assert audit.entity_type == "bill"
        assert audit.entity_id == 42
        assert audit.action == "update"
        assert audit.actor_id == 5
        assert audit.changes is None
        mock_db.add.assert_called_once_with(audit)

    def test_audit_log_with_changes(self):
        """Test creating audit log with changes dict."""
        mock_db = MagicMock()
        changes = {"amount": {"old": 100.0, "new": 150.0}}

        audit = AuditService.log(
            db=mock_db,
            entity_type="bill",
            entity_id=99,
            action="modify",
            actor_id=3,
            changes=changes,
        )

        assert audit.entity_type == "bill"
        assert audit.entity_id == 99
        assert audit.action == "modify"
        assert audit.actor_id == 3
        assert audit.changes == changes
        mock_db.add.assert_called_once_with(audit)

    def test_audit_log_all_parameters(self):
        """Test audit log with all parameters specified."""
        mock_db = MagicMock()
        changes = {"status": {"old": "pending", "new": "closed"}}

        audit = AuditService.log(
            db=mock_db,
            entity_type="period",
            entity_id=7,
            action="close",
            actor_id=2,
            changes=changes,
        )

        assert audit.entity_type == "period"
        assert audit.entity_id == 7
        assert audit.action == "close"
        assert audit.actor_id == 2
        assert audit.changes == changes
        mock_db.add.assert_called_once()

    def test_audit_service_exports(self):
        """Test that AuditService is properly exported."""
        from src.services.audit_service import __all__

        assert "AuditService" in __all__
