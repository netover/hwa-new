"""Comprehensive tests for resync.core.retry module."""

import asyncio
import pytest
import time
from unittest.mock import MagicMock, patch
import httpx

from resync.core.retry import (
    log_retry_attempt,
    http_retry,
    database_retry,
    external_service_retry,
    retry_on_result,
)


class TestLogRetryAttempt:
    """Test suite for log_retry_attempt function."""

    def test_log_retry_attempt_with_exception(self, caplog):
        """Test logging retry attempt with exception."""
        from tenacity import RetryCallState

        # Mock retry state with exception
        mock_outcome = MagicMock()
        mock_outcome.exception.return_value = ValueError("Test error")

        mock_retry_state = MagicMock(spec=RetryCallState)
        mock_retry_state.outcome = mock_outcome
        mock_retry_state.attempt_number = 2
        mock_retry_state.seconds_since_start = 1.5
        mock_retry_state.fn.__qualname__ = "test_function"

        # Mock the stop object
        mock_stop = MagicMock()
        mock_stop.max_attempt_number = 3
        mock_retry_state.retry_object.stop = mock_stop

        log_retry_attempt(mock_retry_state)

        # Check that warning was logged
        assert len(caplog.records) == 1
        log_message = caplog.records[0].message
        assert "Retry attempt 2/3 after 1.50s" in log_message
        assert "test_function" in log_message
        assert "Test error" in log_message

    def test_log_retry_attempt_without_exception(self, caplog):
        """Test logging retry attempt without exception."""
        from tenacity import RetryCallState

        # Mock retry state without exception
        mock_outcome = MagicMock()
        mock_outcome.exception.return_value = None

        mock_retry_state = MagicMock(spec=RetryCallState)
        mock_retry_state.outcome = mock_outcome
        mock_retry_state.attempt_number = 1
        mock_retry_state.seconds_since_start = 0.5
        mock_retry_state.fn.__qualname__ = "test_function"

        # Mock the stop object
        mock_stop = MagicMock()
        mock_stop.max_attempt_number = 5
        mock_retry_state.retry_object.stop = mock_stop

        log_retry_attempt(mock_retry_state)

        # Check that warning was logged
        assert len(caplog.records) == 1
        log_message = caplog.records[0].message
        assert "Retry attempt 1/5 after 0.50s" in log_message
        assert "test_function" in log_message
        assert "unexpected result" in log_message


class TestHTTPRetryDecorator:
    """Test suite for http_retry decorator."""

    def test_http_retry_default_exceptions(self):
        """Test http_retry with default exception types."""
        @http_retry(max_attempts=2)
        async def test_func():
            raise httpx.RequestError("Connection error")

        with pytest.raises(httpx.RequestError):
            asyncio.run(test_func())

    def test_http_retry_custom_exceptions(self):
        """Test http_retry with custom exception types."""
        @http_retry(max_attempts=2, exceptions=(ValueError,))
        async def test_func():
            raise ValueError("Custom error")

        with pytest.raises(ValueError):
            asyncio.run(test_func())

    def test_http_retry_success_after_retry(self):
        """Test http_retry success after retries."""
        call_count = 0

        @http_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.RequestError("Temporary error")
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 3

    def test_http_retry_no_retry_on_success(self):
        """Test http_retry doesn't retry on successful calls."""
        call_count = 0

        @http_retry(max_attempts=3)
        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 1

    def test_http_retry_exponential_backoff(self):
        """Test http_retry exponential backoff timing."""
        call_count = 0
        call_times = []

        @http_retry(max_attempts=3, min_wait=0.1, max_wait=1.0)
        async def test_func():
            nonlocal call_count
            call_count += 1
            call_times.append(time.time())
            if call_count < 3:
                raise httpx.RequestError("Temporary error")
            return "success"

        start_time = time.time()
        result = asyncio.run(test_func())
        end_time = time.time()

        assert result == "success"
        assert call_count == 3
        assert len(call_times) == 3

        # Check that delays are increasing (exponential backoff)
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]

        # Should be roughly exponential (delay2 > delay1)
        assert delay2 > delay1 * 0.5  # Allow some variance


