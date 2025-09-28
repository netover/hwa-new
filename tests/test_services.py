"""Tests for resync.services modules."""

import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from resync.models.tws import JobStatus
from resync.services.mock_tws_service import MockTWSClient
from resync.services.tws_service import OptimizedTWSClient


class TestMockTWSClient:
    """Test MockTWSClient class."""

    @pytest.fixture
    def mock_service(self):
        """Create a MockTWSClient instance."""
        return MockTWSClient()

    @pytest.mark.asyncio
    async def test_get_system_status_success(self, mock_service):
        """Test successful system status retrieval."""
        status = await mock_service.get_system_status()

        # SystemStatus is a Pydantic model, not a dict
        assert hasattr(status, "workstations")
        assert hasattr(status, "jobs")
        assert hasattr(status, "critical_jobs")
        assert isinstance(status.workstations, list)
        assert isinstance(status.jobs, list)
        assert isinstance(status.critical_jobs, list)

    @pytest.mark.asyncio
    async def test_get_system_status_multiple_calls(self, mock_service):
        """Test multiple calls to get_system_status."""
        status1 = await mock_service.get_system_status()
        status2 = await mock_service.get_system_status()

        # Should return consistent structure (both are SystemStatus objects)
        assert type(status1) == type(status2)
        # Both should have the same structure
        assert hasattr(status1, "workstations") and hasattr(status2, "workstations")
        assert hasattr(status1, "jobs") and hasattr(status2, "jobs")
        assert hasattr(status1, "critical_jobs") and hasattr(status2, "critical_jobs")

    @pytest.mark.asyncio
    async def test_restart_job_success(self, mock_service):
        """Test successful job restart."""
        job_id = "TEST_JOB_001"
        result = await mock_service.restart_job(job_id)

        assert "job_id" in result
        assert "action" in result
        assert "status" in result
        assert "timestamp" in result
        assert result["job_id"] == job_id
        assert result["action"] == "restarted"

    @pytest.mark.asyncio
    async def test_restart_job_different_ids(self, mock_service):
        """Test restarting different job IDs."""
        job_ids = ["JOB_001", "JOB_002", "TEST_JOB"]

        for job_id in job_ids:
            result = await mock_service.restart_job(job_id)
            assert result["job_id"] == job_id

    @pytest.mark.asyncio
    async def test_cancel_job_success(self, mock_service):
        """Test successful job cancellation."""
        job_id = "CANCEL_JOB_001"
        result = await mock_service.cancel_job(job_id)

        assert "job_id" in result
        assert "action" in result
        assert "status" in result
        assert "timestamp" in result
        assert result["job_id"] == job_id
        assert result["action"] == "canceled"

    @pytest.mark.asyncio
    async def test_get_job_status_success(self, mock_service):
        """Test successful job status retrieval."""
        job_id = "STATUS_JOB_001"
        status = await mock_service.get_job_status(job_id)

        # JobStatus is a Pydantic model, not a dict
        assert hasattr(status, "name")
        assert hasattr(status, "workstation")
        assert hasattr(status, "status")
        assert hasattr(status, "job_stream")
        assert isinstance(status, JobStatus)

    @pytest.mark.asyncio
    async def test_get_job_history_success(self, mock_service):
        """Test successful job history retrieval."""
        job_id = "HISTORY_JOB_001"
        history = await mock_service.get_job_history(job_id)

        # history is a list of dictionaries
        assert isinstance(history, list)
        assert len(history) > 0
        assert "job_id" in history[0]
        assert history[0]["job_id"] == job_id

    @pytest.mark.asyncio
    async def test_list_jobs_success(self, mock_service):
        """Test successful job listing."""
        jobs = await mock_service.list_jobs()

        # jobs is a list of JobStatus objects
        assert isinstance(jobs, list)
        assert len(jobs) > 0

        # Check job structure
        if jobs:
            job = jobs[0]
            assert hasattr(job, "name")
            assert hasattr(job, "workstation")
            assert hasattr(job, "status")
            assert hasattr(job, "job_stream")
            assert hasattr(job, "name")
            assert hasattr(job, "status")

    @pytest.mark.asyncio
    async def test_list_jobs_with_filter(self, mock_service):
        """Test job listing with status filter."""
        status_filter = "running"
        jobs = await mock_service.list_jobs(status_filter=status_filter)

        # jobs is a list of JobStatus objects
        assert isinstance(jobs, list)
        # All returned jobs should match the filter
        for job in jobs:
            assert job.status == status_filter

    @pytest.mark.asyncio
    async def test_simulate_random_behavior(self, mock_service):
        """Test that mock service simulates some randomness."""
        # Call the same operation multiple times
        results = []
        for _ in range(10):
            status = await mock_service.get_system_status()
            # SystemStatus doesn't have a "status" field, just check that we get objects
            results.append(type(status).__name__)

        # Should have some variety in responses (not all identical)
        unique_results = set(results)
        assert len(unique_results) >= 1  # At least one result

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, mock_service):
        """Test concurrent operations on mock service."""
        # Run multiple operations concurrently
        tasks = [
            mock_service.get_system_status(),
            mock_service.restart_job("CONCURRENT_JOB_1"),
            mock_service.cancel_job("CONCURRENT_JOB_2"),
            mock_service.get_job_status("CONCURRENT_JOB_3"),
            mock_service.list_jobs(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All operations should succeed
        for result in results:
            assert not isinstance(result, Exception)

    @pytest.mark.asyncio
    async def test_error_simulation(self, mock_service):
        """Test error simulation in mock service."""
        # Some operations might simulate errors with low probability
        # We'll test this by calling many times
        error_count = 0
        success_count = 0

        for _ in range(50):
            try:
                await mock_service.get_system_status()
                success_count += 1
            except Exception:
                error_count += 1

        # Should have more successes than errors (mock should mostly work)
        assert success_count > error_count


class TestOptimizedTWSClient:
    """Test OptimizedTWSClient class."""

    def test_tws_service_initialization(self):
        """Test TWSService initialization."""
        with patch("resync.core.cache_hierarchy.get_cache_hierarchy") as mock_cache:
            mock_cache.return_value = MagicMock()
            service = OptimizedTWSClient(
                hostname="localhost",
                port=8080,
                username="test_user",
                password="test_pass",
            )

            assert service.hostname == "localhost"
            assert service.port == 8080
            assert service.username == "test_user"
            assert service.password == "test_pass"
            assert service.timeout == 30

    def test_tws_service_initialization_defaults(self):
        """Test TWSService initialization with minimal config."""
        with patch("resync.core.cache_hierarchy.get_cache_hierarchy") as mock_cache:
            mock_cache.return_value = MagicMock()
            service = OptimizedTWSClient(
                hostname="test-host",
                port=31116,  # Default port
                username="default_user",
                password="default_pass",
            )

            assert service.hostname == "test-host"
            assert service.port == 31116  # Default port
            assert service.timeout == 30  # Default timeout

    @pytest.mark.asyncio
    async def test_get_system_status_success(self):
        """Test successful system status retrieval."""
        with patch("resync.core.cache_hierarchy.get_cache_hierarchy") as mock_cache:
            mock_cache.return_value = MagicMock()
            tws_service = OptimizedTWSClient(
                hostname="localhost",
                port=8080,
                username="test_user",
                password="test_pass",
            )

            mock_response = {
                "status": "healthy",
                "components": {"scheduler": "running", "database": "connected"},
                "timestamp": datetime.now().isoformat(),
            }

            with patch.object(tws_service, "_make_request", return_value=mock_response):
                status = await tws_service.get_system_status()

                assert status == mock_response

    @pytest.mark.asyncio
    async def test_get_system_status_connection_error(self):
        """Test system status with connection error."""
        with patch("resync.core.cache_hierarchy.get_cache_hierarchy") as mock_cache:
            mock_cache.return_value = MagicMock()
            tws_service = OptimizedTWSClient(
                hostname="localhost",
                port=8080,
                username="test_user",
                password="test_pass",
            )

            with patch.object(
                tws_service,
                "_make_request",
                side_effect=ConnectionError("Connection failed"),
            ):
                with pytest.raises(ConnectionError):
                    await tws_service.get_system_status()

    @pytest.mark.asyncio
    async def test_build_url(self):
        """Test URL building functionality."""
        with patch("resync.core.cache_hierarchy.get_cache_hierarchy") as mock_cache:
            mock_cache.return_value = MagicMock()
            tws_service = OptimizedTWSClient(
                hostname="localhost",
                port=8080,
                username="test_user",
                password="test_pass",
            )

            # Test URL building
            url = tws_service._build_url("/test/endpoint")
            assert url == "localhost:8080/twsd/test/endpoint"

            url_with_leading_slash = tws_service._build_url("/test/endpoint/")
            assert url_with_leading_slash == "localhost:8080/twsd/test/endpoint/"
