"""
Logging configuration and helper utilities.

This module provides centralized logging configuration for the entire
trading platform application.
"""

import logging
import sys
from pathlib import Path
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE


def setup_logging(
    level: str = LOG_LEVEL,
    log_to_file: bool = False,
    log_file: str = LOG_FILE
) -> logging.Logger:
    """
    Configure and return the application logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to a file in addition to console
        log_file: Path to log file if log_to_file is True

    Returns:
        Configured logger instance
    """
    # Get the root logger
    logger = logging.getLogger('trading_platform')
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the module (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f'trading_platform.{name}')


# Initialize default logger
default_logger = setup_logging()
