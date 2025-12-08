"""Prompt loader for external .prompt.md files.

Loads prompts at import time and substitutes locale placeholders.
"""

from pathlib import Path

from src.services.locale_service import get_currency_symbol, get_timezone_display_name


def _load_prompt(filename: str) -> str:
    """Load a prompt file and substitute locale placeholders."""
    prompt_path = Path(__file__).parent / filename
    content = prompt_path.read_text(encoding="utf-8")

    # Substitute locale placeholders
    content = content.replace("{currency_symbol}", get_currency_symbol())
    content = content.replace("{timezone_name}", get_timezone_display_name())

    return content


# Load prompts at import time
USER_SYSTEM_PROMPT = _load_prompt("user_system.prompt.md")
ADMIN_SYSTEM_PROMPT = _load_prompt("admin_system.prompt.md")
