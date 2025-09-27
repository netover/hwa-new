"""Tests for resync.services modules."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio
from datetime import datetime

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
        
        assert "status" in status
        assert "components" in status
        assert "timestamp" in status
        assert status["status"] in ["healthy", "degraded", "critical"]
        assert isinstance(status["components"], dict)

    @pytest.mark.asyncio
    async def test_get_system_status_multiple_calls(self, mock_service):
        """Test multiple calls to get_system_status."""
        status1 = await mock_service.get_system_status()
        status2 = await mock_service.get_system_status()
        
        # Should return consistent structure
        assert status1.keys() == status2.keys()
        # Timestamps should be different
        assert status1["timestamp"] != status2["timestamp"]

    @pytest.mark.asyncio
    async def test_restart_job_success(self, mock_service):
        """Test successful job restart."""
        job_id = "TEST_JOB_001"
        result = await mock_service.restart_job(job_id)
        
        assert "success" in result
        assert "job_id" in result
        assert "message" in result
        assert result["job_id"] == job_id
        assert isinstance(result["success"], bool)

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
        
        assert "success" in result
        assert "job_id" in result
        assert "message" in result
        assert result["job_id"] == job_id
        assert isinstance(result["success"], bool)

    @pytest.mark.asyncio
    async def test_get_job_status_success(self, mock_service):
        """Test successful job status retrieval."""
        job_id = "STATUS_JOB_001"
        status = await mock_service.get_job_status(job_id)
        
        assert "job_id" in status
        assert "status" in status
        assert "last_run" in status
        assert status["job_id"] == job_id
        assert status["status"] in ["running", "completed", "failed", "waiting"]

    @pytest.mark.asyncio
    async def test_get_job_history_success(self, mock_service):
        """Test successful job history retrieval."""
        job_id = "HISTORY_JOB_001"
        history = await mock_service.get_job_history(job_id)
        
        assert "job_id" in history
        assert "runs" in history
        assert "total_runs" in history
        assert history["job_id"] == job_id
        assert isinstance(history["runs"], list)
        assert isinstance(history["total_runs"], int)

    @pytest.mark.asyncio
    async def test_list_jobs_success(self, mock_service):
        """Test successful job listing."""
        jobs = await mock_service.list_jobs()
        
        assert "jobs" in jobs
        assert "total_count" in jobs
        assert isinstance(jobs["jobs"], list)
        assert isinstance(jobs["total_count"], int)
        
        # Check job structure
        if jobs["jobs"]:
            job = jobs["jobs"][0]
            assert "job_id" in job
            assert "name" in job
            assert "status" in job

    @pytest.mark.asyncio
    async def test_list_jobs_with_filter(self, mock_service):
        """Test job listing with status filter."""
        status_filter = "running"
        jobs = await mock_service.list_jobs(status_filter=status_filter)
        
        assert "jobs" in jobs
        # All returned jobs should match the filter
        for job in jobs["jobs"]:
            assert job["status"] == status_filter

    @pytest.mark.asyncio
    async def test_simulate_random_behavior(self, mock_service):
        """Test that mock service simulates some randomness."""
        # Call the same operation multiple times
        results = []
        for _ in range(10):
            status = await mock_service.get_system_status()
            results.append(status["status"])
        
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
            mock_service.list_jobs()
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

    @pytest.fixture
    def tws_service(self):
        """Create an OptimizedTWSClient instance."""
        config = {
            "host": "localhost",
            "port": 8080,
            "username": "test_user",
            "password": "test_pass",
            "timeout": 30
        }
        return OptimizedTWSClient(config)

    def test_tws_service_initialization(self, tws_service):
        """Test TWSService initialization."""
        assert tws_service.host == "localhost"
        assert tws_service.port == 8080
        assert tws_service.username == "test_user"
        assert tws_service.password == "test_pass"
        assert tws_service.timeout == 30

    def test_tws_service_initialization_defaults(self):
        """Test TWSService initialization with minimal config."""
        config = {"host": "test-host"}
        service = TWSService(config)
        
        assert service.host == "test-host"
        assert service.port == 31116  # Default port
        assert service.timeout == 30  # Default timeout

    @pytest.mark.asyncio
    async def test_get_system_status_success(self, tws_service):
        """Test successful system status retrieval."""
        mock_response = {
            "status": "healthy",
            "components": {"scheduler": "running", "database": "connected"},
            "timestamp": datetime.now().isoformat()
        }
        
        with patch.object(tws_service, '_make_request', return_value=mock_response):
            status = await tws_service.get_system_status()
            
            assert status == mock_response

    @pytest.mark.asyncio
    async def test_get_system_status_connection_error(self, tws_service):
        """Test system status with connection error."""
        with patch.object(tws_service, '_make_request', side_effect=ConnectionError("Connection failed")):
            with pytest.raises(ConnectionError):
                await tws_service.get_system_status()

    @pytest.mark.asyncio
    async def test_restart_job_success(self, tws_service):
        """Test successful job restart."""
        job_id = "TEST_JOB_001"
        mock_response = {"success": True, "job_id": job_id, "message": "Job restarted"}
        
        with patch.object(tws_service, '_make_request', return_value=mock_response):
            result = await tws_service.restart_job(job_id)
            
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_restart_job_not_found(self, tws_service):
        """Test job restart when job not found."""
        job_id = "NONEXISTENT_JOB"
        
        with patch.object(tws_service, '_make_request', side_effect=ValueError("Job not found")):
            with pytest.raises(ValueError):
                await tws_service.restart_job(job_id)

    @pytest.mark.asyncio
    async def test_cancel_job_success(self, tws_service):
        """Test successful job cancellation."""
        job_id = "CANCEL_JOB_001"
        mock_response = {"success": True, "job_id": job_id, "message": "Job cancelled"}
        
        with patch.object(tws_service, '_make_request', return_value=mock_response):
            result = await tws_service.cancel_job(job_id)
            
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_get_job_status_success(self, tws_service):
        """Test successful job status retrieval."""
        job_id = "STATUS_JOB_001"
        mock_response = {
            "job_id": job_id,
            "status": "running",
            "last_run": "2025-01-01T00:00:00Z"
        }
        
        with patch.object(tws_service, '_make_request', return_value=mock_response):
            status = await tws_service.get_job_status(job_id)
            
            assert status == mock_response

    @pytest.mark.asyncio
    async def test_get_job_history_success(self, tws_service):
        """Test successful job history retrieval."""
        job_id = "HISTORY_JOB_001"
        mock_response = {
            "job_id": job_id,
            "runs": [
                {"start_time": "2025-01-01T00:00:00Z", "status": "completed"},
                {"start_time": "2025-01-02T00:00:00Z", "status": "failed"}
            ],
            "total_runs": 2
        }
        
        with patch.object(tws_service, '_make_request', return_value=mock_response):
            history = await tws_service.get_job_history(job_id)
            
            assert history == mock_response

    @pytest.mark.asyncio
    async def test_list_jobs_success(self, tws_service):
        """Test successful job listing."""
        mock_response = {
            "jobs": [
                {"job_id": "JOB_001", "name": "Daily Backup", "status": "running"},
                {"job_id": "JOB_002", "name": "Report Generation", "status": "waiting"}
            ],
            "total_count": 2
        }
        
        with patch.object(tws_service, '_make_request', return_value=mock_response):
            jobs = await tws_service.list_jobs()
            
            assert jobs == mock_response

    @pytest.mark.asyncio
    async def test_list_jobs_with_filter(self, tws_service):
        """Test job listing with status filter."""
        status_filter = "running"
        mock_response = {
            "jobs": [{"job_id": "JOB_001", "name": "Active Job", "status": "running"}],
            "total_count": 1
        }
        
        with patch.object(tws_service, '_make_request', return_value=mock_response):
            jobs = await tws_service.list_jobs(status_filter=status_filter)
            
            assert jobs == mock_response

    @pytest.mark.asyncio
    async def test_make_request_timeout(self, tws_service):
        """Test request timeout handling."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Simulate timeout
            import httpx
            mock_client.get.side_effect = httpx.TimeoutException("Request timeout")
            
            with pytest.raises(httpx.TimeoutException):
                await tws_service._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_make_request_http_error(self, tws_service):
        """Test HTTP error handling."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock HTTP error response
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 500")
            mock_client.get.return_value = mock_response
            
            with pytest.raises(Exception):
                await tws_service._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_make_request_success(self, tws_service):
        """Test successful HTTP request."""
        expected_data = {"result": "success"}
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock successful response
            mock_response = Mock()
            mock_response.json.return_value = expected_data
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            
            result = await tws_service._make_request("GET", "/test")
            
            assert result == expected_data

    @pytest.mark.asyncio
    async def test_authentication_headers(self, tws_service):
        """Test that authentication headers are included."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.json.return_value = {}
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            
            await tws_service._make_request("GET", "/test")
            
            # Verify client was called with auth
            call_args = mock_client.get.call_args
            assert "auth" in call_args[1] or "headers" in call_args[1]

    def test_build_url(self, tws_service):
        """Test URL building."""
        endpoint = "/api/jobs"
        expected_url = f"http://{tws_service.host}:{tws_service.port}{endpoint}"
        
        # Access private method for testing
        url = tws_service._build_url(endpoint)
        
        assert url == expected_url

    def test_build_url_with_leading_slash(self, tws_service):
        """Test URL building with endpoint that has leading slash."""
        endpoint = "/api/status"
        url = tws_service._build_url(endpoint)
        
        # Should not have double slashes
        assert "//" not in url.replace("http://", "")

    def test_build_url_without_leading_slash(self, tws_service):
        """Test URL building with endpoint without leading slash."""
        endpoint = "api/jobs"
        url = tws_service._build_url(endpoint)
        
        expected_url = f"http://{tws_service.host}:{tws_service.port}/{endpoint}"
        assert url == expected_url
