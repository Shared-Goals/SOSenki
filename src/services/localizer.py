"""Simple localization module for SOSenki.

Loads Russian translations from translations.json once at import time.
Provides a single t(key, **kwargs) function for translation lookup with flat keys.

Translation Key Naming Convention (Flat Structure with Prefixes):
    - btn_*         Clickable buttons (btn_approve, btn_cancel)
    - prompt_*      Input prompts for bot conversations (prompt_meter_start, prompt_budget_main)
    - msg_*         Informational messages/notifications (msg_welcome, msg_period_created)
    - err_*         Error messages (err_invalid_number, err_not_authorized)
    - status_*      State labels (status_open, status_closed, status_pending)
    - empty_*       Empty state messages (empty_bills, empty_transactions)
    - nav_*         Navigation labels (nav_balance, nav_invest)
    - hint_*        Helper text (hint_previous_value)
    - title_*       Section headers (title_existing_periods)
    - label_*       Generic labels (label_weight, label_tenant)
    - action_*      Action button labels (action_new_period, action_close_period)

Domain Suffix Convention:
    Add domain-specific suffix only when ambiguous (Option C).
    Examples:
        - prompt_budget_main / prompt_budget_conservation (disambiguate main vs conservation)
        - prompt_meter_start (domain obvious from context, no suffix needed)
        - empty_bills_list / empty_bills (both exist for different contexts)

Usage:
    from src.services.localizer import t

    # Simple lookup
    message = t("msg_welcome")

    # With placeholder substitution
    message = t("err_group_chat", bot_name="SOSenkiBot")
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Load translations once at import time
_TRANSLATIONS_PATH = Path(__file__).parent.parent / "static" / "mini_app" / "translations.json"
_TRANSLATIONS: dict[str, Any] = {}

try:
    with open(_TRANSLATIONS_PATH, encoding="utf-8") as f:
        _TRANSLATIONS = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    logger.error("Failed to load translations from %s: %s", _TRANSLATIONS_PATH, e)


def t(key: str, **kwargs: Any) -> str:
    """Get translation for a flat key with optional placeholder substitution.

    Args:
        key: Flat key with prefix convention (e.g., "msg_welcome", "err_group_chat")
        **kwargs: Placeholder values for string formatting

    Returns:
        Translated string with placeholders replaced, or the key itself if not found.

    Examples:
        >>> t("msg_welcome")
        "Добро пожаловать в SOSenki! 🏠"

        >>> t("err_group_chat", bot_name="SOSenkiBot")
        "❌ Запросы можно отправлять только в личные сообщения..."
    """
    value = _TRANSLATIONS.get(key)

    if value is None:
        logger.warning("Translation key not found: %s", key)
        return key

    if not isinstance(value, str):
        logger.warning("Translation value is not a string for key: %s", key)
        return key

    if kwargs:
        try:
            return value.format(**kwargs)
        except KeyError as e:
            logger.warning("Missing placeholder %s for key: %s", e, key)
            return value

    return value


__all__ = ["t"]
