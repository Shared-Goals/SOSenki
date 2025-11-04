"""Admin service for approval and rejection workflows."""

from sqlalchemy.orm import Session


class AdminService:
    """Service for admin approval/rejection operations."""

    def __init__(self, db_session: Session):
        self.db = db_session

    async def approve_request(
        self,
        request_id: int,
        admin_telegram_id: str,
    ) -> bool:
        """Approve a client request.

        Args:
            request_id: Request ID to approve
            admin_telegram_id: Admin's Telegram ID

        Returns:
            True if successful, False otherwise
        """
        # TODO: T042 - Update status to approved, mark client as active
        pass

    async def reject_request(
        self,
        request_id: int,
        admin_telegram_id: str,
    ) -> bool:
        """Reject a client request.

        Args:
            request_id: Request ID to reject
            admin_telegram_id: Admin's Telegram ID

        Returns:
            True if successful, False otherwise
        """
        # TODO: - Update status to rejected
        pass

    async def get_admin_config(self) -> dict | None:
        """Get admin configuration.

        Returns:
            Admin config or None
        """
        # TODO: - Load admin from config or database
        pass


__all__ = ["AdminService"]
