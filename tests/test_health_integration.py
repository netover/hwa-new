import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from resync.api.health import (
    health_check,
    health_check_core,
    health_check_detailed,
    health_check_live,
    health_check_ready,
)
from resync.core.health_models import ComponentHealth, ComponentType, HealthStatus


class TestHealthCheckEndpoints:
    """Test health check API endpoints."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock request object."""
        request = Mock()
        request.app.state.health_service = None
        return request

    @pytest.mark.asyncio
    async def test_health_check_endpoint_basic(self, mock_request):
        """Test basic health check endpoint."""
        # Mock health service
        mock_health_service = Mock()
        mock_health_service.perform_comprehensive_health_check = AsyncMock(return_value=Mock(
            overall_status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            components={"test": ComponentHealth("test", ComponentType.DATABASE, HealthStatus.HEALTHY)},
            performance_metrics={"total_check_time_ms": 100}
        ))
        mock_request.app.state.health_service = mock_health_service

        response = await health_check(mock_request)

        assert response.status_code == 200
        data = json.loads(response.body)
        assert data["status"] == "healthy"
        assert "🟢" in data["status_indicator"]
        assert "components" in data
        assert "summary" in data

    @pytest.mark.asyncio
    async def test_health_check_endpoint_unhealthy(self, mock_request):
        """Test health check endpoint with unhealthy status."""
        # Mock health service with unhealthy result
        mock_health_service = Mock()
        mock_health_service.perform_comprehensive_health_check = AsyncMock(return_value=Mock(
            overall_status=HealthStatus.UNHEALTHY,
            timestamp=datetime.now(),
            components={"test": ComponentHealth("test", ComponentType.DATABASE, HealthStatus.UNHEALTHY)},
            performance_metrics={"total_check_time_ms": 100}
        ))
        mock_request.app.state.health_service = mock_health_service

        response = await health_check(mock_request)

        assert response.status_code == 503  # Service Unavailable for unhealthy
        data = json.loads(response.body)
        assert data["status"] == "unhealthy"
        assert "🔴" in data["status_indicator"]

    @pytest.mark.asyncio
    async def test_health_check_core_endpoint(self, mock_request):
        """Test core health check endpoint."""
        # Mock health service
        mock_health_service = Mock()
        mock_health_service.perform_core_health_check = AsyncMock(return_value=Mock(
            overall_status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            components={"database": ComponentHealth("database", ComponentType.DATABASE, HealthStatus.HEALTHY)},
            performance_metrics={"total_check_time_ms": 50}
        ))
        mock_request.app.state.health_service = mock_health_service

        response = await health_check_core(mock_request)

        assert response.status_code == 200
        data = json.loads(response.body)
        assert data["status"] == "healthy"
        assert "core_components" in data
        assert data["core_components"]["database"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_detailed_endpoint(self, mock_request):
        """Test detailed health check endpoint."""
        # Mock health service
        mock_health_service = Mock()
        mock_health_service.perform_comprehensive_health_check = AsyncMock(return_value=Mock(
            overall_status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            components={"test": ComponentHealth("test", ComponentType.DATABASE, HealthStatus.HEALTHY)},
            performance_metrics={"total_check_time_ms": 100},
            message="All systems operational"
        ))
        mock_health_service.get_health_history = Mock(return_value=[
            Mock(timestamp=datetime.now(), overall_status=HealthStatus.HEALTHY, component_changes={})
        ])
        mock_request.app.state.health_service = mock_health_service

        response = await health_check_detailed(mock_request)

        assert response.status_code == 200
        data = json.loads(response.body)
        assert data["status"] == "healthy"
        assert "detailed_status" in data
        assert "history" in data
        assert "alerts" in data

    @pytest.mark.asyncio
    async def test_health_check_ready_endpoint_healthy(self, mock_request):
        """Test readiness probe endpoint with healthy status."""
        # Mock health service
        mock_health_service = Mock()
        mock_health_service.is_healthy = Mock(return_value=True)
        mock_request.app.state.health_service = mock_health_service

        response = await health_check_ready(mock_request)

        assert response.status_code == 200
        data = json.loads(response.body)
        assert data["ready"] is True
        assert data["status"] == "ready"

    @pytest.mark.asyncio
    async def test_health_check_ready_endpoint_unhealthy(self, mock_request):
        """Test readiness probe endpoint with unhealthy status."""
        # Mock health service
        mock_health_service = Mock()
        mock_health_service.is_healthy = Mock(return_value=False)
        mock_request.app.state.health_service = mock_health_service

        response = await health_check_ready(mock_request)

        assert response.status_code == 503  # Service Unavailable
        data = json.loads(response.body)
        assert data["ready"] is False
        assert data["status"] == "not_ready"

    @pytest.mark.asyncio
    async def test_health_check_live_endpoint(self, mock_request):
        """Test liveness probe endpoint."""
        # Mock health service
        mock_health_service = Mock()
        mock_health_service.is_healthy = Mock(return_value=True)
        mock_request.app.state.health_service = mock_health_service

        response = await health_check_live(mock_request)

        assert response.status_code == 200
        data = json.loads(response.body)
        assert data["alive"] is True
        assert data["status"] == "alive"

    @pytest.mark.asyncio
    async def test_health_check_no_service(self, mock_request):
        """Test health check when service is not available."""
        mock_request.app.state.health_service = None

        response = await health_check(mock_request)

        assert response.status_code == 503
        data = json.loads(response.body)
        assert data["status"] == "error"
        assert "Health check service not available" in data["message"]

    @pytest.mark.asyncio
    async def test_health_check_service_exception(self, mock_request):
        """Test health check when service raises exception."""
        # Mock health service that raises exception
        mock_health_service = Mock()
        mock_health_service.perform_comprehensive_health_check = AsyncMock(
            side_effect=Exception("Service error")
        )
        mock_request.app.state.health_service = mock_health_service

        response = await health_check(mock_request)

        assert response.status_code == 503
        data = json.loads(response.body)
        assert data["status"] == "error"
        assert "Health check failed" in data["message"]


class TestHealthCheckFormats:
    """Test different response formats for health checks."""

    @pytest.mark.asyncio
    async def test_health_check_json_format(self):
        """Test JSON response format."""
        from fastapi.testclient import TestClient

        from resync.api.health import router

        # Create test client
        client = TestClient(router)

        # Mock the health service
        with patch('resync.api.health.get_health_check_service') as mock_get_service:
            mock_service = Mock()
            mock_service.perform_comprehensive_health_check = AsyncMock(return_value=Mock(
                overall_status=HealthStatus.HEALTHY,
                timestamp=datetime.now(),
                components={"test": ComponentHealth("test", ComponentType.DATABASE, HealthStatus.HEALTHY)},
                performance_metrics={"total_check_time_ms": 100}
            ))
            mock_get_service.return_value = mock_service

            response = client.get("/")

            assert response.status_code == 200
            assert response.headers["content-type"] == "application/json"

            data = response.json()
            assert "status" in data
            assert "status_indicator" in data
            assert "components" in data
            assert "summary" in data
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_health_check_human_readable_format(self):
        """Test human-readable response format."""
        from fastapi.testclient import TestClient

        from resync.api.health import router

        client = TestClient(router)

        with patch('resync.api.health.get_health_check_service') as mock_get_service:
            mock_service = Mock()
            mock_service.perform_comprehensive_health_check = AsyncMock(return_value=Mock(
                overall_status=HealthStatus.DEGRADED,
                timestamp=datetime.now(),
                components={
                    "database": ComponentHealth("database", ComponentType.DATABASE, HealthStatus.HEALTHY),
                    "redis": ComponentHealth("redis", ComponentType.REDIS, HealthStatus.DEGRADED, message="Connection timeout")
                },
                performance_metrics={"total_check_time_ms": 150}
            ))
            mock_get_service.return_value = mock_service

            response = client.get("/")

            data = response.json()

            # Check human-readable indicators
            assert "🟢" in data["status_indicator"] or "🟡" in data["status_indicator"]
            assert data["status"] == "degraded"

            # Check component details are readable
            assert "database" in data["components"]
            assert "redis" in data["components"]
            assert data["components"]["redis"]["status"] == "degraded"
            assert "timeout" in data["components"]["redis"]["message"].lower()


class TestHealthCheckIntegration:
    """Integration tests for health check system."""

    @pytest.mark.asyncio
    async def test_health_check_service_lifecycle(self):
        """Test health check service lifecycle integration."""
        from resync.core.health_service import get_health_check_service

        # Get service instance
        service = get_health_check_service()
        assert service is not None

        # Test service is working
        result = await service.perform_comprehensive_health_check()
        assert result is not None
        assert result.overall_status in HealthStatus
        assert len(result.components) > 0

    @pytest.mark.asyncio
    async def test_health_check_monitoring_integration(self):
        """Test health check monitoring integration."""
        from resync.core.health_service import get_health_check_service

        service = get_health_check_service()

        # Start monitoring
        await service.start_monitoring()
        assert service._is_monitoring is True

        # Wait a bit for monitoring to collect data
        await asyncio.sleep(2)

        # Check that cache has been populated
        assert len(service.component_cache) > 0

        # Stop monitoring
        await service.stop_monitoring()
        assert service._is_monitoring is False

    @pytest.mark.asyncio
    async def test_health_check_configuration_integration(self):
        """Test health check configuration integration."""
        from resync.core.health_service import get_health_check_service

        service = get_health_check_service()

        # Verify configuration is loaded
        assert service.config is not None
        assert service.config.enabled is True
        assert service.config.check_interval_seconds > 0
        assert service.config.timeout_seconds > 0

        # Test configuration affects behavior
        original_timeout = service.config.timeout_seconds
        service.config.timeout_seconds = 0.001  # Very short timeout

        result = await service.perform_comprehensive_health_check()

        # Should handle timeout gracefully
        assert result is not None
        assert result.overall_status in HealthStatus

        # Restore original timeout
        service.config.timeout_seconds = original_timeout


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
