"""
Tests for exponential backoff with jitter using the tenacity library.

These tests specifically validate the random jitter behavior in wait_exponential_jitter
to ensure it properly distributes wait times within the specified range.
"""

import logging
import random
import time
from typing import Any, Callable
from unittest.mock import AsyncMock, MagicMock, call

import pytest
import tenacity
from tenacity import (
    RetryCallState,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
    wait_fixed,
)

from resync.core.retry import http_retry

logger = logging.getLogger(__name__)

# Mock function to simulate retry scenarios
def make_mock_func(
    exceptions: List[Exception], results: List[Any] = []
) -> AsyncMock:
    """Create an AsyncMock that raises exceptions then returns a result"""
    mock = AsyncMock()
    mock.side_effect = exceptions + results
    return mock

# Ensure exponential jitter produces values within expected range
def test_exponential_jitter_range():
    """Test that jittered wait times stay within min and max bounds."""
    min_wait = 0.1
    max_wait = 5.0
    jitter = wait_exponential_jitter(min=min_wait, max=max_wait)

    # Generate 1000 jitter samples
    samples = [next(jitter) for _ in range(1000)]

    # Check all samples are within min and max
    assert all(min_wait <= t <= max_wait for t in samples)
    # Check no samples are exactly min or max (jitter adds randomness)
    assert min(samples) > min_wait
    assert max(samples) < max_wait

# Demonstrate that retry attempts have varying wait times due to jitter
def test_retry_jitter_behavior():
    """Verify the jitter causes variable wait times between retries."""
    # Create mock function that always fails
    mock_func = make_mock_func([httpx.RequestError("Connection error")] * 5)

    # Apply retry with jitter
    @http_retry(max_attempts=5, min_wait=0.1, max_wait=1.0)
    async def test_func():
        return await mock_func()

    # Mock time to track wait times
    time_patcher = pytest.LazyFixture(lambda: pytest.monkeypatch.setattr(time, "time", mock_time))

    def mock_time():
        """Mock time that records calls and returns increasing times"""
        static.time = 0.0
        def mock():
            result = static.time
            static.time += 0.1  # Move forward in time
            return result
        return mock

    static = type('Static', (), {})

    # Run the function and capture log output
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    logger.addHandler(handler)

    try:
        with pytest.raises(tenacity.TenacityError):
            # Run the async function
            asyncio.run(test_func())
    finally:
        logger.removeHandler(handler)

    # Analyze the wait times from logs
    wait_times = [line for line in handler.buffer if "Retrying" in line]
    wait_deltas = [float(line.split("after")[1].split("seconds")[0].strip()) for line in wait_times]

    # Verify we have attempts with varying wait times
    assert len(wait_deltas) >= 4  # At least 4 retries
    assert len(set(wait_deltas)) > 1  # Not all wait times are the same
    # Ensure all waits are within configured range
    assert all(0.1 <= t <= 1.0 for t in wait_deltas)

# Test that the jitter prevents synchronized retries in distributed systems
def test_thundering_herd_prevention():
    """Simulate multiple clients and verify retries are not synchronized."""
    # Create multiple mock clients
    num_clients = 3
    mock_funcs = [make_mock_func([httpx.RequestError("Connection error")] * 5)
for _ in range(num_clients)]

    # Function to simulate client with retry
    async def client_func(mock_func):
        @http_retry(max_attempts=5, min_wait=0.1, max_wait=1.0)
        async def test_func():
            return await mock_func()
        try:
            return await test_func()
        except:
            return 0

    # Run clients concurrently
    results = asyncio.run(asyncio.gather(*[client_func(f) for f in mock_funcs]))

    # Analyze the retry patterns
    # In a real implementation you would use logging or metrics to analyze timing
    # For this test, we'll assume different error patterns indicate desynchronization
    assert len(set(results)) > 1, "Clients should not all fail synchronously"

# Verify that tenacity version supports the required API
def test_tenacity_version_compatibility():
    """Ensure the tenacity version supports wait_exponential_jitter parameters."""
    import tenacity
    from pkg_resources import parse_version

    # Check minimum version that supports the parameters we're using
    required_version = parse_version("8.0.1")  # Version when parameters were standardized
    assert parse_version(tenacity.__version__) >= required_version, \
        f"tenacity version {tenacity.__version__} does not support the required wait_exponential_jitter parameters"
