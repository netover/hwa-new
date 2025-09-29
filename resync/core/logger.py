"""
Standardized logging configuration for the Resync application.

This module provides consistent logging setup and utilities across all modules.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from resync.settings import settings


class ResyncFormatter(logging.Formatter):
    """Custom formatter for Resync application logs."""

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt=fmt or settings.LOG_FORMAT, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        # Add context information for better debugging
        if not hasattr(record, "module"):
            record.module = (
                record.name.split(".")[0] if "." in record.name else record.name
            )

        return super().format(record)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
) -> None:
    """
    Configure logging for the Resync application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        format_string: Custom format string
        enable_console: Enable console logging
        enable_file: Enable file logging
    """
    # Get configuration from settings or use defaults
    log_level = level or settings.LOG_LEVEL.upper()
    log_file_path = log_file or settings.LOG_FILE_PATH
    log_format = format_string or settings.LOG_FORMAT

    # Create formatter
    formatter = ResyncFormatter(log_format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, log_level))
        root_logger.addHandler(console_handler)

    # File handler
    if enable_file:
        try:
            # Ensure log directory exists
            log_path = Path(log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Use rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, log_level))
            root_logger.addHandler(file_handler)

        except (OSError, IOError) as e:
            # Fallback to console-only if file logging fails
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.ERROR)
            root_logger.addHandler(console_handler)

            # Log the error
            logging.error(f"Failed to setup file logging: {e}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: str) -> None:
    """
    Dynamically change the log level for all loggers.

    Args:
        level: New logging level
    """
    log_level = getattr(logging, level.upper())
    root_logger = logging.getLogger()

    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(log_level)

    root_logger.setLevel(log_level)


# Logging level constants for convenience
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# Standard log messages for consistency
LOG_MESSAGES = {
    "startup": "🚀 Application starting up",
    "shutdown": "🛑 Application shutting down",
    "error": "❌ Error occurred",
    "warning": "⚠️ Warning",
    "success": "✅ Success",
    "info": "ℹ️ Info",
    "debug": "🔍 Debug",
}
