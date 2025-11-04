"""FastAPI webhook endpoint for Telegram updates."""

from fastapi import FastAPI, HTTPException
from telegram import Update
from telegram.ext import Application

# FastAPI instance (will be initialized in main.py)
app = FastAPI(
    title="SOSenki Bot",
    description="Client Request Approval Workflow - Telegram Bot",
    version="0.1.0",
)


async def setup_webhook_route(app: FastAPI, bot_app: Application) -> None:
    """Register webhook endpoint with FastAPI.

    Args:
        app: FastAPI application instance
        bot_app: Telegram bot Application instance
    """

    @app.post("/webhook/telegram")
    async def telegram_webhook(update: dict) -> dict:
        """Receive Telegram updates and dispatch to bot handlers.

        Args:
            update: Telegram Update object (as JSON)

        Returns:
            {"ok": True} response as per Telegram webhook protocol
        """
        try:
            # Convert dict to Telegram Update object
            telegram_update = Update.de_json(update, bot_app.bot)
            if telegram_update:
                # Process update through bot application
                await bot_app.process_update(telegram_update)
            return {"ok": True}
        except Exception as e:
            print(f"Error processing update: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint for monitoring."""
        return {"status": "ok"}


__all__ = ["app", "setup_webhook_route"]
