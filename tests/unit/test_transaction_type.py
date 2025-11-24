"""Tests for TransactionType enum - payment and expense categorization."""

from src.models.transaction_type import TransactionType


class TestTransactionTypeEnum:
    """Test TransactionType enumeration."""

    def test_transaction_type_contribution_value(self) -> None:
        """Verify CONTRIBUTION type has correct value."""
        assert TransactionType.CONTRIBUTION.value == "contribution"

    def test_transaction_type_expense_value(self) -> None:
        """Verify EXPENSE type has correct value."""
        assert TransactionType.EXPENSE.value == "expense"

    def test_transaction_type_salary_value(self) -> None:
        """Verify SALARY type has correct value."""
        assert TransactionType.SALARY.value == "salary"

    def test_transaction_type_transfer_value(self) -> None:
        """Verify TRANSFER type has correct value."""
        assert TransactionType.TRANSFER.value == "transfer"

    def test_transaction_type_service_charge_value(self) -> None:
        """Verify SERVICE_CHARGE type has correct value."""
        assert TransactionType.SERVICE_CHARGE.value == "service_charge"

    def test_all_transaction_types_are_strings(self) -> None:
        """Verify all transaction types are string enums."""
        for transaction_type in TransactionType:
            assert isinstance(transaction_type.value, str)

    def test_transaction_type_enum_count(self) -> None:
        """Verify correct number of transaction types exist."""
        expected_types = 5
        actual_types = len(list(TransactionType))
        assert actual_types == expected_types, (
            f"Expected {expected_types} transaction types, found {actual_types}"
        )

    def test_transaction_type_equality(self) -> None:
        """Verify transaction types can be compared."""
        assert TransactionType.CONTRIBUTION == TransactionType.CONTRIBUTION
        assert TransactionType.CONTRIBUTION != TransactionType.EXPENSE

    def test_transaction_type_from_value(self) -> None:
        """Verify transaction types can be created from string values."""
        contribution_type = TransactionType("contribution")
        assert contribution_type == TransactionType.CONTRIBUTION

    def test_transaction_type_name_attribute(self) -> None:
        """Verify transaction types have correct name attributes."""
        assert TransactionType.CONTRIBUTION.name == "CONTRIBUTION"
        assert TransactionType.EXPENSE.name == "EXPENSE"
        assert TransactionType.SALARY.name == "SALARY"
        assert TransactionType.TRANSFER.name == "TRANSFER"
        assert TransactionType.SERVICE_CHARGE.name == "SERVICE_CHARGE"
