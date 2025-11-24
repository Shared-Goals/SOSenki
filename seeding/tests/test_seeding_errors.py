"""Read-only verification tests for seeded data integrity.

These tests ONLY verify that data from Google Sheets was correctly imported.
They do NOT create, update, or delete any data.

Data-modification tests (transactions, rollbacks, connection pooling, etc.)
should be written in tests/integration/ or tests/unit/ using test_sosenki.db
for isolation.
"""

from seeding.config.seeding_config import SeedingConfig


class TestSeedingConfiguration:
    """Verify seeding configuration works (read-only tests only)."""

    def test_seeding_config_loads(self):
        """Test that seeding configuration can be loaded."""
        # Should load without error
        config = SeedingConfig.load()
        assert config is not None
        assert config.get_user_defaults() is not None
