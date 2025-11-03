"""Pydantic schemas for Mini App authentication."""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class InitDataRequest(BaseModel):
    """Request body for POST /miniapp/auth."""

    init_data: str = Field(..., description="Telegram Mini App initData string")


class UserResponse(BaseModel):
    """Linked user response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="User UUID")
    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    roles: list[str] = Field(default=["User"])


class RequestFormResponse(BaseModel):
    """Request form for unlinked user."""

    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    note: Optional[str] = None


class MiniAppAuthResponse(BaseModel):
    """Response from POST /miniapp/auth."""

    linked: bool = Field(..., description="Whether user is linked to SOSenki")
    user: Optional[UserResponse] = None
    request_form: Optional[RequestFormResponse] = None
