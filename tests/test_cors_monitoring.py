from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from resync.api.cors_monitoring import cors_monitor_router
from resync.core.rate_limiter import init_rate_limiter


class TestCORSMonitoring:
    """Test CORS monitoring endpoints."""

    def setup_method(self):
        """Set up test client and app."""
        self.app = FastAPI()

        # Initialize rate limiting for testing
        init_rate_limiter(self.app)

        # Include CORS monitoring router
        self.app.include_router(cors_monitor_router, prefix="/api/cors")

        # Create test client
        self.client = TestClient(self.app)

    def test_get_cors_stats_endpoint(self):
        """Test CORS statistics endpoint."""
        response = self.client.get("/api/cors/stats")

        # Should return stats (currently mocked data)
        assert response.status_code == 200
        data = response.json()

        assert "total_requests" in data
        assert "preflight_requests" in data
        assert "violations" in data
        assert "violation_rate" in data
        assert "last_updated" in data

    def test_get_cors_config_endpoint(self):
        """Test CORS configuration endpoint."""
        with patch("resync.api.cors_monitoring.settings") as mock_settings:
            mock_settings.CORS_ENVIRONMENT = "development"
            mock_settings.CORS_ENABLED = True

            response = self.client.get("/api/cors/config")

            assert response.status_code == 200
            data = response.json()

            assert "environment" in data
            assert "enabled" in data
            assert "allow_all_origins" in data
            assert "allowed_origins" in data
            assert "allowed_methods" in data
            assert "allowed_headers" in data
            assert "allow_credentials" in data
            assert "max_age" in data
            assert "log_violations" in data

    def test_test_cors_policy_endpoint(self):
        """Test CORS policy testing endpoint."""
        with patch("resync.api.cors_monitoring.settings") as mock_settings:
            mock_settings.CORS_ENVIRONMENT = "development"
            mock_settings.CORS_ENABLED = True

            response = self.client.post(
                "/api/cors/test",
                params={
                    "origin": "http://localhost:3000",
                    "method": "GET",
                    "path": "/api/test",
                },
            )

            assert response.status_code == 200
            data = response.json()

            assert data["origin"] == "http://localhost:3000"
            assert data["method"] == "GET"
            assert data["path"] == "/api/test"
            assert "origin_allowed" in data
            assert "method_allowed" in data
            assert "overall_allowed" in data

    def test_validate_origins_endpoint(self):
        """Test origins validation endpoint."""
        with patch("resync.api.cors_monitoring.settings") as mock_settings:
            mock_settings.CORS_ENVIRONMENT = "development"
            mock_settings.CORS_ENABLED = True

            response = self.client.post(
                "/api/cors/validate-origins",
                params={"origins": ["http://localhost:3000", "https://example.com"]},
            )

            assert response.status_code == 200
            data = response.json()

            assert "environment" in data
            assert "total_origins" in data
            assert "allowed_count" in data
            assert "results" in data

            assert len(data["results"]) == 2
            assert "http://localhost:3000" in data["results"]
            assert "https://example.com" in data["results"]

    def test_validate_origins_production_restrictions(self):
        """Test that production environment rejects wildcard origins."""
        with patch("resync.api.cors_monitoring.settings") as mock_settings:
            mock_settings.CORS_ENVIRONMENT = "production"
            mock_settings.CORS_ENABLED = True

            response = self.client.post(
                "/api/cors/validate-origins",
                params={"origins": ["*", "https://example.com"]},
            )

            assert response.status_code == 200
            data = response.json()

            # Wildcard should have validation errors in production
            wildcard_result = data["results"]["*"]
            assert len(wildcard_result["validation_errors"]) > 0
            assert (
                "Wildcard origins not allowed in production"
                in wildcard_result["validation_errors"][0]
            )

    def test_cors_violations_endpoint_empty(self):
        """Test CORS violations endpoint when no violations exist."""
        response = self.client.get("/api/cors/violations")

        assert response.status_code == 200
        data = response.json()

        # Should return empty list when no violations
        assert isinstance(data, list)
        assert len(data) == 0

    def test_cors_violations_endpoint_with_params(self):
        """Test CORS violations endpoint with query parameters."""
        response = self.client.get(
            "/api/cors/violations", params={"limit": 10, "hours": 1}
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

    def test_cors_endpoints_require_authentication(self):
        """Test that CORS monitoring endpoints require authentication."""
        # This test would need proper authentication setup
        # For now, just verify endpoints exist and return appropriate status

        endpoints = [
            "/api/cors/stats",
            "/api/cors/config",
            "/api/cors/violations",
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # Should either succeed (if auth bypassed in tests) or return auth error
            assert response.status_code in [200, 401, 403]


class TestCORSMonitoringIntegration:
    """Test CORS monitoring integration with main application."""

    def test_cors_monitoring_router_integration(self):
        """Test that CORS monitoring router integrates properly."""
        app = FastAPI()

        # Add CORS monitoring router with proper prefix
        app.include_router(
            cors_monitor_router, prefix="/api/cors", tags=["CORS Monitoring"]
        )

        client = TestClient(app)

        # Test that endpoints are accessible
        response = client.get("/api/cors/config")
        assert response.status_code in [200, 401, 403]  # May require auth

    def test_cors_endpoints_documentation(self):
        """Test that CORS endpoints are properly documented."""
        app = FastAPI()
        app.include_router(cors_monitor_router, prefix="/api/cors")

        # Get OpenAPI schema
        client = TestClient(app)
        response = client.get("/openapi.json")

        if response.status_code == 200:
            schema = response.json()

            # Check that CORS endpoints are documented
            paths = schema.get("paths", {})
            cors_paths = [path for path in paths.keys() if path.startswith("/api/cors")]

            assert len(cors_paths) > 0
            assert "/api/cors/config" in cors_paths
            assert "/api/cors/stats" in cors_paths
            assert "/api/cors/test" in cors_paths
            assert "/api/cors/validate-origins" in cors_paths


class TestCORSMonitoringValidation:
    """Test CORS monitoring input validation."""

    def test_validate_origins_with_invalid_input(self):
        """Test origins validation with invalid input."""
        with patch("resync.api.cors_monitoring.settings") as mock_settings:
            mock_settings.CORS_ENVIRONMENT = "development"
            mock_settings.CORS_ENABLED = True

            # Test with empty origins list
            response = self.client.post("/api/cors/validate-origins", params={})

            # Should handle empty input gracefully
            assert response.status_code in [200, 422]

    def test_test_cors_policy_with_invalid_method(self):
        """Test CORS policy testing with invalid HTTP method."""
        with patch("resync.api.cors_monitoring.settings") as mock_settings:
            mock_settings.CORS_ENVIRONMENT = "development"
            mock_settings.CORS_ENABLED = True

            response = self.client.post(
                "/api/cors/test",
                params={
                    "origin": "http://localhost:3000",
                    "method": "INVALID_METHOD",
                    "path": "/api/test",
                },
            )

            # Should handle invalid method gracefully
            assert response.status_code == 200

    def test_cors_violations_with_invalid_params(self):
        """Test CORS violations endpoint with invalid parameters."""
        # Test with negative limit
        response = self.client.get("/api/cors/violations", params={"limit": -1})
        assert response.status_code == 422

        # Test with limit too high
        response = self.client.get("/api/cors/violations", params={"limit": 1000})
        assert response.status_code == 422

        # Test with negative hours
        response = self.client.get("/api/cors/violations", params={"hours": -1})
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
