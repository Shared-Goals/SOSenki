"""Request service for managing client access requests."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import AccessRequest, RequestStatus
from src.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class RequestService:
    """Service for managing client requests."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_request(
        self,
        user_telegram_id: int,
        request_message: str,
        user_telegram_username: str | None = None,
    ) -> AccessRequest | None:
        """Create a new request from a client.

        Validates that no pending request exists for this client,
        then creates a new AccessRequest with status=pending.
        User record will be created only upon approval by admin.

        Args:
            user_telegram_id: Client's Telegram ID
            request_message: Request message text
            user_telegram_username: Client's Telegram username (optional)

        Returns:
            Created AccessRequest or None if validation fails (duplicate pending request)
        """
        # T028: Check for existing PENDING request from this client
        stmt = select(AccessRequest).where(
            AccessRequest.user_telegram_id == user_telegram_id,
            AccessRequest.status == RequestStatus.PENDING,
        )
        result = await self.session.execute(stmt)
        existing_pending = result.scalar_one_or_none()

        if existing_pending:
            # Client already has a pending request
            return None

        # Create new request directly without creating user
        # User will be created upon approval
        new_request = AccessRequest(
            user_telegram_id=user_telegram_id,
            user_telegram_username=user_telegram_username,
            request_message=request_message,
            status=RequestStatus.PENDING,
        )

        self.session.add(new_request)
        await self.session.flush()  # Get ID

        # Audit log (no actor_id - user-initiated, not admin action)
        await AuditService.log(
            session=self.session,
            entity_type="access_request",
            entity_id=new_request.id,
            action="create",
            actor_id=None,
            changes={
                "user_telegram_id": user_telegram_id,
                "user_telegram_username": user_telegram_username,
                "status": "pending",
            },
        )

        await self.session.commit()
        await self.session.refresh(new_request)

        return new_request

    async def get_pending_request(self, user_telegram_id: int) -> AccessRequest | None:
        """Get pending request for a client.

        Args:
            user_telegram_id: Client's Telegram ID

        Returns:
            Pending AccessRequest or None if not found
        """
        # T039: Query database for status=pending request from this client
        stmt = select(AccessRequest).where(
            AccessRequest.user_telegram_id == user_telegram_id,
            AccessRequest.status == RequestStatus.PENDING,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_request_by_id(self, request_id: int) -> AccessRequest | None:
        """Get request by ID.

        Args:
            request_id: Request ID

        Returns:
            AccessRequest or None if not found
        """
        stmt = select(AccessRequest).where(AccessRequest.id == request_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_request_status(
        self,
        request_id: int,
        new_status: RequestStatus,
        admin_telegram_id: int,
        admin_response: str | None = None,
    ) -> bool:
        """Update request status after admin action.

        Args:
            request_id: Request ID
            new_status: New status (approved/rejected)
            admin_telegram_id: Admin's Telegram ID
            admin_response: Admin's response message (optional)

        Returns:
            True if successful, False otherwise
        """
        # T040: Query, update status and admin details, commit
        result = await self.session.execute(
            select(AccessRequest).where(AccessRequest.id == request_id)
        )
        request = result.scalar_one_or_none()

        if not request:
            return False

        request.status = new_status
        request.admin_telegram_id = admin_telegram_id
        request.admin_response = admin_response
        # updated_at is auto-managed by ORM

        await self.session.commit()
        return True


__all__ = ["RequestService"]