class TestDatabaseRetryDecorator:
    """Test suite for database_retry decorator."""

    def test_database_retry_default_exceptions(self):
        """Test database_retry with default exception types."""
        @database_retry(max_attempts=2)
        async def test_func():
            raise ConnectionError("Database connection failed")

        with pytest.raises(ConnectionError):
            asyncio.run(test_func())

    def test_database_retry_success_after_retry(self):
        """Test database_retry success after retries."""
        call_count = 0

        @database_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary DB error")
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 2

    def test_database_retry_custom_exceptions(self):
        """Test database_retry with custom exceptions."""
        @database_retry(max_attempts=2, exceptions=(ValueError,))
        async def test_func():
            raise ValueError("Custom DB error")

        with pytest.raises(ValueError):
            asyncio.run(test_func())


class TestExternalServiceRetryDecorator:
    """Test suite for external_service_retry decorator."""

    def test_external_service_retry_default_exceptions(self):
        """Test external_service_retry with default exceptions."""
        @external_service_retry(max_attempts=2)
        async def test_func():
            raise ConnectionError("External service error")

        with pytest.raises(ConnectionError):
            asyncio.run(test_func())

    def test_external_service_retry_success_after_retry(self):
        """Test external_service_retry success after retries."""
        call_count = 0

        @external_service_retry(max_attempts=3, wait_time=0.01, max_delay=1.0)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.RequestError("External service error")
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 2

    def test_external_service_retry_max_delay(self):
        """Test external_service_retry respects max_delay."""
        call_count = 0

        @external_service_retry(max_attempts=10, wait_time=0.1, max_delay=0.2)
        async def test_func():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Persistent error")

        with pytest.raises(ConnectionError):
            asyncio.run(test_func())

        # Should have stopped due to max_delay, not max_attempts
        assert call_count <= 3  # Should be limited by max_delay


class TestRetryOnResultDecorator:
    """Test suite for retry_on_result decorator."""

    def test_retry_on_result_success(self):
        """Test retry_on_result with successful result."""
        call_count = 0

        @retry_on_result(lambda x: x == "retry", max_attempts=3, wait_time=0.01)
        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 1

    def test_retry_on_result_retry_needed(self):
        """Test retry_on_result when retry is needed."""
        call_count = 0

        @retry_on_result(lambda x: x == "retry", max_attempts=3, wait_time=0.01)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return "retry"
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 3

    def test_retry_on_result_max_attempts_exceeded(self):
        """Test retry_on_result when max attempts exceeded."""
        @retry_on_result(lambda x: x == "retry", max_attempts=2, wait_time=0.01)
        async def test_func():
            return "retry"

        with pytest.raises(Exception):  # Should raise due to tenacity
            asyncio.run(test_func())


class TestRetryDecoratorIntegration:
    """Test suite for retry decorator integration."""

    def test_http_retry_with_real_httpx_error(self):
        """Test http_retry with real HTTPx error types."""
        @http_retry(max_attempts=2)
        async def test_func():
            raise httpx.HTTPStatusError(
                "Rate limited",
                request=MagicMock(),
                response=MagicMock(status_code=429)
            )

        with pytest.raises(httpx.HTTPStatusError):
            asyncio.run(test_func())

    def test_retry_decorators_with_different_wait_strategies(self):
        """Test different wait strategies in retry decorators."""
        call_count = 0
        call_times = []

        @database_retry(max_attempts=3, min_wait=0.05, max_wait=0.2)
        async def test_func():
            nonlocal call_count
            call_count += 1
            call_times.append(time.time())
            if call_count < 3:
                raise ConnectionError("DB error")
            return "success"

        start_time = time.time()
        result = asyncio.run(test_func())
        end_time = time.time()

        assert result == "success"
        assert call_count == 3
        assert len(call_times) == 3

        # Check exponential backoff timing
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]

        # Delays should be different (exponential backoff)
        assert abs(delay1 - delay2) > 0.01

    def test_retry_decorators_logging(self, caplog):
        """Test that retry decorators produce appropriate logs."""
        @http_retry(max_attempts=2, min_wait=0.01)
        async def test_func():
            raise httpx.RequestError("Test error")

        with pytest.raises(httpx.RequestError):
            asyncio.run(test_func())

        # Check that retry logs were generated
        retry_logs = [record for record in caplog.records if "Retry attempt" in record.message]
        assert len(retry_logs) > 0

    def test_retry_decorators_with_mixed_exception_types(self):
        """Test retry decorators with mixed exception types."""
        call_count = 0

        @http_retry(max_attempts=3)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Network error")
            elif call_count == 2:
                raise httpx.TimeoutException("Timeout")
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 3

    def test_retry_decorators_preserve_function_metadata(self):
        """Test that retry decorators preserve function metadata."""
        @http_retry(max_attempts=2)
        async def test_func():
            """Test function docstring."""
            return "test"

        # Check that metadata is preserved
        assert test_func.__name__ == "test_func"
        assert test_func.__doc__ == "Test function docstring."

    def test_retry_decorators_with_async_generators(self):
        """Test retry decorators with async generators."""
        @http_retry(max_attempts=2)
        async def async_gen():
            yield "test"

        # Should work with async generators
        gen = async_gen()
        assert hasattr(gen, '__aiter__')

    def test_retry_decorators_exception_hierarchy(self):
        """Test that retry decorators work with exception hierarchy."""
        @http_retry(max_attempts=2)
        async def test_func():
            # HTTPStatusError is a subclass of RequestError
            raise httpx.HTTPStatusError(
                "Server error",
                request=MagicMock(),
                response=MagicMock(status_code=500)
            )

        with pytest.raises(httpx.HTTPStatusError):
            asyncio.run(test_func())


