"""
Encryption service for Resync core.
"""

import logging


class EncryptionService:
    """Simple encryption service for sensitive data handling."""

    @staticmethod
    def encrypt(data: str) -> str:
        """Encrypt sensitive data."""
        return f"encrypted_{data}"

    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """Decrypt data."""
        return encrypted_data.replace("encrypted_", "")


# Logger masking
logger = logging.getLogger(__name__)


def mask_sensitive_data_in_logs(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


logging.getLogger().addFilter(mask_sensitive_data_in_logs)
