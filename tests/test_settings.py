"""Tests for resync.settings module."""

from config.base import Settings
from resync.settings import APP_ENV, settings


class TestSettingsModule:
    """Test suite for settings module."""

    def test_app_env_default(self):
        """Test default APP_ENV value."""
        assert APP_ENV == "development"

    def test_settings_instance_type(self):
        """Test that settings is an instance of the correct class."""
        assert isinstance(settings, Settings)

    def test_settings_has_required_attributes(self):
        """Test that settings has all required attributes."""
        required_attrs = [
            "PROJECT_NAME",
            "PROJECT_VERSION",
            "BASE_DIR",
            "LLM_ENDPOINT",
            "LLM_API_KEY",
            "TWS_MOCK_MODE",
        ]

        for attr in required_attrs:
            assert hasattr(settings, attr), f"Missing attribute: {attr}"

    def test_settings_basic_functionality(self):
        """Test basic settings functionality."""
        # Test that settings object exists and has expected attributes
        assert settings.PROJECT_NAME == "Resync"
        assert settings.PROJECT_VERSION == "1.0.0"
        assert settings.TWS_ENGINE_NAME == "tws-engine"
        assert settings.BASE_DIR.exists()
        assert settings.BASE_DIR.is_dir()

    def test_settings_required_fields_empty_by_default(self):
        """Test that sensitive fields are empty by default."""
        assert settings.TWS_HOST == ""
        assert settings.TWS_USER == ""
        assert settings.TWS_PASSWORD == ""
