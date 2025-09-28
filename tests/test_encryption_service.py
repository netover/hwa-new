"""Tests for resync.core.encryption_service module."""

import logging
from unittest.mock import MagicMock

from resync.core.encryption_service import (
    EncryptionService,
    mask_sensitive_data_in_logs,
)


class TestEncryptionService:
    """Test suite for EncryptionService class."""

    def test_encrypt_basic_string(self):
        """Test basic string encryption."""
        data = "test_data"
        result = EncryptionService.encrypt(data)

        assert result == f"encrypted_{data}"
        assert result != data  # Should be different from original

    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        data = ""
        result = EncryptionService.encrypt(data)

        assert result == "encrypted_"
        assert result != data

    def test_encrypt_special_characters(self):
        """Test encrypting string with special characters."""
        data = "test@#$%^&*()_+{}|:<>?[]\\;',./"
        result = EncryptionService.encrypt(data)

        assert result == f"encrypted_{data}"
        assert result.startswith("encrypted_")

    def test_decrypt_basic_string(self):
        """Test basic string decryption."""
        encrypted_data = "encrypted_test_data"
        result = EncryptionService.decrypt(encrypted_data)

        assert result == "test_data"
        assert result != encrypted_data  # Should be different from encrypted

    def test_decrypt_empty_string(self):
        """Test decrypting empty encrypted string."""
        encrypted_data = "encrypted_"
        result = EncryptionService.decrypt(encrypted_data)

        assert result == ""
        assert result != encrypted_data

    def test_decrypt_non_encrypted_string(self):
        """Test decrypting string that doesn't have encrypted_ prefix."""
        data = "not_encrypted_data"
        result = EncryptionService.decrypt(data)

        assert result == data  # Should return original string
        assert result == data

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypt/decrypt roundtrip works correctly."""
        original_data = "sensitive_information"
        encrypted = EncryptionService.encrypt(original_data)
        decrypted = EncryptionService.decrypt(encrypted)

        assert decrypted == original_data
        assert encrypted != original_data
        assert decrypted != encrypted

    def test_encrypt_decrypt_multiple_roundtrips(self):
        """Test multiple encrypt/decrypt roundtrips."""
        test_cases = [
            "simple",
            "with spaces",
            "with@special#chars$%",
            "very_long_string_" * 100,
            "",
        ]

        for original in test_cases:
            encrypted = EncryptionService.encrypt(original)
            decrypted = EncryptionService.decrypt(encrypted)
            assert decrypted == original, f"Failed for: {original}"


class TestLogMasking:
    """Test suite for log masking functionality."""

    def test_mask_sensitive_data_in_logs_password_in_message(self):
        """Test masking password in log messages."""
        # Create a log record with password
        record = MagicMock()
        record.msg = "User logged in with password: secret123"

        # Apply the filter
        result = mask_sensitive_data_in_logs(record)

        assert result is True
        assert "password" not in record.msg
        assert "***" in record.msg
        assert "secret123" not in record.msg

    def test_mask_sensitive_data_in_logs_password_case_insensitive(self):
        """Test masking password case insensitively."""
        record = MagicMock()
        record.msg = "PASSWORD: mypassword"

        result = mask_sensitive_data_in_logs(record)

        assert result is True
        # The line should be masked
        assert "*** PASSWORD LOG ENTRY MASKED ***" in record.msg

    def test_mask_sensitive_data_in_logs_no_password(self):
        """Test that non-password messages are not modified."""
        record = MagicMock()
        original_msg = "User logged in successfully"
        record.msg = original_msg

        result = mask_sensitive_data_in_logs(record)

        assert result is True
        assert record.msg == original_msg  # Should be unchanged

    def test_mask_sensitive_data_in_logs_multiple_passwords(self):
        """Test masking multiple password occurrences."""
        record = MagicMock()
        record.msg = "password: secret1 and password: secret2"

        result = mask_sensitive_data_in_logs(record)

        assert result is True
        assert "password" not in record.msg
        assert "***" in record.msg
        assert "secret1" not in record.msg
        assert "secret2" not in record.msg

    def test_mask_sensitive_data_in_logs_empty_message(self):
        """Test masking with empty message."""
        record = MagicMock()
        record.msg = ""

        result = mask_sensitive_data_in_logs(record)

        assert result is True
        assert record.msg == ""

    def test_mask_sensitive_data_in_logs_no_msg_attribute(self):
        """Test filter with record that has no msg attribute."""
        record = MagicMock()
        # Remove msg attribute
        del record.msg

        result = mask_sensitive_data_in_logs(record)

        assert result is True  # Filter should return True to include record

    def test_logging_filter_integration(self, caplog):
        """Test that the logging filter is properly integrated."""
        # Create a logger and add our filter
        logger = logging.getLogger("test_encryption")
        logger.addFilter(mask_sensitive_data_in_logs)

        # Test logging with password
        with caplog.at_level(logging.INFO):
            logger.info("User password: secret123")

        # Check that the message was masked
        assert len(caplog.records) == 1
        assert "password" not in caplog.records[0].message
        assert "***" in caplog.records[0].message
        assert "secret123" not in caplog.records[0].message

    def test_logging_filter_no_password(self, caplog):
        """Test logging filter with non-password message."""
        logger = logging.getLogger("test_encryption_no_password")
        logger.addFilter(mask_sensitive_data_in_logs)

        with caplog.at_level(logging.INFO):
            logger.info("User logged in successfully")

        # Check that the message was not modified
        assert len(caplog.records) == 1
        assert caplog.records[0].message == "User logged in successfully"

    def test_mask_sensitive_data_in_logs_only_password_word(self):
        """Test that only the word 'password' is masked, not similar words."""
        record = MagicMock()
        record.msg = "This is a passport number: ABC123"

        result = mask_sensitive_data_in_logs(record)

        assert result is True
        # Should not be modified since it contains "passport", not "password"
        assert record.msg == "This is a passport number: ABC123"
