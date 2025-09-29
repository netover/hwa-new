"""Tests for resync.core.dependencies module."""

from unittest.mock import MagicMock, patch

import pytest

from resync.core.dependencies import get_tws_client
from resync.services.mock_tws_service import MockTWSClient
from resync.services.tws_service import OptimizedTWSClient


class TestDependencies:
    """Test suite for dependency injection functions."""

    def test_get_tws_client_mock_mode_enabled(self):
        """Test get_tws_client returns MockTWSClient when TWS_MOCK_MODE is True."""
        with patch("resync.core.dependencies.settings") as mock_settings:
            mock_settings.TWS_MOCK_MODE = True

            # Ensure agent_manager doesn't have a mock client initially
            with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
                mock_agent_manager._mock_tws_client = None

                client_generator = get_tws_client()
                client = next(client_generator)

                assert isinstance(client, MockTWSClient)
                assert mock_agent_manager._mock_tws_client is client

    def test_get_tws_client_mock_mode_disabled(self):
        """Test get_tws_client returns OptimizedTWSClient when TWS_MOCK_MODE is False."""
        with patch("resync.core.dependencies.settings") as mock_settings:
            mock_settings.TWS_MOCK_MODE = False

            with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
                # Mock the _get_tws_client method
                mock_client = MagicMock(spec=OptimizedTWSClient)
                mock_agent_manager._get_tws_client.return_value = mock_client

                client_generator = get_tws_client()
                client = next(client_generator)

                assert client is mock_client
                mock_agent_manager._get_tws_client.assert_called_once()

    def test_get_tws_client_singleton_mock_client(self):
        """Test that mock client is reused as singleton."""
        with patch("resync.core.dependencies.settings") as mock_settings:
            mock_settings.TWS_MOCK_MODE = True

            with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
                # First call - should create new client
                mock_agent_manager._mock_tws_client = None
                client_generator1 = get_tws_client()
                client1 = next(client_generator1)

                # Second call - should return same client
                client_generator2 = get_tws_client()
                client2 = next(client_generator2)

                assert client1 is client2
                assert mock_agent_manager._mock_tws_client is client1

    def test_get_tws_client_exception_handling(self):
        """Test error handling in get_tws_client."""
        with patch("resync.core.dependencies.settings") as mock_settings:
            mock_settings.TWS_MOCK_MODE = True

            with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
                # Simulate an error when creating the mock client
                mock_agent_manager._mock_tws_client = None
                with patch(
                    "resync.core.dependencies.MockTWSClient"
                ) as mock_client_class:
                    mock_client_class.side_effect = Exception(
                        "Mock client creation failed"
                    )

                    with pytest.raises(Exception, match="Mock client creation failed"):
                        client_generator = get_tws_client()
                        next(client_generator)

    def test_get_tws_client_logging(self, caplog):
        """Test that get_tws_client logs appropriately."""
        with patch("resync.core.dependencies.settings") as mock_settings:
            mock_settings.TWS_MOCK_MODE = True

            with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
                mock_agent_manager._mock_tws_client = None

                client_generator = get_tws_client()
                next(client_generator)

                # Just check that some logging occurred
                assert len(caplog.records) > 0

    def test_get_tws_client_real_mode_logging(self, caplog):
        """Test logging when TWS_MOCK_MODE is disabled."""
        with patch("resync.core.dependencies.settings") as mock_settings:
            mock_settings.TWS_MOCK_MODE = False

            with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
                mock_client = MagicMock(spec=OptimizedTWSClient)
                mock_agent_manager._get_tws_client.return_value = mock_client

                client_generator = get_tws_client()
                next(client_generator)

                # Should not log mock mode message
                mock_mode_logs = [
                    record
                    for record in caplog.records
                    if "TWS_MOCK_MODE is enabled" in record.message
                ]
                assert len(mock_mode_logs) == 0

    def test_get_tws_client_exception_logging(self, caplog):
        """Test that exceptions are logged properly."""
        with patch("resync.core.dependencies.settings") as mock_settings:
            mock_settings.TWS_MOCK_MODE = True

            with patch("resync.core.dependencies.agent_manager") as mock_agent_manager:
                mock_agent_manager._mock_tws_client = None
                with patch(
                    "resync.core.dependencies.MockTWSClient"
                ) as mock_client_class:
                    mock_client_class.side_effect = Exception("Test exception")

                    with pytest.raises(Exception):
                        client_generator = get_tws_client()
                        next(client_generator)

                    # Just check that logging occurred
                    assert len(caplog.records) > 0
