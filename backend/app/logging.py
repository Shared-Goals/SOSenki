"""Application logging configuration."""

import logging
import sys

from backend.app.config import settings


def configure_logging():
    """Configure application logging."""
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(settings.log_level.upper())

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level.upper())

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add handler
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger


# Initialize logger
logger = configure_logging()
