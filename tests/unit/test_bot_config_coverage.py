"""Unit tests for bot configuration with expanded coverage."""

import os
from unittest.mock import patch

import pytest

from src.bot.config import BotConfig, get_bot_config


class TestBotConfigValidation:
    """Test cases for BotConfig validation."""

    def test_validate_success(self):
        """Test validation succeeds with valid token."""
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_BOT_TOKEN": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
                "TELEGRAM_BOT_NAME": "test_bot",
                "TELEGRAM_MINI_APP_ID": "test_app",
            },
        ):
            config = BotConfig()
            config.validate()
            # Should not raise

    def test_validate_missing_token(self):
        """Test validation fails without telegram bot token."""
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_BOT_NAME": "test_bot",
                "TELEGRAM_MINI_APP_ID": "test_app",
            },
            clear=True,
        ):
            config = BotConfig(
                telegram_bot_name="test", telegram_mini_app_id="app", telegram_bot_token=""
            )
            with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
                config.validate()

    def test_bot_config_fields(self):
        """Test bot config has required fields."""
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_BOT_TOKEN": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
                "TELEGRAM_BOT_NAME": "test_bot",
                "TELEGRAM_MINI_APP_ID": "test_app",
            },
        ):
            config = BotConfig()
            assert config.telegram_bot_token == "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
            assert config.telegram_bot_name == "test_bot"
            assert config.telegram_mini_app_id == "test_app"

    def test_bot_config_singleton_instance(self):
        """Test get_bot_config creates and caches config."""
        with patch.dict(
            os.environ,
            {
                "TELEGRAM_BOT_TOKEN": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
                "TELEGRAM_BOT_NAME": "test_bot",
                "TELEGRAM_MINI_APP_ID": "test_app",
            },
        ):
            # First call should create instance
            config1 = get_bot_config()
            # Second call should return same instance
            config2 = get_bot_config()
            assert config1 is config2
