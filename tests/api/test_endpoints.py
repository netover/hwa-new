"""
API Endpoints Tests for Health Checks.

This module tests the /health API endpoints for functionality, ensuring they
respond correctly and reflect the state of their dependencies.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import the specific routers we want to test
from resync.api.health import config_router, health_router


@pytest.fixture
def client():
    """
    Create a TestClient instance using a minimal FastAPI app.
    This app only includes the health check router, completely bypassing the
    main application's complex startup lifecycle.
    """
    test_app = FastAPI()
    test_app.include_router(health_router)
    test_app.include_router(config_router)

    with TestClient(test_app) as c:
        yield c


class TestHealthEndpoint:
    """Test /health endpoint functionality."""

    @patch('resync.api.health.get_container')
    @patch('resync.api.health.agent_manager')
    def test_health_check_basic(self, mock_agent_manager, mock_get_container, client):
        """Test basic health check functionality for the core app."""
        # Mock the dependencies called by the endpoint
        mock_agent_manager.agents = {"test-agent": "foo"}
        mock_container = MagicMock()
        # IMPORTANT: container.get() is an async method, so it must be an AsyncMock
        mock_container.get = AsyncMock()
        mock_get_container.return_value = mock_container

        response = client.get("/health/core")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "agent_manager" in data["components"]

    @patch('resync.api.health.agent_manager', new_callable=MagicMock)
    @patch('resync.api.health.circuit_breaker_manager', new_callable=MagicMock)
    def test_health_check_with_dependencies(self, mock_circuit_breaker_manager, mock_agent_manager, client):
        """Test health check with dependency verification for external services."""
        # Mock the objects and their methods as they are used in the endpoint
        mock_agent_manager.tws_client.ping = AsyncMock(return_value=None)
        mock_circuit_breaker_manager.get_all_metrics.return_value = {}

        response = client.get("/health/services")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["components"]["tws_client"] == "reachable"

    @patch('resync.api.health.agent_manager', new_callable=MagicMock)
    @patch('resync.api.health.circuit_breaker_manager', new_callable=MagicMock)
    def test_health_check_dependency_failure(self, mock_circuit_breaker_manager, mock_agent_manager, client):
        """Test health check when a dependency fails."""
        mock_agent_manager.tws_client.ping = AsyncMock(side_effect=Exception("TWS unavailable"))
        mock_circuit_breaker_manager.get_all_metrics.return_value = {}

        response = client.get("/health/services")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert "error: TWS unavailable" in data["components"]["tws_client"]
