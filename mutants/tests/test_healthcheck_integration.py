"""
Integration tests for healthcheck endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from resync.main import app


class TestHealthcheckIntegration:
    """Integration tests for healthcheck endpoints."""

    def test_global_health_endpoint(self):
        """Test global health endpoint."""
        client = TestClient(app)

        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "correlation_id" in data
        assert "components" in data
        assert "subsystems" in data

        # Check subsystems
        subsystems = data["subsystems"]
        assert "core" in subsystems
        assert "infrastructure" in subsystems
        assert "services" in subsystems

    def test_core_health_endpoint(self):
        """Test core health endpoint."""
        client = TestClient(app)

        response = client.get("/health/core")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "correlation_id" in data
        assert "components" in data

    def test_infrastructure_health_endpoint(self):
        """Test infrastructure health endpoint."""
        client = TestClient(app)

        response = client.get("/health/infrastructure")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "correlation_id" in data
        assert "components" in data

    def test_services_health_endpoint(self):
        """Test services health endpoint."""
        client = TestClient(app)

        response = client.get("/health/services")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "correlation_id" in data
        assert "components" in data

    def test_di_health_endpoint(self):
        """Test DI container health endpoint."""
        client = TestClient(app)

        response = client.get("/health/di")
        assert response.status_code == 200

        data = response.json()
        assert "overall_status" in data
        assert "services" in data
        assert "timestamp" in data
        assert "correlation_id" in data

    @pytest.mark.asyncio
    async def test_config_validation_endpoint(self):
        """Test configuration validation endpoint."""
        client = TestClient(app)

        response = client.get("/config/validate")
        # This might fail in test environment due to missing config
        # but we test the endpoint structure
        data = response.json()

        # Should return some validation result
        assert isinstance(data, dict)
        assert "overall_status" in data
        assert "correlation_id" in data
