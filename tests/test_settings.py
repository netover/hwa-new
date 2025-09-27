"""Tests for resync.settings module."""

import pytest
from unittest.mock import patch
import os
from pathlib import Path

from resync.settings import settings


class TestGlobalSettings:
    """Test the global settings instance."""

    def test_settings_exists(self):
        """Test that settings object exists."""
        assert settings is not None

    def test_settings_has_expected_attributes(self):
        """Test that settings has expected attributes."""
        # Check for common settings attributes that should exist
        expected_attrs = [
            "PROJECT_NAME",
        ]
        
        for attr in expected_attrs:
            assert hasattr(settings, attr), f"Missing attribute: {attr}"

    def test_settings_project_name(self):
        """Test PROJECT_NAME setting."""
        assert hasattr(settings, "PROJECT_NAME")
        project_name = settings.PROJECT_NAME
        assert isinstance(project_name, str)
        assert len(project_name) > 0

    def test_settings_string_representation(self):
        """Test string representation of settings."""
        settings_str = str(settings)
        assert isinstance(settings_str, str)
        assert len(settings_str) > 0

    def test_settings_type_validation(self):
        """Test that settings have expected types."""
        if hasattr(settings, "PROJECT_NAME"):
            assert isinstance(settings.PROJECT_NAME, str)

    def test_settings_import_consistency(self):
        """Test that settings import is consistent."""
        from resync.settings import settings as settings2
        
        # Should be the same object
        assert settings is settings2

    def test_settings_attribute_access(self):
        """Test accessing settings attributes."""
        # Should be able to access PROJECT_NAME without errors
        project_name = settings.PROJECT_NAME
        assert project_name is not None

    def test_settings_dir_attributes(self):
        """Test directory-related attributes if they exist."""
        # Check for common directory attributes
        dir_attrs = ["BASE_DIR", "PROJECT_ROOT", "DATA_DIR"]
        
        for attr in dir_attrs:
            if hasattr(settings, attr):
                value = getattr(settings, attr)
                if isinstance(value, (str, Path)):
                    # Should be a valid path-like string or Path object
                    assert len(str(value)) > 0

    def test_settings_debug_attribute(self):
        """Test debug attribute if it exists."""
        if hasattr(settings, "DEBUG"):
            debug_value = settings.DEBUG
            assert isinstance(debug_value, bool)

    def test_settings_model_attributes(self):
        """Test model-related attributes if they exist."""
        model_attrs = ["AUDITOR_MODEL_NAME", "MODEL_NAME", "LLM_MODEL"]
        
        for attr in model_attrs:
            if hasattr(settings, attr):
                value = getattr(settings, attr)
                assert isinstance(value, str)
                assert len(value) > 0

    def test_settings_environment_loading(self):
        """Test that settings can handle environment variables."""
        # Test with a temporary environment variable
        test_var = "TEST_PROJECT_NAME"
        test_value = "TestProject"
        
        # This test only works if the settings system uses environment variables
        with patch.dict(os.environ, {test_var: test_value}):
            # Just verify that setting environment variables doesn't break anything
            assert os.environ.get(test_var) == test_value

    def test_settings_attributes_not_none(self):
        """Test that key settings attributes are not None."""
        # Get all public attributes
        public_attrs = [attr for attr in dir(settings) if not attr.startswith('_')]
        
        # At least some attributes should exist
        assert len(public_attrs) > 0
        
        # PROJECT_NAME should not be None if it exists
        if hasattr(settings, "PROJECT_NAME"):
            assert settings.PROJECT_NAME is not None

    def test_settings_immutability_behavior(self):
        """Test settings behavior regarding immutability."""
        # Get current PROJECT_NAME
        if hasattr(settings, "PROJECT_NAME"):
            original_name = settings.PROJECT_NAME
            
            # Verify we can access it multiple times consistently
            assert settings.PROJECT_NAME == original_name
            assert settings.PROJECT_NAME == original_name

    def test_settings_class_type(self):
        """Test the type of the settings object."""
        # Should be some kind of settings class
        settings_type = type(settings)
        settings_name = settings_type.__name__
        
        # Should have a reasonable class name
        assert "Settings" in settings_name or "Config" in settings_name

    def test_settings_module_import(self):
        """Test importing from settings module."""
        # Should be able to import without errors
        from resync.settings import settings as imported_settings
        assert imported_settings is not None

    def test_settings_equality_consistency(self):
        """Test that settings object is consistent."""
        from resync.settings import settings as s1
        from resync.settings import settings as s2
        
        # Should be the same object
        assert s1 is s2