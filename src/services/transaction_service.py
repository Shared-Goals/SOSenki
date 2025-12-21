"""Transaction service for creating and managing account-to-account transactions.

Provides business logic for:
- Account frequency analysis (for smart UI ordering)
- Amount suggestion (debt roundup or last transaction)
- Description generation (searchable format)
- Transaction creation with validation
"""

import logging
import math
from decimal import Decimal

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account import Account, AccountType
from src.models.transaction import Transaction
from src.services.audit_service import AuditService
from src.services.balance_service import BalanceCalculationService
from src.services.locale_service import format_currency

logger = logging.getLogger(__name__)


class TransactionService:
    """Service for transaction creation and account analysis."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session.

        Args:
            session: AsyncSession for database operations
        """
        self.session = session
        self.balance_service = BalanceCalculationService(session)

    async def get_accounts_by_from_frequency(self) -> list[Account]:
        """Get all accounts ordered by outgoing transaction count DESC.

        Returns accounts sorted by how frequently they are used as source
        accounts in transactions. Most frequent senders appear first.

        Returns:
            List of Account objects ordered by transaction frequency
        """
        stmt = (
            select(Account, func.count(Transaction.id).label("tx_count"))
            .outerjoin(Transaction, Transaction.from_account_id == Account.id)
            .group_by(Account.id)
            .order_by(func.count(Transaction.id).desc(), Account.name.asc())
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_accounts_by_to_frequency(self, from_account_id: int) -> list[Account]:
        """Get accounts ordered by incoming transaction count from specific source DESC.

        Returns accounts sorted by how frequently they receive transactions
        from the specified source account. Most frequent recipients appear first.

        Args:
            from_account_id: Source account ID to analyze relationships for

        Returns:
            List of Account objects ordered by relationship frequency
        """
        stmt = (
            select(Account, func.count(Transaction.id).label("tx_count"))
            .outerjoin(
                Transaction,
                and_(
                    Transaction.to_account_id == Account.id,
                    Transaction.from_account_id == from_account_id,
                ),
            )
            .group_by(Account.id)
            .order_by(func.count(Transaction.id).desc(), Account.name.asc())
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def calculate_suggested_amount(self, from_account: Account, to_account: Account) -> int:
        """Calculate suggested transaction amount based on account types and history.

        Logic:
        - If OWNER → ORGANIZATION: Round debt up to nearest 5000 (e.g., 34200 → 35000)
        - Otherwise: Use last transaction amount between these accounts

        Args:
            from_account: Source account
            to_account: Destination account

        Returns:
            Suggested amount as integer (rubles)
        """
        # Handle OWNER → ORGANIZATION (debt payment)
        if (
            from_account.account_type == AccountType.OWNER
            and to_account.account_type == AccountType.ORGANIZATION
        ):
            balance = await self.balance_service.calculate_account_balance(from_account.id)
            logger.info(
                "Balance calculation for %s: balance=%.2f (organization perspective)",
                from_account.name,
                balance,
            )

            if balance > 0:
                # Positive balance = owner owes to organization (debt)
                debt = balance
                suggested = int(math.ceil(debt / 5000) * 5000)
                logger.info("Owner owes %.2f to organization, suggesting %d", debt, suggested)
                return suggested
            elif balance < 0:
                # Negative balance = owner has overpaid (credit)
                overpaid = -balance
                suggested = 5000  # Minimal suggestion for overpaid owners
                logger.info(
                    "Owner overpaid %.2f (has credit), suggesting minimal %d", overpaid, suggested
                )
                return suggested
            else:
                # Zero balance = suggest 5000
                return 5000

        # All other cases: use last transaction amount
        stmt = (
            select(Transaction.amount)
            .filter(
                Transaction.from_account_id == from_account.id,
                Transaction.to_account_id == to_account.id,
            )
            .order_by(desc(Transaction.transaction_date), desc(Transaction.id))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        last_amount = result.scalar_one_or_none()
        return int(last_amount) if last_amount else 0

    def generate_description(
        self, from_account: Account, to_account: Account, amount: Decimal
    ) -> str:
        """Generate searchable transaction description.

        Creates a standardized description that makes transactions
        easy to find in reports without requiring joins.

        Args:
            from_account: Source account
            to_account: Destination account
            amount: Transaction amount

        Returns:
            Description in format "FromName → ToName Amount"

        Example:
            "Иванов И. → Взносы 35 000 ₽"
        """
        return f"{from_account.name} → {to_account.name} {format_currency(amount)}"

    async def create_transaction(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
        description: str,
        actor_id: int | None = None,
    ) -> Transaction:
        """Create a new transaction with validation.

        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID
            amount: Transaction amount (must be positive)
            description: Transaction description
            actor_id: User ID performing the action (for audit logging)

        Returns:
            Created Transaction object

        Raises:
            ValueError: If amount is not positive or accounts don't exist
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be positive")

        # Validate accounts exist
        from_account = await self.session.get(Account, from_account_id)
        if not from_account:
            raise ValueError(f"From account {from_account_id} not found")

        to_account = await self.session.get(Account, to_account_id)
        if not to_account:
            raise ValueError(f"To account {to_account_id} not found")

        # Create transaction
        from datetime import date

        transaction = Transaction(
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            transaction_date=date.today(),
            description=description,
            budget_item_id=None,
        )

        self.session.add(transaction)
        await self.session.flush()  # Get ID without committing

        # Audit log
        await AuditService.log(
            session=self.session,
            entity_type="transaction",
            entity_id=transaction.id,
            action="create",
            actor_id=actor_id,
            changes={
                "from_account_id": from_account_id,
                "from_account_name": from_account.name,
                "to_account_id": to_account_id,
                "to_account_name": to_account.name,
                "amount": float(amount),
                "description": description,
            },
        )

        logger.info(
            "Transaction created: from=%d to=%d amount=%s description='%s'",
            from_account_id,
            to_account_id,
            amount,
            description,
        )

        return transaction

    async def get_account_by_id(self, account_id: int) -> Account | None:
        """Get account by ID.

        Args:
            account_id: Account ID to fetch

        Returns:
            Account if found, None otherwise
        """
        return await self.session.get(Account, account_id)


__all__ = ["TransactionService"]
