"""TelegramUserCandidate model - pending user requests."""

from sqlalchemy import Column, BigInteger, String, Enum as SQLEnum, UniqueConstraint
import enum

from backend.app.models.base import BaseModel


class CandidateStatus(str, enum.Enum):
    """Status of a pending request."""

    PENDING = "pending"
    PROCESSED = "processed"
    CANCELLED = "cancelled"


class TelegramUserCandidate(BaseModel):
    """Lightweight record for a user requesting access via Telegram."""

    __tablename__ = "telegram_user_candidate"

    telegram_id = Column(BigInteger, nullable=False, index=True)
    telegram_username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    photo_url = Column(String(512), nullable=True)
    note = Column(String(280), nullable=True)  # max 280 chars user-provided note

    status = Column(SQLEnum(CandidateStatus), default=CandidateStatus.PENDING, nullable=False)

    __table_args__ = (
        UniqueConstraint("telegram_id", name="uq_candidate_telegram_id"),
    )
