"""Telegram bot application factory."""

from telegram.ext import Application
from src.bot.config import bot_config


async def create_bot_app() -> Application:
    """Create and return Telegram bot application with async handlers."""
    app = (
        Application.builder()
        .token(bot_config.telegram_bot_token)
        .build()
    )

    # Handlers will be registered in src/bot/handlers.py
    # Initialize any other bot-level setup here

    return app


__all__ = ["create_bot_app"]
