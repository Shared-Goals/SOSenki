"""Base model for all database models."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, Uuid

from backend.app.database import Base


class BaseModel(Base):
    """Base model with common fields for all models."""

    __abstract__ = True

    id = Column(Uuid, primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
