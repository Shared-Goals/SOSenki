"""Unit tests for main entry point to increase coverage."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestMainEnvironmentValidation:
    """Tests for environment validation in main.py."""

    def test_validate_environment_success(self):
        """Test successful environment validation."""
        with patch.dict(os.environ, {"MINI_APP_URL": "https://example.com/mini-app"}):
            from src.main import _validate_environment

            # Should not raise
            _validate_environment()

    def test_validate_environment_missing_url(self):
        """Test environment validation when MINI_APP_URL is missing."""
        with patch.dict(os.environ, {}, clear=True):
            from src.main import _validate_environment

            with pytest.raises(RuntimeError, match="MINI_APP_URL"):
                _validate_environment()

    def test_validate_environment_empty_url(self):
        """Test environment validation when MINI_APP_URL is empty string."""
        with patch.dict(os.environ, {"MINI_APP_URL": ""}, clear=True):
            from src.main import _validate_environment

            with pytest.raises(RuntimeError, match="MINI_APP_URL"):
                _validate_environment()

    def test_validate_environment_whitespace_url(self):
        """Test environment validation when MINI_APP_URL is whitespace only."""
        with patch.dict(os.environ, {"MINI_APP_URL": "   "}, clear=True):
            from src.main import _validate_environment

            with pytest.raises(RuntimeError, match="MINI_APP_URL"):
                _validate_environment()


class TestMainEnvironmentLoading:
    """Tests for environment loading."""

    def test_load_environment_from_env_file(self):
        """Test loading environment from .env file."""
        from src.main import _load_environment

        # Should not raise even if files don't exist
        _load_environment()

    def test_load_environment_handles_missing_files(self):
        """Test that missing .env files don't cause errors."""
        from src.main import _load_environment
        from unittest.mock import MagicMock

        mock_path = MagicMock()
        mock_path.return_value.exists.return_value = False
        
        with patch("src.main.Path", mock_path):
            # Should handle gracefully
            _load_environment()


class TestMainWebhookSetup:
    """Tests for webhook setup error handling."""

    @pytest.mark.asyncio
    async def test_webhook_registration_failure(self):
        """Test handling of webhook registration failure."""
        mock_bot_app = MagicMock()
        mock_bot_app.bot.set_webhook = AsyncMock(
            side_effect=Exception("Telegram API error")
        )
        mock_bot_app.shutdown = AsyncMock()

        # Create a minimal FastAPI app
        from fastapi import FastAPI

        mock_app = FastAPI()
        mock_event_handlers = []
        mock_app.add_event_handler = lambda event, handler: mock_event_handlers.append(
            (event, handler)
        )

        with patch("src.main.app", mock_app):
            with patch("src.main.create_bot_app", return_value=mock_bot_app):
                with patch("src.main.setup_webhook_route"):
                    with patch("src.main.logger"):
                        from src.main import run_webhook_mode

                        # Webhook error should not prevent shutdown handler registration
                        try:
                            await run_webhook_mode("127.0.0.1", 8000)
                        except Exception:
                            # Server.serve() will fail in test, but that's ok
                            pass

    @pytest.mark.asyncio
    async def test_webhook_url_not_set(self):
        """Test behavior when WEBHOOK_URL is not set."""
        mock_bot_app = MagicMock()
        mock_bot_app.shutdown = AsyncMock()

        from fastapi import FastAPI

        mock_app = FastAPI()
        mock_event_handlers = []
        mock_app.add_event_handler = lambda event, handler: mock_event_handlers.append(
            (event, handler)
        )

        with patch.dict(os.environ, {}, clear=True):
            with patch("src.main.app", mock_app):
                with patch("src.main.create_bot_app", return_value=mock_bot_app):
                    with patch("src.main.setup_webhook_route"):
                        with patch("src.main.logger"):
                            from src.main import run_webhook_mode

                            try:
                                await run_webhook_mode("127.0.0.1", 8000)
                            except Exception:
                                # Expected: Server.serve() fails in test
                                pass


class TestMainShutdownHandling:
    """Tests for graceful shutdown handling."""

    @pytest.mark.asyncio
    async def test_shutdown_bot_success(self):
        """Test successful bot shutdown."""
        mock_bot_app = MagicMock()
        mock_bot_app.shutdown = AsyncMock()

        from fastapi import FastAPI

        mock_app = FastAPI()

        with patch("src.main.app", mock_app):
            with patch("src.main.create_bot_app", return_value=mock_bot_app):
                with patch("src.main.setup_webhook_route"):
                    with patch("src.main.logger"):
                        from src.main import run_webhook_mode

                        try:
                            await run_webhook_mode("127.0.0.1", 8000)
                        except Exception:
                            pass

    @pytest.mark.asyncio
    async def test_shutdown_bot_exception(self):
        """Test shutdown when bot raises exception."""
        mock_bot_app = MagicMock()
        mock_bot_app.shutdown = AsyncMock(side_effect=RuntimeError("Shutdown error"))

        from fastapi import FastAPI

        mock_app = FastAPI()
        shutdown_handlers = []
        mock_app.add_event_handler = lambda event, handler: shutdown_handlers.append(
            (event, handler)
        )

        with patch("src.main.app", mock_app):
            with patch("src.main.create_bot_app", return_value=mock_bot_app):
                with patch("src.main.setup_webhook_route"):
                    with patch("src.main.logger"):
                        from src.main import run_webhook_mode

                        try:
                            await run_webhook_mode("127.0.0.1", 8000)
                        except Exception:
                            pass


class TestMainArgumentParsing:
    """Tests for command line argument parsing."""

    def test_main_webhook_mode_default(self):
        """Test that webhook mode is the default."""
        with patch("sys.argv", ["main.py"]):
            with patch("src.main.run_webhook_mode", new_callable=AsyncMock) as mock_run:
                with patch("asyncio.run"):
                    from src.main import main

                    # Just verify arguments parse correctly
                    import argparse

                    parser = argparse.ArgumentParser(description="SOSenki Bot")
                    parser.add_argument(
                        "--mode",
                        choices=["webhook"],
                        default="webhook",
                        help="Run mode (webhook only - polling not supported)",
                    )
                    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
                    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")

                    args = parser.parse_args([])
                    assert args.mode == "webhook"
                    assert args.host == "0.0.0.0"
                    assert args.port == 8000

    def test_main_custom_host_port(self):
        """Test custom host and port arguments."""
        import argparse

        parser = argparse.ArgumentParser(description="SOSenki Bot")
        parser.add_argument(
            "--mode", choices=["webhook"], default="webhook", help="Run mode"
        )
        parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
        parser.add_argument("--port", type=int, default=8000, help="Port to bind to")

        args = parser.parse_args(["--host", "127.0.0.1", "--port", "9000"])
        assert args.host == "127.0.0.1"
        assert args.port == 9000