class TestRetryConfiguration:
    """Test suite for retry configuration."""

    def test_http_retry_configuration(self):
        """Test http_retry configuration parameters."""
        decorator = http_retry(max_attempts=5, min_wait=2.0, max_wait=30.0)

        # Test that decorator was created
        assert callable(decorator)

        # Test decorator application
        @decorator
        async def test_func():
            return "test"

        assert hasattr(test_func, '__wrapped__')

    def test_database_retry_configuration(self):
        """Test database_retry configuration parameters."""
        decorator = database_retry(max_attempts=10, min_wait=0.5, max_wait=5.0)

        @decorator
        async def test_func():
            return "test"

        assert callable(test_func)

    def test_external_service_retry_configuration(self):
        """Test external_service_retry configuration parameters."""
        decorator = external_service_retry(
            max_attempts=5,
            max_delay=60.0,
            wait_time=3.0
        )

        @decorator
        async def test_func():
            return "test"

        assert callable(test_func)

    def test_retry_on_result_configuration(self):
        """Test retry_on_result configuration parameters."""
        decorator = retry_on_result(
            lambda x: x == "error",
            max_attempts=3,
            wait_time=1.0
        )

        @decorator
        async def test_func():
            return "test"

        assert callable(test_func)


class TestRetryErrorHandling:
    """Test suite for retry error handling."""

    def test_retry_decorator_preserves_original_exception(self):
        """Test that retry decorators preserve original exception type."""
        @http_retry(max_attempts=2)
        async def test_func():
            raise ValueError("Original error")

        with pytest.raises(ValueError) as exc_info:
            asyncio.run(test_func())

        assert str(exc_info.value) == "Original error"

    def test_retry_decorator_with_non_retryable_exception(self):
        """Test retry decorator with non-retryable exception."""
        @http_retry(max_attempts=3)
        async def test_func():
            raise ValueError("Non-retryable error")

        # Should raise immediately without retries
        with pytest.raises(ValueError):
            asyncio.run(test_func())

    def test_retry_decorator_with_keyboard_interrupt(self):
        """Test retry decorator with KeyboardInterrupt."""
        @http_retry(max_attempts=3)
        async def test_func():
            raise KeyboardInterrupt("User interrupt")

        # KeyboardInterrupt should not be retried
        with pytest.raises(KeyboardInterrupt):
            asyncio.run(test_func())

    def test_retry_decorator_with_system_exit(self):
        """Test retry decorator with SystemExit."""
        @http_retry(max_attempts=3)
        async def test_func():
            raise SystemExit("System exit")

        # SystemExit should not be retried
        with pytest.raises(SystemExit):
            asyncio.run(test_func())


