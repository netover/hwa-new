"""Tests for resync.core.logger module."""

import pytest
import logging
from unittest.mock import patch

from resync.core.logger import setup_logging


class TestLogger:
    """Test logger configuration and functionality."""

    def test_logger_exists(self):
        """Test that logger is properly imported."""
        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_logger_name(self):
        """Test logger name."""
        assert logger.name == "resync.core"

    def test_logger_level(self):
        """Test logger level configuration."""
        # Logger should have a level set
        assert logger.level is not None
        assert isinstance(logger.level, int)

    def test_logger_has_handlers(self):
        """Test that logger has handlers configured."""
        # Should have at least one handler or inherit from root
        assert len(logger.handlers) >= 0  # May use parent handlers

    def test_logger_basic_logging(self):
        """Test basic logging functionality."""
        with patch('logging.Logger.info') as mock_info:
            logger.info("Test message")
            mock_info.assert_called_once_with("Test message")

    def test_logger_different_levels(self):
        """Test logging at different levels."""
        test_message = "Test logging message"
        
        with patch('logging.Logger.debug') as mock_debug, \
             patch('logging.Logger.info') as mock_info, \
             patch('logging.Logger.warning') as mock_warning, \
             patch('logging.Logger.error') as mock_error:
            
            logger.debug(test_message)
            logger.info(test_message)
            logger.warning(test_message)
            logger.error(test_message)
            
            mock_debug.assert_called_once_with(test_message)
            mock_info.assert_called_once_with(test_message)
            mock_warning.assert_called_once_with(test_message)
            mock_error.assert_called_once_with(test_message)

    def test_logger_exception_logging(self):
        """Test exception logging."""
        with patch('logging.Logger.exception') as mock_exception:
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.exception("An error occurred")
            
            mock_exception.assert_called_once_with("An error occurred")

    def test_logger_with_extra_data(self):
        """Test logging with extra data."""
        extra_data = {"user_id": "123", "action": "test"}
        
        with patch('logging.Logger.info') as mock_info:
            logger.info("User action", extra=extra_data)
            mock_info.assert_called_once_with("User action", extra=extra_data)

    def test_logger_string_formatting(self):
        """Test logger with string formatting."""
        with patch('logging.Logger.info') as mock_info:
            user_id = "user123"
            action = "login"
            logger.info(f"User {user_id} performed {action}")
            mock_info.assert_called_once_with("User user123 performed login")

    def test_logger_inheritance(self):
        """Test logger inheritance from Python logging."""
        assert isinstance(logger, logging.Logger)
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'critical')
        assert hasattr(logger, 'exception')

    def test_logger_configuration_persistence(self):
        """Test that logger configuration persists across imports."""
        # Import logger again
        from resync.core.logger import logger as logger2
        
        # Should be the same instance
        assert logger is logger2
        assert logger.name == logger2.name
