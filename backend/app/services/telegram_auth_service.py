"""Telegram authentication service: initData verification and user management."""

import hashlib
import hmac
import time
from typing import Optional


def verify_initdata(init_data: str, bot_token: str, max_age_seconds: int = 120) -> Optional[dict]:
    """
    Verify Telegram Mini App initData signature using HMAC-SHA256.
    
    ## Implementation TODO
    - Parse init_data string (URL-encoded key=value pairs)
    - Extract 'hash' parameter (HMAC-SHA256 signature)
    - Compute HMAC-SHA256(check_string, secret_key) where:
      - secret_key = HMAC-SHA256("WebAppData", bot_token)
      - check_string = sorted key=value pairs (excluding 'hash')
    - Compare computed hash with provided hash (constant-time comparison)
    - Validate 'auth_date' is fresh (< max_age_seconds)
    - Extract and return user data: { "telegram_id": int, "auth_date": int, ...}
    - Raise exception or return None if validation fails
    
    ## Arguments
    - init_data: URL-encoded string from Telegram WebApp
    - bot_token: Telegram bot token (for HMAC secret derivation)
    - max_age_seconds: Maximum age of auth_date (default 120 seconds per spec)
    
    ## Returns
    - Dict with extracted user data (telegram_id, first_name, etc.) if valid
    - None if validation fails
    
    ## Specification Reference
    specs/001-seamless-telegram-auth/research.md#initData-verification
    """
    # TODO: implement HMAC-SHA256 verification
    # TODO: implement auth_date freshness check
    # TODO: implement user data extraction
    # Sample skeleton:
    # 1. Parse init_data query string
    # 2. Extract hash and auth_date
    # 3. Verify hash matches HMAC-SHA256(check_string, derived_key)
    # 4. Verify auth_date is fresh
    # 5. Return user data dict or raise/return None
    raise NotImplementedError("verify_initdata not yet implemented")


def get_or_create_user(telegram_id: int, init_data_dict: dict) -> tuple[bool, dict]:
    """
    Get or create SOSenkiUser by telegram_id.
    
    ## Implementation TODO
    - Query database for SOSenkiUser with matching telegram_id
    - If user exists: return (linked=True, user_object)
    - If not found: create TelegramUserCandidate (pending admin approval)
      - Store telegram_id, user_data from initData
      - Return (linked=False, candidate_request_form)
    
    ## Arguments
    - telegram_id: Verified Telegram user ID from initData
    - init_data_dict: Parsed user data from verify_initdata
    
    ## Returns
    - Tuple: (is_linked: bool, data_dict: dict)
      - If linked: (True, {"user_id": ..., "role": ..., ...})
      - If unlinked: (False, {"form": {...}})
    
    ## Database Models Reference
    specs/001-seamless-telegram-auth/data-model.md
    """
    # TODO: implement database query/create logic
    # TODO: use SQLAlchemy models from backend/app/models/
    raise NotImplementedError("get_or_create_user not yet implemented")
