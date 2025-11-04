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
        # T029: Send message via bot
        try:
            await self.bot.send_message(chat_id=int(chat_id), text=text)
        except Exception as e:
            print(f"Error sending message to {chat_id}: {e}")
            raise

    async def send_confirmation_to_client(
        self, client_id: str, message: str = None
    ) -> None:
        """Send confirmation message to client after request submission.

        Args:
            client_id: Client's Telegram ID
            message: Optional custom message (not used in MVP, using standard message)
        """
        # T029: Send standard confirmation message
        confirmation_text = (
            "Your request has been received and is pending review."
        )
        await self.send_message(client_id, confirmation_text)

    async def send_notification_to_admin(
        self, request_id: int, client_id: str, client_name: str = None, request_message: str = None
    ) -> None:
        """Send notification to admin about new request.

        Args:
            request_id: Request ID from database
            client_id: Client's Telegram ID
            client_name: Client's name from Telegram
            request_message: The client's request message
        """
        # Import here to avoid circular import
        from src.bot.config import bot_config
        
        # T030: Send notification with [Approve] [Reject] reply keyboard
        notification_text = (
            f"Client Request: {client_name or 'User'} (ID: {client_id}) - '{request_message or '(no message)'}'"
        )

        # Note: Reply keyboard implementation requires storing request_id
        # in the message context for admin handlers to parse.
        # For now, send the message. Admin handlers will need to track
        # which message replies correspond to which requests.

        # TODO: Implement reply keyboard with callback data
        # For MVP, using simple Approve/Reject text responses
        await self.send_message(bot_config.admin_telegram_id, notification_text)

    async def send_welcome_message(self, client_id: str) -> None:
        """Send welcome message to approved client.

        Args:
            client_id: Client's Telegram ID
        """
        # T041: Send welcome message after approval
        welcome_text = (
            "Welcome to SOSenki! Your request has been approved and access "
            "has been granted. You can now use all features."
        )
        await self.send_message(client_id, welcome_text)

    async def send_rejection_message(self, client_id: str) -> None:
        """Send rejection message to rejected client.

        Args:
            client_id: Client's Telegram ID
        """
        # T050: Send rejection message after rejection
        rejection_text = (
            "Your request for access to SOSenki has not been approved at this time. "
            "Please contact support if you have questions."
        )
        await self.send_message(client_id, rejection_text)


__all__ = ["NotificationService"]
