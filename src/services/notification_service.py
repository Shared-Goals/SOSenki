"""Notification service for sending Telegram messages."""

from telegram.ext import Application


class NotificationService:
    """Service for sending Telegram messages to clients and admins."""

    def __init__(self, app: Application):
        self.app = app
        self.bot = app.bot

    async def send_message(self, chat_id: str, text: str) -> None:
        """Send message to a Telegram chat.

        Args:
            chat_id: Telegram chat ID
            text: Message text
        """
        # TODO: T029, T030, T041, T050 - Implement message sending
        pass

    async def send_confirmation_to_client(self, client_id: str, message: str) -> None:
        """Send confirmation message to client after request submission.

        Args:
            client_id: Client's Telegram ID
            message: Optional custom message
        """
        # TODO: T029 - Implement
        pass

    async def send_notification_to_admin(
        self, request_id: int, client_id: str, client_name: str, request_message: str
    ) -> None:
        """Send notification to admin about new request.

        Args:
            request_id: Request ID from database
            client_id: Client's Telegram ID
            client_name: Client's name from Telegram
            request_message: The client's request message
        """
        # TODO: T030 - Implement with [Approve] [Reject] reply keyboard
        pass

    async def send_welcome_message(self, client_id: str) -> None:
        """Send welcome message to approved client.

        Args:
            client_id: Client's Telegram ID
        """
        # TODO: T041 - Implement
        pass

    async def send_rejection_message(self, client_id: str) -> None:
        """Send rejection message to rejected client.

        Args:
            client_id: Client's Telegram ID
        """
        # TODO: T050 - Implement
        pass


__all__ = ["NotificationService"]
