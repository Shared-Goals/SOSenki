"""Transaction parsing and creation utilities for database seeding.

Unified service for creating account-to-account Transaction records,
replacing dual Debit + Credit logic.
"""

import logging
from typing import Dict, List

from sqlalchemy.orm import Session

from src.models.account import Account, AccountType
from src.models.service_period import ServicePeriod
from src.models.transaction import Transaction
from src.models.user import User
from src.services.errors import DataValidationError


def get_or_create_service_period(
    session: Session, 
    period_name: str,
    start_date_str: str,
    end_date_str: str
) -> ServicePeriod:
    """Get existing service period or create new one.
    
    Args:
        session: SQLAlchemy session
        period_name: Period name (e.g., "2024-2025")
        start_date_str: Start date as DD.MM.YYYY string
        end_date_str: End date as DD.MM.YYYY string
        
    Returns:
        ServicePeriod instance
        
    Raises:
        DataValidationError: On creation failure
    """
    logger = logging.getLogger("sosenki.seeding.transactions")
    
    try:
        # Query for existing period
        period = session.query(ServicePeriod).filter(
            ServicePeriod.name == period_name
        ).first()
        
        if period:
            logger.debug(f"Found existing service period: {period_name}")
            return period
        
        # Parse dates
        from datetime import datetime as dt
        start_date = dt.strptime(start_date_str, "%d.%m.%Y").date()
        end_date = dt.strptime(end_date_str, "%d.%m.%Y").date()
        
        # Create new period
        period = ServicePeriod(
            name=period_name,
            start_date=start_date,
            end_date=end_date,
        )
        session.add(period)
        session.flush()
        
        logger.info(
            f"Created service period: {period_name} ({start_date} - {end_date})"
        )
        return period
        
    except Exception as e:
        raise DataValidationError(
            f"Failed to get or create service period '{period_name}': {e}"
        ) from e


def get_or_create_community_account(session: Session, name: str) -> Account:
    """Get existing community account or create new one.
    
    Args:
        session: SQLAlchemy session
        name: Account name (e.g., "Взносы", "Reserve")
        
    Returns:
        Account instance with account_type='community'
        
    Raises:
        DataValidationError: On creation failure
    """
    logger = logging.getLogger("sosenki.seeding.transactions")
    
    try:
        # Query for existing account
        account = session.query(Account).filter(
            Account.name == name,
            Account.account_type == AccountType.COMMUNITY
        ).first()
        
        if account:
            logger.debug(f"Found existing community account: {name}")
            return account
        
        # Create new account
        account = Account(
            name=name,
            account_type=AccountType.COMMUNITY,
        )
        session.add(account)
        session.flush()
        
        logger.info(f"Created community account: {name}")
        return account
        
    except Exception as e:
        raise DataValidationError(
            f"Failed to get or create community account '{name}': {e}"
        ) from e


def create_debit_transactions(
    session: Session,
    debit_dicts: List[Dict],
    user_map: Dict[str, User],
    period: ServicePeriod,
    default_account_name: str = "Взносы",
) -> int:
    """Create debit transactions (user account → community account).
    
    Args:
        session: SQLAlchemy session
        debit_dicts: List of dicts with owner_name, amount, debit_date, comment, account_name
        user_map: Dict mapping user names to User instances
        period: ServicePeriod to link transactions to
        default_account_name: Default community account name
        
    Returns:
        Number of transactions created
        
    Raises:
        DataValidationError: On creation failure
    """
    logger = logging.getLogger("sosenki.seeding.transactions")
    
    try:
        created_count = 0
        
        for debit_dict in debit_dicts:
            owner_name = debit_dict.pop("owner_name")
            user = user_map.get(owner_name)
            
            if not user:
                logger.warning(f"Owner not found: {owner_name}, skipping debit")
                continue
            
            if not user.account:
                logger.warning(f"No personal account for user: {owner_name}, skipping debit")
                continue
            
            # Get community account
            account_name = debit_dict.pop("account_name", None) or default_account_name
            community_account = get_or_create_community_account(session, account_name)
            
            # Create transaction: user account → community account
            transaction = Transaction(
                from_account_id=user.account.id,
                to_account_id=community_account.id,
                amount=debit_dict["amount"],
                transaction_date=debit_dict["debit_date"],
                service_period_id=period.id,
                description=debit_dict.get("comment"),
            )
            session.add(transaction)
            
            logger.info(
                f"Created debit transaction: {owner_name} → {account_name} "
                f"{debit_dict['amount']} {debit_dict['debit_date']}"
            )
            created_count += 1
        
        logger.info(f"Created {created_count} debit transactions")
        return created_count
        
    except Exception as e:
        raise DataValidationError(f"Failed to create debit transactions: {e}") from e


def create_credit_transactions(
    session: Session,
    credit_dicts: List[Dict],
    user_map: Dict[str, User],
    period: ServicePeriod,
    default_account_name: str = "Взносы",
) -> int:
    """Create credit transactions (community account → user account).
    
    Args:
        session: SQLAlchemy session
        credit_dicts: List of dicts with payer_name, amount, debit_date, expense_type, description
        user_map: Dict mapping user first names to User instances
        period: ServicePeriod to link transactions to
        default_account_name: Default community account name
        
    Returns:
        Number of transactions created
        
    Raises:
        DataValidationError: On creation failure
    """
    logger = logging.getLogger("sosenki.seeding.transactions")
    
    try:
        created_count = 0
        community_account = get_or_create_community_account(session, default_account_name)
        
        for credit_dict in credit_dicts:
            payer_name = credit_dict.pop("payer_name")
            # Extract first name for user lookup
            payer_first_word = payer_name.split()[0] if payer_name else ""
            user = user_map.get(payer_first_word)
            
            if not user:
                logger.warning(f"Payer not found: {payer_name}, skipping credit")
                continue
            
            if not user.account:
                logger.warning(f"No personal account for user: {payer_name}, skipping credit")
                continue
            
            # Create transaction: community account → user account
            # (community reimburses the person who paid from pocket)
            transaction = Transaction(
                from_account_id=community_account.id,
                to_account_id=user.account.id,
                amount=credit_dict["amount"],
                transaction_date=credit_dict["debit_date"],
                service_period_id=period.id,
                description=f"{credit_dict['expense_type']}: {credit_dict.get('description', '')}".strip(),
            )
            session.add(transaction)
            
            logger.info(
                f"Created credit transaction: {community_account.name} → {payer_name} "
                f"{credit_dict['amount']} {credit_dict['debit_date']} "
                f"({credit_dict['expense_type']})"
            )
            created_count += 1
        
        logger.info(f"Created {created_count} credit transactions")
        return created_count
        
    except Exception as e:
        raise DataValidationError(f"Failed to create credit transactions: {e}") from e


__all__ = [
    "get_or_create_service_period",
    "get_or_create_community_account",
    "create_debit_transactions",
    "create_credit_transactions",
]
