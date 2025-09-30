from __future__ import annotations

import logging
import sys


def setup_logging():
    """
    Configures basic logging for the application.
    In a real-world scenario, this would be more complex, handling different
    environments, formats, and handlers (e.g., JSON logs for production).
    """
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def log_with_correlation(
    level: int,
    message: str,
    correlation_id: str | None = None,
    component: str = "main",
    operation: str | None = None,
    error: Exception | None = None,
    **extra_fields,
) -> None:
    """
    Structured logging with correlation ID and contextual information.

    Args:
        level: Logging level (logging.INFO, logging.ERROR, etc.)
        message: Log message
        correlation_id: Correlation ID for tracing
        component: Component name (main, tws_client, etc.)
        operation: Operation being performed
        error: Exception object for error logging
        extra_fields: Additional structured fields
    """
    # Use the component name to get a specific logger instance
    logger = logging.getLogger(component)

    extra = {
        "correlation_id": correlation_id or "system",
        "component": component,
        "operation": operation,
        **extra_fields,
    }

    # The actual logging call doesn't pass 'extra' directly in basicConfig,
    # but this structure is essential for handlers that use it (like JSON formatters).
    # For basic logging, we'll format the message to include the context.
    log_message = f"[{correlation_id}] [{component}] [{operation}] {message}"

    if error:
        log_message += f" | error: {type(error).__name__}: {error}"
        logger.log(level, log_message, exc_info=error)
    else:
        logger.log(level, log_message)