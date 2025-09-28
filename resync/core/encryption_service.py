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
        if encrypted_data.startswith("encrypted_"):
            return encrypted_data[10:]  # Remove "encrypted_" prefix
        return encrypted_data  # Return as-is if not encrypted


# Logger masking
logger = logging.getLogger(__name__)


def mask_sensitive_data_in_logs(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg"):
        msg_str = str(record.msg)
        # Replace entire lines containing password with masked version
        lines = msg_str.split("\n")
        masked_lines = []

        for line in lines:
            if "password" in line.lower():
                # Mask the entire line containing password
                masked_lines.append("*** PASSWORD LOG ENTRY MASKED ***")
            else:
                masked_lines.append(line)

        record.msg = "\n".join(masked_lines)
    return True


logging.getLogger().addFilter(mask_sensitive_data_in_logs)
