"""Audit service for logging entity lifecycle events."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.audit_log import AuditLog


class AuditService:
    """Service for audit log operations.

    Provides static method to create minimal audit log entries.
    """

    @staticmethod
    async def log(
        session: AsyncSession,
        entity_type: str,
        entity_id: int,
        action: str,
        actor_id: int | None = None,
        changes: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Create audit log entry (async).

        Args:
            session: Async database session
            entity_type: Type of entity (lowercase: "transaction", "bill", "period", etc.)
            entity_id: Primary key of the entity
            action: Action performed (present tense: "create", "update", "delete", "close", etc.)
            actor_id: User (admin) who performed the action (required for user-initiated operations)
            changes: Optional JSON snapshot of changed fields

        Returns:
            Created AuditLog object (not yet committed)
        """
        audit = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            changes=changes,
        )
        session.add(audit)
        return audit


__all__ = ["AuditService"]
