import logging
import re

logger = logging.getLogger("resync.core")


def log_info(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)
