from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, List, TypeVar

import httpx
from pydantic import BaseModel

from resync.models.tws import (
    CriticalJob,
    JobStatus,
    SystemStatus,
    WorkstationStatus,
)
from resync.settings import TWSProtocol

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- Constants ---
DEFAULT_TIMEOUT = 30.0

# --- Generic TypeVar for Cache ---
T = TypeVar("T")


# --- Caching Mechanism ---
class CacheEntry(BaseModel):
    """Represents a single entry in the cache."""

    data: Any
    timestamp: float


class SimpleTTLCache:
    """
    A simple in-memory cache with a Time-To-Live (TTL) for entries.
    This implementation includes a lock to prevent cache stampedes (dog-piling).
    """

    def __init__(self, ttl: int = 30):
        self.ttl = ttl
        self.cache: Dict[str, CacheEntry] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    async def _get_lock(self, key: str) -> asyncio.Lock:
        """Retrieves or creates a lock for a given cache key."""
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def get(self, key: str) -> Any | None:
        """Retrieves an item from the cache if it exists and has not expired."""
        entry = self.cache.get(key)
        if entry:
            loop = asyncio.get_running_loop()
            if (loop.time() - entry.timestamp) < self.ttl:
                logger.debug(f"Cache HIT for key: {key}")
                return entry.data
            else:
                logger.debug(f"Cache EXPIRED for key: {key}")
                # The lock will prevent multiple requests from deleting simultaneously
                async with await self._get_lock(key):
                    if (
                        key in self.cache
                        and (loop.time() - self.cache[key].timestamp) >= self.ttl
                    ):
                        del self.cache[key]
        logger.debug(f"Cache MISS for key: {key}")
        return None

    async def set(self, key: str, value: Any):
        """Adds an item to the cache."""
        loop = asyncio.get_running_loop()
        self.cache[key] = CacheEntry(data=value, timestamp=loop.time())
        logger.debug(f"Cache SET for key: {key}")

    async def get_or_fetch(
        self, key: str, fetch_func: Callable[[], Coroutine[Any, Any, T]]
    ) -> T:
        """
        A robust method to get an item from cache, or fetch, cache, and return it.
        Handles cache stampedes by using locks.
        """
        cached_data = await self.get(key)
        if cached_data is not None:
            return cached_data

        lock = await self._get_lock(key)
        async with lock:
            # Check again in case another coroutine populated the cache while we waited for the lock
            cached_data = await self.get(key)
            if cached_data is not None:
                return cached_data

            # Fetch new data, cache it, and return
            logger.debug(f"Fetching data for cache key: {key}")
            new_data = await fetch_func()
            await self.set(key, new_data)
            return new_data


# --- TWS Client ---
class OptimizedTWSClient:
    """
    An optimized client for interacting with the HCL Workload Automation (TWS) API.
    Features include asynchronous requests, connection pooling, and caching.
    """

    def __init__(
        self,
        protocol: TWSProtocol,
        hostname: str,
        port: int,
        username: str,
        password: str,
        ssl_verify: bool,
        engine_name: str = "tws-engine",
        engine_owner: str = "tws-owner",
    ):
        self.base_url = f"{protocol}://{hostname}:{port}/twsd"
        self.auth = (username, password)
        self.engine_name = engine_name
        self.engine_owner = engine_owner

        # Asynchronous client with connection pooling and configurable SSL verification
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=self.auth,
            verify=ssl_verify,
            timeout=DEFAULT_TIMEOUT,
        )
        self.cache = SimpleTTLCache(ttl=30)
        logger.info(
            "OptimizedTWSClient initialized for base URL: %s (SSL Verify: %s)",
            self.base_url,
            ssl_verify,
        )

    async def _api_request(self, method: str, url: str, **kwargs) -> Any:
        """A robust method for making API requests."""
        logger.debug(f"Request: {method.upper()} {url}")
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error occurred: %s - %s", e.response.status_code, e.response.text
            )
            raise ConnectionError(f"HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error("Request error occurred: %s", e)
            raise ConnectionError(f"Request failed: {e}") from e

    async def check_connection(self) -> bool:
        """Verifies the connection to the TWS server is active."""
        try:
            data = await self._api_request("GET", "/plan/current")
            return "planId" in data
        except ConnectionError:
            return False

    async def get_workstations_status(self) -> List[WorkstationStatus]:
        """Retrieves the status of all workstations, utilizing the cache."""

        async def _fetch() -> List[WorkstationStatus]:
            url = f"/model/workstation?engineName={self.engine_name}&engineOwner={self.engine_owner}"
            data = await self._api_request("GET", url)
            return [WorkstationStatus(**ws) for ws in data]

        return await self.cache.get_or_fetch("workstations_status", _fetch)

    async def get_jobs_status(self) -> List[JobStatus]:
        """Retrieves the status of all jobs, utilizing the cache."""

        async def _fetch() -> List[JobStatus]:
            url = f"/model/jobdefinition?engineName={self.engine_name}&engineOwner={self.engine_owner}"
            data = await self._api_request("GET", url)
            return [JobStatus(**job) for job in data]

        return await self.cache.get_or_fetch("jobs_status", _fetch)

    async def get_critical_path_status(self) -> List[CriticalJob]:
        """Retrieves the status of jobs in the critical path, utilizing the cache."""

        async def _fetch() -> List[CriticalJob]:
            url = "/plan/current/criticalpath"
            data = await self._api_request("GET", url)
            return [CriticalJob(**job) for job in data.get("jobs", [])]

        return await self.cache.get_or_fetch("critical_path_status", _fetch)

    async def get_system_status(self) -> SystemStatus:
        """Retrieves a comprehensive system status by calling cached methods."""
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
