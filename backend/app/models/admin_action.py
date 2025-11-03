"""AdminAction model - audit log for admin decisions."""

from sqlalchemy import Column, ForeignKey, String, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum

from backend.app.models.base import BaseModel


class AdminActionType(str, enum.Enum):
    """Type of admin action."""

    ACCEPT = "accept"
    REJECT = "reject"


class AdminAction(BaseModel):
    """Audit log for admin decisions on user requests."""

    __tablename__ = "admin_action"

    request_id = Column(String(255), ForeignKey("telegram_user_candidate.id"), nullable=False)
    admin_user_id = Column(String(255), ForeignKey("sosenki_user.id"), nullable=False)
    action = Column(SQLEnum(AdminActionType), nullable=False)
    payload = Column(JSON, nullable=True)  # Additional data like assigned role
    comment = Column(String(1000), nullable=True)

    # Relationships
    # request = relationship("TelegramUserCandidate")
    # admin_user = relationship("SOSenkiUser")
