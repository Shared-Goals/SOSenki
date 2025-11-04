"""Telegram bot application factory."""

from telegram.ext import Application, CommandHandler

from src.bot.config import bot_config
from src.bot.handlers import handle_request_command


async def create_bot_app() -> Application:
    """Create and return Telegram bot application with async handlers.

    T032, T044, T052: Register command handlers with the bot application.
    """
    app = (
        Application.builder()
        .token(bot_config.telegram_bot_token)
        .build()
    )

    # T031/T032: Register /request command handler
    app.add_handler(CommandHandler("request", handle_request_command))

    # Note: Approval/Rejection handlers are called directly in test fixtures
    # and via Update message routing in production. Handler registration
    # deferred to Phase 6 for production deployment (T044, T052).

    # Initialize any other bot-level setup here

    return app


__all__ = ["create_bot_app"]
