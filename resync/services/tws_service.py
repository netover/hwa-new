from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, List

import httpx

from resync.core.cache_hierarchy import get_cache_hierarchy
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
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.engine_name = engine_name
        self.engine_owner = engine_owner
        self.timeout = DEFAULT_TIMEOUT
        self.base_url = f"{hostname}:{port}/twsd"
        self.auth = (username, password)

        # Asynchronous client with TWS-optimized connection pooling
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=self.auth,
            verify=False,  # Development: TWS often uses self-signed certs
            timeout=httpx.Timeout(
                connect=10,  # TWS can be slow to connect
                read=30,  # TWS responses can be large/slow
                write=10,
                pool=5,
            ),
            limits=httpx.Limits(
                max_connections=20,  # 15 users + 4M jobs/month = need more connections
                max_keepalive_connections=8,
            ),
        )
        # Caching layer to reduce redundant API calls - now using cache hierarchy
        self.cache = get_cache_hierarchy()
        logger.info("OptimizedTWSClient initialized for base URL: %s", self.base_url)

    @http_retry(max_attempts=3, min_wait=1.0, max_wait=5.0)
    async def _make_request(
        self, method: str, url: str, **kwargs: Any
    ) -> httpx.Response:
        """Makes an HTTP request with retry logic."""
        logger.debug("Making request: %s %s", method.upper(), url)
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    @asynccontextmanager
    async def _api_request(
        self, method: str, url: str, **kwargs: Any
    ) -> AsyncGenerator[Any, None]:
        """A context manager for making robust API requests."""
        try:
            response = await self._make_request(method, url, **kwargs)
            yield response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error occurred: %s - %s",
                e.response.status_code,
                e.response.text,
            )
            raise ConnectionError(f"HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error("Network error during API request: %s", str(e))
            raise ConnectionError(f"Network error: {str(e)}") from e
        except Exception as e:
            logger.error("An unexpected error occurred during API request: %s", e)
            raise

    async def check_connection(self) -> bool:
        """Verifies the connection to the TWS server is active."""
        try:
            async with self._api_request("GET", "/plan/current") as data:
                return "planId" in data
        except ConnectionError:
            return False

    async def get_workstations_status(self) -> List[WorkstationStatus]:
        """Retrieves the status of all workstations, utilizing the cache."""
        cache_key = "workstations_status"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data

        url = f"/model/workstation?engineName={self.engine_name}&engineOwner={self.engine_owner}"
        async with self._api_request("GET", url) as data:
            workstations = [WorkstationStatus(**ws) for ws in data]
            await self.cache.set_from_source(
                cache_key, workstations, ttl_seconds=settings.TWS_CACHE_TTL
            )
            return workstations

    async def get_jobs_status(self) -> List[JobStatus]:
        """Retrieves the status of all jobs, utilizing the cache."""
        cache_key = "jobs_status"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data

        url = f"/model/jobdefinition?engineName={self.engine_name}&engineOwner={self.engine_owner}"
        async with self._api_request("GET", url) as data:
            jobs = [JobStatus(**job) for job in data]
            await self.cache.set_from_source(
                cache_key, jobs, ttl_seconds=settings.TWS_CACHE_TTL
            )
            return jobs

    async def get_critical_path_status(self) -> List[CriticalJob]:
        """Retrieves the status of jobs in the critical path, utilizing the cache."""
        cache_key = "critical_path_status"
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            return cached_data

        url = "/plan/current/criticalpath"
        async with self._api_request("GET", url) as data:
            critical_jobs = [CriticalJob(**job) for job in data.get("jobs", [])]
            await self.cache.set_from_source(
                cache_key, critical_jobs, ttl_seconds=settings.TWS_CACHE_TTL
            )
            return critical_jobs

    async def get_system_status(self) -> SystemStatus:
        """Retrieves a comprehensive system status."""
        workstations = await self.get_workstations_status()
        jobs = await self.get_jobs_status()
        critical_jobs = await self.get_critical_path_status()
        return SystemStatus(
            workstations=workstations, jobs=jobs, critical_jobs=critical_jobs
        )

    async def get_job_status_batch(self, job_ids: List[str]) -> dict[str, JobStatus]:
        """
        Batch multiple job status queries in a single optimized request.

        Args:
            job_ids: List of job IDs to query

        Returns:
            Dictionary mapping job_id to JobStatus
        """
        results = {}
        uncached_jobs = []

        # Check cache for each job
        for job_id in job_ids:
            cache_key = f"job_status:{job_id}"
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                results[job_id] = cached_data
            else:
                uncached_jobs.append(job_id)

        # Batch request for uncached jobs
        if uncached_jobs:
            # TWS API may support batch queries - if not, make individual calls
            for job_id in uncached_jobs:
                try:
                    # This would ideally be a batch API call
                    # For now, make individual calls (can be optimized further)
                    url = f"/model/jobdefinition/{job_id}?engineName={self.engine_name}&engineOwner={self.engine_owner}"
                    async with self._api_request("GET", url) as data:
                        job_status = JobStatus(**data)
                        results[job_id] = job_status
                        # Cache the result
                        await self.cache.set_from_source(
                            f"job_status:{job_id}",
                            job_status,
                            ttl_seconds=settings.TWS_CACHE_TTL,
                        )
                except Exception as e:
                    logger.warning(f"Failed to get status for job {job_id}: {e}")
                    # Return None or a default status for failed jobs
                    results[job_id] = None

        return results

    async def close(self) -> None:
        """Closes the underlying HTTPX client and its connections."""
        if not self.client.is_closed:
            await self.client.aclose()
            logger.info("HTTPX client has been closed.")
