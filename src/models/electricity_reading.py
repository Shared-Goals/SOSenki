"""Electricity reading ORM model for tracking meter readings."""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, BaseModel


class ElectricityReading(Base, BaseModel):
    """Model representing an electricity meter reading.

    Tracks meter readings (start and end) for either a property or user
    during a billing period. Polymorphic design allows readings for both
    property-level and user-level tracking.
    """

    __tablename__ = "electricity_readings"

    # Foreign keys (nullable for polymorphic design)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
        comment="User this reading belongs to (if property_id is null)",
    )

    property_id: Mapped[int | None] = mapped_column(
        ForeignKey("properties.id"),
        nullable=True,
        index=True,
        comment="Property this reading belongs to",
    )

    # Reading data
    reading_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Meter reading value (kWh)",
    )

    reading_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Date when reading was taken",
    )

    # Relationships
    user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[user_id],
    )

    property: Mapped["Property | None"] = relationship(  # noqa: F821
        "Property",
        foreign_keys=[property_id],
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_reading_user_date", "user_id", "reading_date"),
        Index("idx_reading_property_date", "property_id", "reading_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<ElectricityReading(id={self.id}, user_id={self.user_id}, "
            f"property_id={self.property_id}, reading_value={self.reading_value}, "
            f"reading_date={self.reading_date})>"
        )


__all__ = ["ElectricityReading"]
