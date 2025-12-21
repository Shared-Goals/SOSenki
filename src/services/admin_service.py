"""Admin service for approval and rejection workflows."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.access_request import AccessRequest, RequestStatus
from src.models.user import User
from src.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class AdminService:
    """Service for admin approval/rejection operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def approve_request(
        self,
        request_id: int,
        admin_user: User,
        selected_user_id: int | None = None,
    ) -> AccessRequest | None:
        """Approve a client request.

        T040, T042: Update status to approved, mark client as active.

        When selected_user_id is provided, links the request creator (via client_telegram_id)
        to the selected user and assigns their Telegram ID and username.

        Args:
            request_id: Request ID to approve
            admin_user: Verified admin User object (guaranteed is_administrator=True)
            selected_user_id: If provided, assign Telegram ID to user with this ID

        Returns:
            Updated request object if successful, None otherwise
        """
        try:
            # Find the request
            stmt = select(AccessRequest).where(AccessRequest.id == request_id)
            result = await self.session.execute(stmt)
            request = result.scalar_one_or_none()

            if not request:
                logger.warning("Request %d not found for approval", request_id)
                return None

            # Get the requester's username from the stored request
            requester_username = request.user_telegram_username

            # If user ID provided, link request creator to that user
            if selected_user_id is not None and selected_user_id > 0:
                selected_user = await self.session.get(User, selected_user_id)

                if selected_user:
                    # Assign the request creator's Telegram credentials to the selected user
                    selected_user.telegram_id = request.user_telegram_id
                    selected_user.username = requester_username
                    selected_user.is_active = True
                    logger.info(
                        "Assigned Telegram ID %s (username: %s) to user %s (ID: %d)",
                        request.user_telegram_id,
                        requester_username,
                        selected_user.name,
                        selected_user.id,
                    )
                else:
                    logger.warning("User ID %d not found for Telegram assignment", selected_user_id)
                    return None
            else:
                # No selected user, find or create user by telegram_id
                stmt = select(User).where(User.telegram_id == request.user_telegram_id)
                result = await self.session.execute(stmt)
                user = result.scalar_one_or_none()

                if user:
                    user.is_active = True
                    logger.info("Activated user %s on approval", request.user_telegram_id)
                else:
                    # Create user if it doesn't exist (user should be created on first approval)
                    placeholder_name = f"User_{request.user_telegram_id}"
                    user = User(
                        telegram_id=request.user_telegram_id, name=placeholder_name, is_active=True
                    )
                    self.session.add(user)
                    logger.info("Created new user %s on approval", request.user_telegram_id)

            # Update request status to approved
            request.status = RequestStatus.APPROVED
            request.admin_response = "approved"
            request.admin_telegram_id = admin_user.telegram_id

            await self.session.flush()  # Ensure IDs are assigned

            # Audit log
            await AuditService.log(
                session=self.session,
                entity_type="access_request",
                entity_id=request.id,
                action="approve",
                actor_id=admin_user.id,
                changes={
                    "status": "approved",
                    "user_telegram_id": request.user_telegram_id,
                    "selected_user_id": selected_user_id,
                },
            )

            await self.session.commit()
            logger.info(
                "Request %d approved by admin telegram_id=%d", request_id, admin_user.telegram_id
            )
            return request

        except Exception as e:
            logger.error("Error approving request %d: %s", request_id, e, exc_info=True)
            await self.session.rollback()
            return None

    async def reject_request(
        self,
        request_id: int,
        admin_user: User,
    ) -> AccessRequest | None:
        """Reject a client request.

        T040: Update status to rejected.

        Args:
            request_id: Request ID to reject
            admin_user: Verified admin User object (guaranteed is_administrator=True)

        Returns:
            Updated request object if successful, None otherwise
        """
        try:
            # Find the request
            stmt = select(AccessRequest).where(AccessRequest.id == request_id)
            result = await self.session.execute(stmt)
            request = result.scalar_one_or_none()

            if not request:
                logger.warning("Request %d not found for rejection", request_id)
                return None

            # Update request status to rejected
            request.status = RequestStatus.REJECTED
            request.admin_telegram_id = admin_user.telegram_id
            request.admin_response = "rejected"

            await self.session.flush()  # Ensure changes are persisted

            # Audit log
            await AuditService.log(
                session=self.session,
                entity_type="access_request",
                entity_id=request.id,
                action="reject",
                actor_id=admin_user.id,
                changes={
                    "status": "rejected",
                    "user_telegram_id": request.user_telegram_id,
                },
            )

            await self.session.commit()
            logger.info(
                "Request %d rejected by admin telegram_id=%d", request_id, admin_user.telegram_id
            )
            return request

        except Exception as e:
            logger.error("Error rejecting request %d: %s", request_id, e, exc_info=True)
            await self.session.rollback()
            return None

    async def get_admin_config(self) -> dict | None:
        """Get admin configuration.

        Returns:
            Admin config or None
        """
        # TODO: - Load admin from config or database
        pass


__all__ = ["AdminService"]
