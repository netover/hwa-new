from __future__ import annotations

import asyncio
import logging
import re
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, List

import httpx

from resync.core.cache_hierarchy import get_cache_hierarchy
from resync.core.connection_pool_manager import get_connection_pool_manager
from resync.core.exceptions import TWSConnectionError
from resync.core.resilience import circuit_breaker, retry_with_backoff, with_timeout
from resync.models.tws import (
    CriticalJob,
    JobStatus,
    SystemStatus,
    WorkstationStatus,
)
from resync.settings import settings  # New import

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# Regex para validar job_ids, permitindo alfanuméricos, underscores e hifens.
SAFE_JOB_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

# --- Constants ---
# Default timeout for HTTP requests to prevent indefinite hangs
DEFAULT_TIMEOUT = 30.0


# --- Caching Mechanism ---
# CacheEntry and SimpleTTLCache moved to resync.core.async_cache
# Now using AsyncTTLCache for truly async operations


# --- TWS Client ---
class OptimizedTWSClient:
    """
    An optimized client for interacting with the HCL Workload Automation (TWS) API.
    Features include asynchronous requests, connection pooling, and caching.
    """

    def __init__(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str,
        engine_name: str = "tws-engine",
        engine_owner: str = "tws-owner",
        use_connection_pool: bool = True,
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.engine_name = engine_name
        self.engine_owner = engine_owner
        self.timeout = DEFAULT_TIMEOUT
        self.base_url = f"http://{hostname}:{port}/twsd"
        self.auth = (username, password)
        self.use_connection_pool = use_connection_pool
        self._pool_manager: Any = None

        if use_connection_pool:
            # Use connection pool manager for enhanced connection management
            logger.info("Using connection pool manager for TWS HTTP client")
        else:
            # Legacy direct httpx client for backward compatibility
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                auth=self.auth,
                verify=True,  # Development: TWS often uses self-signed certs
                timeout=httpx.Timeout(
                    connect=getattr(settings, "TWS_CONNECT_TIMEOUT", 10.0),
                    read=getattr(settings, "TWS_READ_TIMEOUT", 30.0),
                    write=getattr(settings, "TWS_WRITE_TIMEOUT", 30.0),
                    pool=getattr(settings, "TWS_POOL_TIMEOUT", 5.0),
                ),
                limits=httpx.Limits(
                    max_connections=getattr(settings, "TWS_MAX_CONNECTIONS", 100),
                    max_keepalive_connections=getattr(
                        settings, "TWS_MAX_KEEPALIVE", 20
                    ),
                ),
            )

        # Caching layer to reduce redundant API calls - using a direct Redis cache
        self.cache = get_cache_hierarchy()
        logger.info("OptimizedTWSClient initialized for base URL: %s", self.base_url)

    async def _get_http_client(self) -> Any:
        """Get HTTP client from connection pool or use direct client."""
        if self.use_connection_pool:
            if self._pool_manager is None:
                self._pool_manager = await get_connection_pool_manager()
            pool = self._pool_manager.get_pool("tws_http")
            if pool:
                return await pool.get_connection()
            else:
                logger.warning(
                    "TWS HTTP connection pool not available, falling back to direct client"
                )
                # Fallback to direct client if pool not available
                if not hasattr(self, "client"):
                    self.client = httpx.AsyncClient(
                        base_url=self.base_url,
                        auth=self.auth,
                        verify=True,
                        timeout=httpx.Timeout(
                            connect=getattr(settings, "TWS_CONNECT_TIMEOUT", 10.0),
                            read=getattr(settings, "TWS_READ_TIMEOUT", 30.0),
                            write=getattr(settings, "TWS_WRITE_TIMEOUT", 30.0),
                            pool=getattr(settings, "TWS_POOL_TIMEOUT", 5.0),
                        ),
                        limits=httpx.Limits(
                            max_connections=getattr(
                                settings, "TWS_MAX_CONNECTIONS", 100
                            ),
                            max_keepalive_connections=getattr(
                                settings, "TWS_MAX_KEEPALIVE", 20
                            ),
                        ),
                    )
                return self.client
        else:
            return self.client if hasattr(self, "client") else None

    @circuit_breaker(  # type: ignore
        failure_threshold=3, recovery_timeout=30, name="tws_http_client"
    )
    @retry_with_backoff(  # type: ignore
        max_retries=3, base_delay=1.0, max_delay=10.0, jitter=True
    )
    @with_timeout(getattr(settings, "TWS_REQUEST_TIMEOUT", 30.0))  # type: ignore
    async def _make_request(
        self, method: str, url: str, **kwargs: Any
    ) -> httpx.Response:
        """Makes an HTTP request with retry logic using connection pool."""
        logger.debug("Making request: %s %s", method.upper(), url)

        # Get client from connection pool or use direct client
        client = await self._get_http_client()
        if client is None:
            raise TWSConnectionError("No HTTP client available")

        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"HTTP request failed: {method} {url} - {e}")
            raise

    @asynccontextmanager
    async def _api_request(
        self, method: str, url: str, **kwargs: Any
    ) -> AsyncGenerator[dict[str, Any] | list[Any], None]:
        """A context manager for making robust API requests."""
        try:
            response = await self._make_request(method, url, **kwargs)
            data = response.json()
            if isinstance(data, (dict, list)):
                yield data
            else:
                yield {}
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error occurred: %s - %s",
                e.response.status_code,
                e.response.text,
            )
            raise TWSConnectionError(
                f"HTTP error: {e.response.status_code}", original_exception=e
            )
        except httpx.RequestError as e:
            logger.error("Network error during API request: %s", str(e))
            raise TWSConnectionError(
                f"Network error during API request: {e.request.url}",
                original_exception=e,
            )
        except Exception as e:
            logger.error("An unexpected error occurred during API request: %s", e)
            # Wrap unexpected errors for consistent error handling
            raise TWSConnectionError(
                "An unexpected error occurred", original_exception=e
            )

    @circuit_breaker(  # type: ignore
        failure_threshold=5, recovery_timeout=60, name="tws_ping"
    )
    @retry_with_backoff(  # type: ignore
        max_retries=2, base_delay=0.5, max_delay=3.0, jitter=True
    )
    @with_timeout(5.0)  # type: ignore
    async def ping(self) -> None:
        """
        Performs a lightweight connectivity test to the TWS server.

        This method attempts to establish a connection and receive a response
        without processing the full API response, making it suitable for health checks.

        Raises:
            TWSConnectionError: If the server is unreachable, unresponsive, or times out.
        """
        try:
            # Get client from connection pool or use direct client
            client = await self._get_http_client()
            if client is None:
                raise TWSConnectionError("No HTTP client available for ping")

            # Use a simple HEAD request to the base URL to test connectivity
            response = await client.head("", timeout=5.0)
            response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.warning("TWS server ping timed out")
            raise TWSConnectionError("TWS server ping timed out", original_exception=e)
        except httpx.RequestError as e:
            logger.error(f"TWS server ping failed: {e}")
            raise TWSConnectionError(f"TWS server unreachable", original_exception=e)
        except Exception as e:
            logger.error(f"Unexpected error during TWS ping: {e}")
            raise TWSConnectionError(
                "TWS ping failed unexpectedly", original_exception=e
            )

    @circuit_breaker(  # type: ignore
        failure_threshold=3, recovery_timeout=30, name="tws_check_connection"
    )
    @with_timeout(10.0)  # type: ignore
    async def check_connection(self) -> bool:
        """Verifies the connection to the TWS server is active."""
        try:
            async with self._api_request("GET", "/plan/current") as data:
                return "planId" in data
        except TWSConnectionError:
            return False

    @circuit_breaker(  # type: ignore
        failure_threshold=3, recovery_timeout=30, name="tws_workstations"
    )
    @retry_with_backoff(  # type: ignore
        max_retries=2, base_delay=1.0, max_delay=5.0, jitter=True
    )
    @with_timeout(getattr(settings, "TWS_REQUEST_TIMEOUT", 30.0))  # type: ignore
    async def get_workstations_status(self) -> List[WorkstationStatus]:
        """Retrieves the status of all workstations, utilizing the cache."""
        cache_key = "workstations_status"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data if isinstance(cached_data, list) else []

        url = f"/model/workstation?engineName={self.engine_name}&engineOwner={self.engine_owner}"
        async with self._api_request("GET", url) as data:
            workstations = (
                [WorkstationStatus(**ws) for ws in data]
                if isinstance(data, list)
                else []
            )
            await self.cache.set(
                cache_key, workstations
            )  # ttl not supported in current cache implementation
            return workstations

    @circuit_breaker(  # type: ignore
        failure_threshold=3, recovery_timeout=30, name="tws_jobs_status"
    )
    @retry_with_backoff(  # type: ignore
        max_retries=2, base_delay=1.0, max_delay=5.0, jitter=True
    )
    @with_timeout(getattr(settings, "TWS_REQUEST_TIMEOUT", 30.0))  # type: ignore
    async def get_jobs_status(self) -> List[JobStatus]:
        """Retrieves the status of all jobs, utilizing the cache."""
        cache_key = "jobs_status"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data if isinstance(cached_data, list) else []

        url = f"/model/jobdefinition?engineName={self.engine_name}&engineOwner={self.engine_owner}"
        async with self._api_request("GET", url) as data:
            jobs = [JobStatus(**job) for job in data] if isinstance(data, list) else []
            await self.cache.set(
                cache_key, jobs
            )  # ttl not supported in current cache implementation
            return jobs

    async def get_critical_path_status(self) -> List[CriticalJob]:
        """Retrieves the status of jobs in the critical path, utilizing the cache."""
        cache_key = "critical_path_status"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data if isinstance(cached_data, list) else []

        url = "/plan/current/criticalpath"
        async with self._api_request("GET", url) as data:
            jobs_data = data.get("jobs", []) if isinstance(data, dict) else []
            critical_jobs = (
                [CriticalJob(**job) for job in jobs_data]
                if isinstance(jobs_data, list)
                else []
            )
            await self.cache.set(
                cache_key, critical_jobs
            )  # ttl not supported in current cache implementation
            return critical_jobs

    @circuit_breaker(  # type: ignore
        failure_threshold=2, recovery_timeout=60, name="tws_system_status"
    )
    @retry_with_backoff(  # type: ignore
        max_retries=3, base_delay=1.0, max_delay=8.0, jitter=True
    )
    @with_timeout(getattr(settings, "TWS_REQUEST_TIMEOUT", 30.0))  # type: ignore
    async def get_system_status(self) -> SystemStatus:
        """Retrieves a comprehensive system status with parallel execution."""
        # Execute all three calls concurrently
        workstations_task = asyncio.create_task(self.get_workstations_status())
        jobs_task = asyncio.create_task(self.get_jobs_status())
        critical_jobs_task = asyncio.create_task(self.get_critical_path_status())

        workstations: List[WorkstationStatus] | Exception
        jobs: List[JobStatus] | Exception
        critical_jobs: List[CriticalJob] | Exception
        workstations, jobs, critical_jobs = await asyncio.gather(
            workstations_task, jobs_task, critical_jobs_task, return_exceptions=True
        )

        # Handle potential exceptions
        if isinstance(workstations, Exception):
            logger.error(f"Failed to get workstations status: {workstations}")
            workstations = []

        if isinstance(jobs, Exception):
            logger.error(f"Failed to get jobs status: {jobs}")
            jobs = []

        if isinstance(critical_jobs, Exception):
            logger.error(f"Failed to get critical path status: {critical_jobs}")
            critical_jobs = []

        return SystemStatus(
            workstations=workstations, jobs=jobs, critical_jobs=critical_jobs
        )

    async def get_job_status_batch(self, job_ids: List[str]) -> dict[str, JobStatus]:
        """
        Batch multiple job status queries using parallel execution.

        Args:
            job_ids: List of job IDs to query

        Returns:
            Dictionary mapping job_id to JobStatus
        """
        results: dict[str, JobStatus] = {}

        # Separate cached and uncached jobs
        uncached_jobs = []
        for job_id in job_ids:
            # Validação de segurança para prevenir Path Traversal ou injeção de URL
            if not SAFE_JOB_ID_PATTERN.match(job_id):
                logger.warning(f"Skipping invalid job_id format: {job_id}")
                continue

            cache_key = f"job_status:{job_id}"
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                results[job_id] = cached_data
            else:
                uncached_jobs.append(job_id)

        # Process uncached jobs in parallel with concurrency control
        if uncached_jobs:
            # Limit concurrent requests to prevent overwhelming the server
            semaphore = asyncio.Semaphore(
                getattr(settings, "TWS_MAX_CONCURRENT_REQUESTS", 10)
            )

            async def fetch_single_job(job_id: str) -> tuple[str, JobStatus | None]:
                async with semaphore:
                    try:
                        url = f"/model/jobdefinition/{job_id}?engineName={self.engine_name}&engineOwner={self.engine_owner}"
                        async with self._api_request("GET", url) as data:
                            if isinstance(data, dict):
                                job_status = JobStatus(**data)
                                # Cache the result
                                await self.cache.set(
                                    f"job_status:{job_id}", job_status
                                )  # ttl not supported in current cache implementation
                                return job_id, job_status
                            else:
                                logger.warning(
                                    f"Unexpected data format for job {job_id}: expected dict, got {type(data)}"
                                )
                                return job_id, None
                    except Exception as e:
                        logger.warning(f"Failed to get status for job {job_id}: {e}")
                        return job_id, None

            # Execute all requests concurrently
            tasks = [fetch_single_job(job_id) for job_id in uncached_jobs]
            parallel_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in parallel_results:
                if isinstance(result, Exception):
                    logger.error(f"Error in parallel job status fetch: {result}")
                elif isinstance(result, tuple) and len(result) == 2:
                    job_id, job_status = result
                    if job_status is not None:
                        results[job_id] = job_status

        return results

    async def validate_connection(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> dict[str, Any]:
        """
        Validates TWS connection parameters without changing the current connection.

        Args:
            host: TWS server hostname (optional, uses current if not provided)
            port: TWS server port (optional, uses current if not provided)
            user: TWS username (optional, uses current if not provided)
            password: TWS password (optional, uses current if not provided)

        Returns:
            Dictionary with validation result
        """
        # Use current values if not provided
        test_host = host or self.hostname
        test_port = port or self.port
        test_user = user or self.username
        test_password = password or self.password

        try:
            # Create a temporary client with the test parameters
            test_base_url = f"http://{test_host}:{test_port}/twsd"
            test_client = httpx.AsyncClient(
                base_url=test_base_url,
                auth=(test_user, test_password),
                verify=True,
                timeout=httpx.Timeout(
                    connect=getattr(settings, "TWS_CONNECT_TIMEOUT", 10),
                    read=getattr(settings, "TWS_READ_TIMEOUT", 30),
                    write=getattr(settings, "TWS_WRITE_TIMEOUT", 30),
                    pool=getattr(settings, "TWS_POOL_TIMEOUT", 30),
                ),
            )

            # Try to establish a connection
            response = await test_client.head("", timeout=5.0)
            response.raise_for_status()

            await test_client.aclose()

            logger.info(
                f"TWS connection validation successful for {test_host}:{test_port}"
            )
            return {
                "valid": True,
                "message": f"Successfully validated connection to {test_host}:{test_port}",
                "host": test_host,
                "port": test_port,
            }

        except httpx.TimeoutException as e:
            logger.warning(
                f"TWS connection validation timed out for {test_host}:{test_port}"
            )
            return {
                "valid": False,
                "message": f"TWS connection validation timed out: {e}",
                "host": test_host,
                "port": test_port,
            }
        except httpx.RequestError as e:
            logger.error(
                f"TWS connection validation failed for {test_host}:{test_port} - {e}"
            )
            await test_client.aclose()  # Make sure client is closed in case of error
            return {
                "valid": False,
                "message": f"TWS connection validation failed: {e}",
                "host": test_host,
                "port": test_port,
            }
        except Exception as e:
            logger.error(f"Unexpected error during TWS connection validation: {e}")
            if "test_client" in locals():
                try:
                    await test_client.aclose()
                except Exception as e:
                    # Log cleanup errors but don't fail the validation
                    logger.debug(f"TWS test client cleanup error: {e}")
            return {
                "valid": False,
                "message": f"Unexpected error during TWS connection validation: {e}",
                "host": test_host,
                "port": test_port,
            }

    async def invalidate_system_cache(self) -> None:
        """Invalidates system-level cache."""
        logger.info("Invalidating system-level TWS cache")
        # Clear all cached system status data
        await self.cache.delete_pattern("tws:system:*")

    async def invalidate_all_jobs(self) -> None:
        """Invalidates all job-related cache."""
        logger.info("Invalidating all job-related TWS cache")
        # Clear all cached job data
        await self.cache.delete_pattern("tws:jobs:*")

    async def invalidate_all_workstations(self) -> None:
        """Invalidates all workstation-related cache."""
        logger.info("Invalidating all workstation-related TWS cache")
        # Clear all cached workstation data
        await self.cache.delete_pattern("tws:workstations:*")

    @property
    def is_connected(self) -> bool:
        """Checks if the TWS client is currently connected."""
        if self.use_connection_pool:
            pool_manager = asyncio.run(get_connection_pool_manager())
            return pool_manager.is_pool_healthy("tws_http")
        else:
            return hasattr(self, "client") and not self.client.is_closed

    async def close(self) -> None:
        """Closes the underlying HTTPX client and its connections."""
        if self.use_connection_pool:
            # Connection pool manager handles cleanup
            logger.info(
                "TWS client using connection pool - cleanup handled by pool manager"
            )
        else:
            # Close direct client if it exists
            if hasattr(self, "client") and not self.client.is_closed:
                await self.client.aclose()
                logger.info("HTTPX client has been closed.")
