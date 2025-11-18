"""Transaction type enumeration for payment and expense categorization."""

from enum import Enum


class TransactionType(str, Enum):
    """Transaction type classification for accounting.

    - CONTRIBUTION: User payment to account (membership, fees, etc.)
    - EXPENSE: Community expense paid by member from pocket (to be reimbursed)
    - SALARY: Account payment to staff member
    - TRANSFER: Money transfer between accounts
    - SERVICE_CHARGE: Automatic charge for services (utilities, etc.)
    """

    CONTRIBUTION = "contribution"
    EXPENSE = "expense"
    SALARY = "salary"
    TRANSFER = "transfer"
    SERVICE_CHARGE = "service_charge"
