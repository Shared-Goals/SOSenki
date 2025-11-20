"""Electricity bill ORM model for tracking billing periods."""

from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, BaseModel


class ElectricityBill(Base, BaseModel):
    """Model representing an electricity bill for a user or property.

    Tracks billing amounts for either a property or user during a service period.
    Polymorphic design allows billing for both property-level and user-level tracking.
    """

    __tablename__ = "electricity_bills"

    # Foreign keys
    service_period_id: Mapped[int] = mapped_column(
        ForeignKey("service_periods.id"),
        nullable=False,
        index=True,
        comment="Associated service/billing period",
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
        comment="User this bill belongs to (if property_id is null)",
    )

    property_id: Mapped[int | None] = mapped_column(
        ForeignKey("properties.id"),
        nullable=True,
        index=True,
        comment="Property this bill belongs to",
    )

    # Bill details
    bill_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Bill amount in rubles",
    )

    comment: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Optional comment (e.g., property name when property_id not found)",
    )

    # Relationships
    service_period: Mapped["ServicePeriod"] = relationship(  # noqa: F821
        "ServicePeriod",
        foreign_keys=[service_period_id],
    )

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
        Index("idx_bill_period_user", "service_period_id", "user_id"),
        Index("idx_bill_period_property", "service_period_id", "property_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<ElectricityBill(id={self.id}, service_period_id={self.service_period_id}, "
            f"user_id={self.user_id}, property_id={self.property_id}, "
            f"bill_amount={self.bill_amount}, comment={self.comment!r})>"
        )


__all__ = ["ElectricityBill"]