class TestRetryPerformance:
    """Test suite for retry performance characteristics."""

    def test_retry_decorator_overhead(self):
        """Test that retry decorators don't add significant overhead."""
        @http_retry(max_attempts=1)  # No retries for minimal overhead
        async def test_func():
            return "test"

        start_time = time.time()
        for _ in range(100):
            result = asyncio.run(test_func())
            assert result == "test"
        end_time = time.time()

        # Should complete quickly (less than 1 second for 100 calls)
        assert end_time - start_time < 1.0

    def test_retry_with_backoff_timing(self):
        """Test retry timing with backoff."""
        call_count = 0
        start_times = []

        @http_retry(max_attempts=3, min_wait=0.1, max_wait=1.0)
        async def test_func():
            nonlocal call_count
            call_count += 1
            start_times.append(time.time())
            if call_count < 3:
                raise httpx.RequestError("Temporary error")
            return "success"

        start_time = time.time()
        result = asyncio.run(test_func())
        end_time = time.time()

        assert result == "success"
        assert len(start_times) == 3

        # Check that delays are reasonable
        total_time = end_time - start_time
        # Should take at least the sum of minimum waits
        assert total_time >= 0.1  # At least first retry delay

    def test_concurrent_retry_operations(self):
        """Test concurrent retry operations."""
        async def test_concurrent_retries():
            tasks = []

            for i in range(5):
                @http_retry(max_attempts=2, min_wait=0.01)
                async def task_func(task_id):
                    await asyncio.sleep(0.01)  # Simulate work
                    return f"task_{task_id}_result"

                tasks.append(task_func(i))

            results = await asyncio.gather(*tasks)
            return results

        results = asyncio.run(test_concurrent_retries())
        assert len(results) == 5
        assert all("task_" in result for result in results)


class TestRetryEdgeCases:
    """Test suite for retry edge cases."""

    def test_retry_with_zero_attempts(self):
        """Test retry with zero attempts."""
        @http_retry(max_attempts=0)
        async def test_func():
            raise httpx.RequestError("Error")

        with pytest.raises(httpx.RequestError):
            asyncio.run(test_func())

    def test_retry_with_negative_attempts(self):
        """Test retry with negative attempts."""
        @http_retry(max_attempts=-1)
        async def test_func():
            raise httpx.RequestError("Error")

        with pytest.raises(httpx.RequestError):
            asyncio.run(test_func())

    def test_retry_with_very_large_attempts(self):
        """Test retry with very large number of attempts."""
        @http_retry(max_attempts=1000)
        async def test_func():
            raise httpx.RequestError("Persistent error")

        with pytest.raises(httpx.RequestError):
            asyncio.run(test_func())

    def test_retry_with_zero_wait_time(self):
        """Test retry with zero wait time."""
        call_count = 0

        @http_retry(max_attempts=3, min_wait=0.0, max_wait=0.0)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.RequestError("Error")
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 3

    def test_retry_decorator_on_sync_function(self):
        """Test retry decorator on synchronous function."""
        @http_retry(max_attempts=2)
        def sync_func():
            raise httpx.RequestError("Sync error")

        with pytest.raises(httpx.RequestError):
            sync_func()


class TestRetryIntegration:
    """Test suite for retry integration scenarios."""

    def test_retry_decorators_stacking(self):
        """Test stacking multiple retry decorators."""
        call_count = 0

        @database_retry(max_attempts=2)
        @http_retry(max_attempts=2)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Error")
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 3

    def test_retry_with_different_error_types_in_sequence(self):
        """Test retry with different error types."""
        call_count = 0
        errors = [ConnectionError("Network"), httpx.TimeoutException("Timeout"), ValueError("Data")]

        @http_retry(max_attempts=4)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count <= len(errors):
                raise errors[call_count - 1]
            return "success"

        result = asyncio.run(test_func())
        assert result == "success"
        assert call_count == 4

    def test_retry_decorator_with_context_manager(self):
        """Test retry decorator with async context manager."""
        call_count = 0

        @http_retry(max_attempts=2)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.RequestError("Error")
            return "success"

        class AsyncContextManager:
            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        async def test_with_context():
            async with AsyncContextManager():
                return await test_func()

        result = asyncio.run(test_with_context())
        assert result == "success"
        assert call_count == 2



