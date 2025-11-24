"""Tests for logging service configuration."""

import logging
import tempfile
from pathlib import Path

from src.services.logging import setup_server_logging


class TestServerLogging:
    """Test server logging configuration."""

    def test_setup_server_logging_creates_log_directory(self) -> None:
        """Verify setup_server_logging creates logs directory if missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test_logs" / "server.log"

            # Directory should not exist yet
            assert not log_file.parent.exists()

            # Setup logging
            setup_server_logging(str(log_file))

            # Directory should now exist
            assert log_file.parent.exists()

    def test_setup_server_logging_creates_handlers(self) -> None:
        """Verify setup_server_logging creates both stdout and file handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "server.log"

            # Clear existing handlers
            root_logger = logging.getLogger()
            root_logger.handlers.clear()

            setup_server_logging(str(log_file))

            # Should have 2 handlers (stdout + file)
            assert len(root_logger.handlers) == 2

    def test_setup_server_logging_sets_info_level(self) -> None:
        """Verify setup_server_logging sets log level to INFO."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "server.log"

            setup_server_logging(str(log_file))

            root_logger = logging.getLogger()
            assert root_logger.level == logging.INFO

    def test_setup_server_logging_handler_levels(self) -> None:
        """Verify both handlers are set to INFO level."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "server.log"

            root_logger = logging.getLogger()
            root_logger.handlers.clear()

            setup_server_logging(str(log_file))

            for handler in root_logger.handlers:
                assert handler.level == logging.INFO

    def test_setup_server_logging_writes_to_file(self) -> None:
        """Verify setup_server_logging writes log messages to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "server.log"

            root_logger = logging.getLogger()
            root_logger.handlers.clear()

            setup_server_logging(str(log_file))

            # Log a test message
            test_logger = logging.getLogger("test.module")
            test_message = "Test log message"
            test_logger.info(test_message)

            # Verify file exists and contains message
            assert log_file.exists()
            log_contents = log_file.read_text()
            assert test_message in log_contents

    def test_setup_server_logging_formatter_has_timestamp(self) -> None:
        """Verify log formatter includes ISO timestamps."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "server.log"

            root_logger = logging.getLogger()
            root_logger.handlers.clear()

            setup_server_logging(str(log_file))

            # Log a test message
            test_logger = logging.getLogger("test.timestamp")
            test_logger.info("Timestamp test")

            # Verify ISO format timestamp in log
            log_contents = log_file.read_text()
            # ISO format: [YYYY-MM-DD HH:MM:SS]
            assert "[202" in log_contents  # Year starts with 202x

    def test_setup_server_logging_formatter_includes_logger_name(self) -> None:
        """Verify log formatter includes logger name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "server.log"

            root_logger = logging.getLogger()
            root_logger.handlers.clear()

            setup_server_logging(str(log_file))

            # Log with specific logger name
            test_logger = logging.getLogger("custom.logger")
            test_logger.info("Test message")

            # Verify logger name in output
            log_contents = log_file.read_text()
            assert "custom.logger" in log_contents

    def test_setup_server_logging_formatter_includes_level(self) -> None:
        """Verify log formatter includes log level."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "server.log"

            root_logger = logging.getLogger()
            root_logger.handlers.clear()

            setup_server_logging(str(log_file))

            # Log at different levels
            test_logger = logging.getLogger("test.level")
            test_logger.info("Info message")
            test_logger.warning("Warning message")

            log_contents = log_file.read_text()
            assert "INFO" in log_contents
            assert "WARNING" in log_contents

    def test_setup_server_logging_removes_existing_handlers(self) -> None:
        """Verify setup_server_logging clears existing handlers to avoid duplicates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "server.log"

            root_logger = logging.getLogger()

            # Add a dummy handler
            dummy_handler = logging.StreamHandler()
            root_logger.addHandler(dummy_handler)
            initial_count = len(root_logger.handlers)
            assert initial_count >= 1

            # Setup logging (should clear and recreate)
            setup_server_logging(str(log_file))

            # Should have exactly 2 handlers (not 3+)
            assert len(root_logger.handlers) == 2
            assert dummy_handler not in root_logger.handlers
