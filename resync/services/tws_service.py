from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import List

import httpx

from resync.core.cache_hierarchy import get_cache_hierarchy
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
        self.base_url = f"{hostname}:{port}/twsd"
        self.auth = (username, password)
        self.engine_name = engine_name
        self.engine_owner = engine_owner

        # Asynchronous client with connection pooling
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=self.auth,
            verify=True,
            timeout=DEFAULT_TIMEOUT,
        )
        # Caching layer to reduce redundant API calls - now using cache hierarchy
        self.cache = get_cache_hierarchy()
        logger.info("OptimizedTWSClient initialized for base URL: %s", self.base_url)

    @asynccontextmanager
    async def _api_request(self, method: str, url: str, **kwargs) -> any:
        """A context manager for making robust API requests."""
        logger.debug(f"Request: {method.upper()} {url}")
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            yield response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error occurred: %s - %s",
                e.response.status_code,
                e.response.text,
            )
            raise ConnectionError(f"HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error("Request error occurred: %s", e)
            raise ConnectionError(f"Request failed: {e}") from e
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

    async def close(self):
        """Closes the underlying HTTPX client and its connections."""
        if not self.client.is_closed:
            await self.client.aclose()
            logger.info("HTTPX client has been closed.")
