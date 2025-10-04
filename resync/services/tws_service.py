from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, List

import httpx

from resync.core.cache_hierarchy import get_cache_hierarchy
from resync.core.connection_pool_manager import get_connection_pool_manager
from resync.core.exceptions import TWSConnectionError
from resync.core.retry import http_retry
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
        self._pool_manager = None

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
                    connect=settings.TWS_CONNECT_TIMEOUT,
                    read=settings.TWS_READ_TIMEOUT,
                    write=settings.TWS_WRITE_TIMEOUT,
                    pool=settings.TWS_POOL_TIMEOUT,
                ),
                limits=httpx.Limits(
                    max_connections=settings.TWS_MAX_CONNECTIONS,
                    max_keepalive_connections=settings.TWS_MAX_KEEPALIVE,
                ),
            )

        # Caching layer to reduce redundant API calls - using a direct Redis cache
        self.cache = get_cache_hierarchy()
        logger.info("OptimizedTWSClient initialized for base URL: %s", self.base_url)

    async def _get_http_client(self):
        """Get HTTP client from connection pool or use direct client."""
        if self.use_connection_pool:
            if self._pool_manager is None:
                self._pool_manager = await get_connection_pool_manager()
            pool = self._pool_manager.get_pool("tws_http")
            if pool:
                return await pool.get_connection()
            else:
                logger.warning("TWS HTTP connection pool not available, falling back to direct client")
                # Fallback to direct client if pool not available
                if not hasattr(self, 'client'):
                    self.client = httpx.AsyncClient(
                        base_url=self.base_url,
                        auth=self.auth,
                        verify=True,
                        timeout=httpx.Timeout(
                            connect=settings.TWS_CONNECT_TIMEOUT,
                            read=settings.TWS_READ_TIMEOUT,
                            write=settings.TWS_WRITE_TIMEOUT,
                            pool=settings.TWS_POOL_TIMEOUT,
                        ),
                        limits=httpx.Limits(
                            max_connections=settings.TWS_MAX_CONNECTIONS,
                            max_keepalive_connections=settings.TWS_MAX_KEEPALIVE,
                        ),
                    )
                return self.client
        else:
            return self.client if hasattr(self, 'client') else None

    @http_retry(max_attempts=3, min_wait=1.0, max_wait=5.0)
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
            return response
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
            raise TWSConnectionError("An unexpected error occurred", original_exception=e)

    async def ping(self) -> None:
        """
        Performs a lightweight connectivity test to the TWS server.

        This method attempts to establish a connection and receive a response
        without processing the full API response, making it suitable for health checks.

        Raises:
            TWSConnectionError: If the server is unreachable, unresponsive, or times out.
        """
        try:
            # Use a simple HEAD request to the base URL to test connectivity
            # The client already has the base_url configured with protocol
            response = await self.client.head("", timeout=5.0)
            response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.warning("TWS server ping timed out")
            raise TWSConnectionError("TWS server ping timed out", original_exception=e)
        except httpx.RequestError as e:
            logger.error(f"TWS server ping failed: {e}")
            raise TWSConnectionError(
                f"TWS server unreachable: {e.request.url}", original_exception=e
            )
        except Exception as e:
            logger.error(f"Unexpected error during TWS ping: {e}")
            raise TWSConnectionError("TWS ping failed unexpectedly", original_exception=e)

    async def check_connection(self) -> bool:
        """Verifies the connection to the TWS server is active."""
        try:
            async with self._api_request("GET", "/plan/current") as data:
                return "planId" in data
        except TWSConnectionError:
            return False

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
            await self.cache.set(cache_key, workstations, ttl=settings.TWS_CACHE_TTL)
            return workstations

    async def get_jobs_status(self) -> List[JobStatus]:
        """Retrieves the status of all jobs, utilizing the cache."""
        cache_key = "jobs_status"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data if isinstance(cached_data, list) else []

        url = f"/model/jobdefinition?engineName={self.engine_name}&engineOwner={self.engine_owner}"
        async with self._api_request("GET", url) as data:
            jobs = [JobStatus(**job) for job in data] if isinstance(data, list) else []
            await self.cache.set(cache_key, jobs, ttl=settings.TWS_CACHE_TTL)
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
            await self.cache.set(cache_key, critical_jobs, ttl=settings.TWS_CACHE_TTL)
            return critical_jobs

    async def get_system_status(self) -> SystemStatus:
        """Retrieves a comprehensive system status with parallel execution."""
        # Execute all three calls concurrently
        workstations_task = asyncio.create_task(self.get_workstations_status())
        jobs_task = asyncio.create_task(self.get_jobs_status())
        critical_jobs_task = asyncio.create_task(self.get_critical_path_status())
        
        workstations, jobs, critical_jobs = await asyncio.gather(
            workstations_task, 
            jobs_task, 
            critical_jobs_task,
            return_exceptions=True
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
            workstations=workstations, 
            jobs=jobs, 
            critical_jobs=critical_jobs
        )

    async def get_job_status_batch(self, job_ids: List[str]) -> dict[str, JobStatus]:
        """
        Batch multiple job status queries using parallel execution.

        Args:
            job_ids: List of job IDs to query

        Returns:
            Dictionary mapping job_id to JobStatus
        """
        results = {}
        
        # Separate cached and uncached jobs
        uncached_jobs = []
        for job_id in job_ids:
            # Validação de segurança para prevenir Path Traversal ou injeção de URL
            if not SAFE_JOB_ID_PATTERN.match(job_id):
                logger.warning(f"Skipping invalid job_id format: {job_id}")
                results[job_id] = None
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
            semaphore = asyncio.Semaphore(settings.TWS_MAX_CONCURRENT_REQUESTS or 10)
            
            async def fetch_single_job(job_id: str) -> tuple[str, JobStatus]:
                async with semaphore:
                    try:
                        url = f"/model/jobdefinition/{job_id}?engineName={self.engine_name}&engineOwner={self.engine_owner}"
                        async with self._api_request("GET", url) as data:
                            if isinstance(data, dict):
                                job_status = JobStatus(**data)
                                # Cache the result
                                await self.cache.set(
                                    f"job_status:{job_id}",
                                    job_status,
                                    ttl=settings.TWS_CACHE_TTL,
                                )
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
                else:
                    job_id, job_status = result
                    results[job_id] = job_status

        return results

    async def close(self) -> None:
        """Closes the underlying HTTPX client and its connections."""
        if self.use_connection_pool:
            # Connection pool manager handles cleanup
            logger.info("TWS client using connection pool - cleanup handled by pool manager")
        else:
            # Close direct client if it exists
            if hasattr(self, 'client') and not self.client.is_closed:
                await self.client.aclose()
                logger.info("HTTPX client has been closed.")
