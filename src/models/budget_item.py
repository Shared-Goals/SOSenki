"""Budget item ORM model for expense categorization and allocation strategies."""

from decimal import Decimal
from enum import Enum

from sqlalchemy import Enum as SQLEnum, ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, BaseModel


class AllocationStrategy(str, Enum):
    """Strategy for allocating expense costs among residents."""

    PROPORTIONAL = "proportional"  # By property share weight
    FIXED_FEE = "fixed_fee"  # Equal split
    USAGE_BASED = "usage_based"  # Based on meter readings
    NONE = "none"  # No allocation (informational only)


class BudgetItem(Base, BaseModel):
    """Model representing a budget item for expense categorization.

    Defines how to allocate specific expense types among property owners.
    """

    __tablename__ = "budget_items"

    # Foreign keys
    service_period_id: Mapped[int] = mapped_column(
        ForeignKey("service_periods.id"),
        nullable=False,
        index=True,
        comment="Associated service/billing period",
    )

    # Budget details
    expense_type: Mapped[str] = mapped_column(
        nullable=False,
        comment="Type of expense (e.g., utilities, repairs, common area maintenance)",
    )
    allocation_strategy: Mapped[AllocationStrategy] = mapped_column(
        SQLEnum(AllocationStrategy),
        nullable=False,
        default=AllocationStrategy.NONE,
        comment="Strategy for allocating costs among residents",
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Total budgeted or actual amount for this expense type",
    )

    # Relationships
    service_period: Mapped["ServicePeriod"] = relationship(  # noqa: F821
        "ServicePeriod",
        back_populates="budget_items",
        foreign_keys=[service_period_id],
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_period_type", "service_period_id", "expense_type"),
        Index("idx_period_strategy", "service_period_id", "allocation_strategy"),
    )

    def __repr__(self) -> str:
        return (
            f"<BudgetItem(id={self.id}, period_id={self.service_period_id}, "
            f"type={self.expense_type}, strategy={self.allocation_strategy}, amount={self.total_amount})>"
        )


__all__ = ["BudgetItem", "AllocationStrategy"]
