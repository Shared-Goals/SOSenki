"""normalize_audit_log_entity_type_to_lowercase

Revision ID: 0a9c93ae7c55
Revises: 001_initial_schema
Create Date: 2025-12-21 16:31:18.979918
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "0a9c93ae7c55"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Normalize entity_type values in audit_log table to lowercase.

    Changes:
    - ElectricityReading -> electricity_reading
    """
    # Update PascalCase to snake_case for consistency
    op.execute(
        "UPDATE audit_logs SET entity_type = 'electricity_reading' "
        "WHERE entity_type = 'ElectricityReading'"
    )


def downgrade() -> None:
    """Revert entity_type values to PascalCase."""
    op.execute(
        "UPDATE audit_logs SET entity_type = 'ElectricityReading' "
        "WHERE entity_type = 'electricity_reading'"
    )
