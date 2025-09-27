"""
Tests for the retry functionality.
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from tenacity import RetryError

from resync.core.retry import http_retry, database_retry, external_service_retry, retry_on_result


class TestRetryDecorators:
    """Test suite for retry decorators."""

    @pytest.mark.asyncio
    async def test_http_retry_success(self):
        """Test that http_retry succeeds after temporary failures."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}

        # Mock function that fails twice then succeeds
        mock_func = AsyncMock(side_effect=[
            httpx.RequestError("Connection error"),
            httpx.RequestError("Timeout error"),
            mock_response
        ])

        @http_retry(max_attempts=3)
        async def test_func():
            return await mock_func()

        result = await test_func()
        
        # Should have been called exactly 3 times
        assert mock_func.call_count == 3
        # Should return the successful response
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_http_retry_failure(self):
        """Test that http_retry gives up after max attempts."""
        # Mock function that always fails
        mock_func = AsyncMock(side_effect=httpx.RequestError("Connection error"))

        @http_retry(max_attempts=3)
        async def test_func():
            return await mock_func()

        # Should raise RetryError after exhausting retries
        with pytest.raises(RetryError):
            await test_func()
        
        # Should have been called exactly 3 times
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_database_retry(self):
        """Test database_retry with a temporary database error."""
        # Mock function that fails once then succeeds
        mock_func = AsyncMock(side_effect=[
            ConnectionError("Database connection lost"),
            {"data": "success"}
        ])

        @database_retry(max_attempts=2)
        async def test_func():
            return await mock_func()

        result = await test_func()
        
        # Should have been called exactly 2 times
        assert mock_func.call_count == 2
        # Should return the successful response
        assert result == {"data": "success"}

    @pytest.mark.asyncio
    async def test_external_service_retry(self):
        """Test external_service_retry with a rate limit error."""
        # Mock function that fails with rate limit then succeeds
        mock_func = AsyncMock(side_effect=[
            httpx.HTTPStatusError(
                "Rate limited",
                request=MagicMock(),
                response=MagicMock(status_code=429)
            ),
            {"data": "success"}
        ])

        @external_service_retry(max_attempts=2, wait_time=0.1)
        async def test_func():
            return await mock_func()

        result = await test_func()
        
        # Should have been called exactly 2 times
        assert mock_func.call_count == 2
        # Should return the successful response
        assert result == {"data": "success"}

    def test_retry_on_result(self):
        """Test retry_on_result with an undesirable result."""
        # Mock function that returns bad result twice then good result
        mock_func = MagicMock(side_effect=[
            {"status": "pending"},
            {"status": "processing"},
            {"status": "completed"}
        ])

        # Retry if status is not "completed"
        def is_not_completed(result):
            return result.get("status") != "completed"

        @retry_on_result(is_not_completed, max_attempts=3, wait_time=0.1)
        def test_func():
            return mock_func()

        result = test_func()
        
        # Should have been called exactly 3 times
        assert mock_func.call_count == 3
        # Should return the successful response
        assert result == {"status": "completed"}


@pytest.mark.asyncio
async def test_tws_client_retry_integration():
    """Integration test for TWS client with retry functionality."""
    from resync.services.tws_service import OptimizedTWSClient
    
    # Create a client with test credentials
    client = OptimizedTWSClient(
        hostname="http://test-host",
        port=8080,
        username="test",
        password="test"
    )
    
    # Mock the httpx client's request method
    with patch.object(client.client, "request") as mock_request:
        # Setup the mock to fail twice then succeed
        mock_response = MagicMock()
        mock_response.json.return_value = {"planId": "test-plan"}
        mock_response.raise_for_status = MagicMock()
        
        mock_request.side_effect = [
            httpx.RequestError("Connection refused"),
            httpx.RequestError("Timeout"),
            mock_response
        ]
        
        # Test the check_connection method which uses _api_request internally
        result = await client.check_connection()
        
        # Should have been called exactly 3 times
        assert mock_request.call_count == 3
        # Should return True as the connection check succeeded
        assert result is True
    
    # Clean up
    await client.close()
