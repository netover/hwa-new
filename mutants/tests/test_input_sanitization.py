"""
Tests for InputSanitizer class and related functionality.
"""

import pytest
from pathlib import Path
from resync.main import InputSanitizer


class TestInputSanitizer:
    """Test cases for InputSanitizer functionality."""

    def test_sanitize_path_valid(self):
        """Test path sanitization with valid paths."""
        # Test with string path
        result = InputSanitizer.sanitize_path("/tmp/test.txt")
        assert isinstance(result, Path)
        assert str(result).endswith("test.txt")

        # Test with Path object
        path_obj = Path("test.txt")
        result = InputSanitizer.sanitize_path(path_obj)
        assert isinstance(result, Path)

    def test_sanitize_path_invalid(self):
        """Test path sanitization with invalid paths."""
        # Test with path traversal attempt
        with pytest.raises(ValueError, match="suspicious pattern"):
            InputSanitizer.sanitize_path("../../etc/passwd")

        # Test with null bytes
        with pytest.raises(ValueError, match="suspicious pattern"):
            InputSanitizer.sanitize_path("test\x00file.txt")

        # Test with empty path
        with pytest.raises(ValueError, match="cannot be empty"):
            InputSanitizer.sanitize_path("")

    def test_sanitize_host_port_valid(self):
        """Test host:port sanitization with valid inputs."""
        # Test IPv4
        host, port = InputSanitizer.sanitize_host_port("192.168.1.1:8080")
        assert host == "192.168.1.1"
        assert port == 8080

        # Test hostname
        host, port = InputSanitizer.sanitize_host_port("localhost:3000")
        assert host == "localhost"
        assert port == 3000

    def test_sanitize_host_port_invalid(self):
        """Test host:port sanitization with invalid inputs."""
        # Test missing colon
        with pytest.raises(ValueError, match="Host:port format required"):
            InputSanitizer.sanitize_host_port("localhost")

        # Test invalid hostname
        with pytest.raises(ValueError, match="Invalid hostname format"):
            InputSanitizer.sanitize_host_port("invalid..host:8080")

        # Test port out of range
        with pytest.raises(ValueError):
            InputSanitizer.sanitize_host_port("localhost:70000")

    def test_sanitize_environment_value(self):
        """Test environment variable sanitization."""
        # Test string
        result = InputSanitizer.sanitize_environment_value("TEST_VAR", "hello", str)
        assert result == "hello"

        # Test boolean conversion
        result = InputSanitizer.sanitize_environment_value("TEST_BOOL", "true", bool)
        assert result is True

        result = InputSanitizer.sanitize_environment_value("TEST_BOOL", "0", bool)
        assert result is False

        # Test int conversion
        result = InputSanitizer.sanitize_environment_value("TEST_INT", "42", int)
        assert result == 42

        # Test float conversion
        result = InputSanitizer.sanitize_environment_value("TEST_FLOAT", "3.14", float)
        assert result == 3.14

    def test_validate_path_exists(self):
        """Test path existence validation."""
        # Create a temporary file for testing
        import tempfile
        with tempfile.NamedTemporaryFile() as tmp:
            tmp_path = Path(tmp.name)

            # Test existing file
            result = InputSanitizer.validate_path_exists(tmp_path, must_exist=True)
            assert result == tmp_path.resolve()

            # Test non-existing file
            nonexistent = Path("definitely_does_not_exist_12345.txt")
            with pytest.raises(FileNotFoundError):
                InputSanitizer.validate_path_exists(nonexistent, must_exist=True)

            # Test non-existing file with must_exist=False
            result = InputSanitizer.validate_path_exists(nonexistent, must_exist=False)
            assert result == nonexistent.resolve()


class TestPathValidation:
    """Test cases for path validation functions."""

    def test_validate_tws_host(self):
        """Test TWS host validation."""
        from resync.main import validate_tws_host
        from resync.core.exceptions import ConfigError

        # Valid host:port
        validate_tws_host("192.168.1.1:8080")  # Should not raise

        # Invalid format
        with pytest.raises(ConfigError):
            validate_tws_host("invalid-host")

    def test_validate_paths(self):
        """Test path validation."""
        from resync.main import validate_paths
        from resync.core.exceptions import ConfigError

        # This will likely fail in test environment due to missing settings
        # but tests the validation logic
        with pytest.raises(ConfigError):
            validate_paths()
