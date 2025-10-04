"""
Query handlers for TWS operations in the CQRS pattern.
"""
from typing import List, Dict, Any
from resync.cqrs.base import IQueryHandler, QueryResult
from resync.cqrs.queries import (
    GetSystemStatusQuery, GetWorkstationsStatusQuery, GetJobsStatusQuery,
    GetCriticalPathStatusQuery, GetJobStatusQuery, GetJobStatusBatchQuery,
    GetSystemHealthQuery, SearchJobsQuery, GetPerformanceMetricsQuery
)
from resync.core.interfaces import ITWSClient
from resync.models.tws import SystemStatus, WorkstationStatus, JobStatus, CriticalJob
from resync.core.cache_hierarchy import get_cache_hierarchy


class GetSystemStatusQueryHandler(IQueryHandler[GetSystemStatusQuery, QueryResult]):
    """Handler for getting the overall system status."""
    
    def __init__(self, tws_client: ITWSClient):
        self.tws_client = tws_client
        self.cache = get_cache_hierarchy()
    
    async def execute(self, query: GetSystemStatusQuery) -> QueryResult:
        try:
            # Try to get from cache first
            cache_key = "query_system_status"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return QueryResult(
                    success=True,
                    data=cached_result
                )
            
            # If not in cache, fetch from TWS
            system_status = await self.tws_client.get_system_status()
            result = system_status.dict()
            
            # Store in cache
            await self.cache.set(cache_key, result, ttl=30)  # 30 seconds TTL
            
            return QueryResult(
                success=True,
                data=result
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )


class GetWorkstationsStatusQueryHandler(IQueryHandler[GetWorkstationsStatusQuery, QueryResult]):
    """Handler for getting workstation statuses."""
    
    def __init__(self, tws_client: ITWSClient):
        self.tws_client = tws_client
        self.cache = get_cache_hierarchy()
    
    async def execute(self, query: GetWorkstationsStatusQuery) -> QueryResult:
        try:
            # Try to get from cache first
            cache_key = "query_workstations_status"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return QueryResult(
                    success=True,
                    data=cached_result
                )
            
            # If not in cache, fetch from TWS
            workstations = await self.tws_client.get_workstations_status()
            result = [ws.dict() for ws in workstations]
            
            # Store in cache
            await self.cache.set(cache_key, result, ttl=30)  # 30 seconds TTL
            
            return QueryResult(
                success=True,
                data=result
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )


class GetJobsStatusQueryHandler(IQueryHandler[GetJobsStatusQuery, QueryResult]):
    """Handler for getting job statuses."""
    
    def __init__(self, tws_client: ITWSClient):
        self.tws_client = tws_client
        self.cache = get_cache_hierarchy()
    
    async def execute(self, query: GetJobsStatusQuery) -> QueryResult:
        try:
            # Try to get from cache first
            cache_key = "query_jobs_status"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return QueryResult(
                    success=True,
                    data=cached_result
                )
            
            # If not in cache, fetch from TWS
            jobs = await self.tws_client.get_jobs_status()
            result = [job.dict() for job in jobs]
            
            # Store in cache
            await self.cache.set(cache_key, result, ttl=30)  # 30 seconds TTL
            
            return QueryResult(
                success=True,
                data=result
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )


class GetCriticalPathStatusQueryHandler(IQueryHandler[GetCriticalPathStatusQuery, QueryResult]):
    """Handler for getting critical path statuses."""
    
    def __init__(self, tws_client: ITWSClient):
        self.tws_client = tws_client
        self.cache = get_cache_hierarchy()
    
    async def execute(self, query: GetCriticalPathStatusQuery) -> QueryResult:
        try:
            # Try to get from cache first
            cache_key = "query_critical_path_status"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return QueryResult(
                    success=True,
                    data=cached_result
                )
            
            # If not in cache, fetch from TWS
            critical_jobs = await self.tws_client.get_critical_path_status()
            result = [cj.dict() for cj in critical_jobs]
            
            # Store in cache
            await self.cache.set(cache_key, result, ttl=30)  # 30 seconds TTL
            
            return QueryResult(
                success=True,
                data=result
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )


class GetJobStatusQueryHandler(IQueryHandler[GetJobStatusQuery, QueryResult]):
    """Handler for getting a specific job status."""
    
    def __init__(self, tws_client: ITWSClient):
        self.tws_client = tws_client
        self.cache = get_cache_hierarchy()
    
    async def execute(self, query: GetJobStatusQuery) -> QueryResult:
        try:
            # Try to get from cache first
            cache_key = f"query_job_status_{query.job_id}"
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return QueryResult(
                    success=True,
                    data=cached_result
                )
            
            # If not in cache, fetch from TWS using the batch method
            jobs_status = await self.tws_client.get_job_status_batch([query.job_id])
            job_status = jobs_status.get(query.job_id)
            result = job_status.dict() if job_status else None
            
            # Store in cache
            if result:
                await self.cache.set(cache_key, result, ttl=30)  # 30 seconds TTL
            
            return QueryResult(
                success=True,
                data=result
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )


class GetJobStatusBatchQueryHandler(IQueryHandler[GetJobStatusBatchQuery, QueryResult]):
    """Handler for getting batch job statuses."""
    
    def __init__(self, tws_client: ITWSClient):
        self.tws_client = tws_client
        self.cache = get_cache_hierarchy()
    
    async def execute(self, query: GetJobStatusBatchQuery) -> QueryResult:
        try:
            # Process each job ID, checking cache first
            results = {}
            uncached_job_ids = []
            
            # Check cache for each job
            for job_id in query.job_ids:
                cache_key = f"query_job_status_{job_id}"
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    results[job_id] = cached_result
                else:
                    uncached_job_ids.append(job_id)
            
            # Fetch uncached jobs from TWS
            if uncached_job_ids:
                uncached_results = await self.tws_client.get_job_status_batch(uncached_job_ids)
                for job_id, job_status in uncached_results.items():
                    if job_status:
                        result = job_status.dict()
                        results[job_id] = result
                        # Cache the individual result
                        await self.cache.set(
                            f"query_job_status_{job_id}",
                            result,
                            ttl=30
                        )
                    else:
                        results[job_id] = None
            
            return QueryResult(
                success=True,
                data=results
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )


class GetSystemHealthQueryHandler(IQueryHandler[GetSystemHealthQuery, QueryResult]):
    """Handler for getting system health."""
    
    def __init__(self, tws_monitor: any):
        self.tws_monitor = tws_monitor
    
    async def execute(self, query: GetSystemHealthQuery) -> QueryResult:
        try:
            health_report = self.tws_monitor.get_performance_report()
            return QueryResult(
                success=True,
                data=health_report
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )


class SearchJobsQueryHandler(IQueryHandler[SearchJobsQuery, QueryResult]):
    """Handler for searching jobs."""
    
    def __init__(self, tws_client: ITWSClient):
        self.tws_client = tws_client
        self.cache = get_cache_hierarchy()
    
    async def execute(self, query: SearchJobsQuery) -> QueryResult:
        try:
            # First, get all jobs
            jobs = await self.tws_client.get_jobs_status()
            
            # Filter jobs based on search term
            filtered_jobs = [
                job for job in jobs
                if query.search_term.lower() in job.name.lower() or
                query.search_term.lower() in job.workstation.lower() or
                query.search_term.lower() in job.status.lower()
            ][:query.limit]  # Limit the results
            
            result = [job.dict() for job in filtered_jobs]
            
            return QueryResult(
                success=True,
                data=result
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )


class GetPerformanceMetricsQueryHandler(IQueryHandler[GetPerformanceMetricsQuery, QueryResult]):
    """Handler for getting performance metrics."""
    
    def __init__(self, tws_monitor: any):
        self.tws_monitor = tws_monitor
    
    async def execute(self, query: GetPerformanceMetricsQuery) -> QueryResult:
        try:
            performance_metrics = self.tws_monitor.get_current_metrics()
            return QueryResult(
                success=True,
                data=performance_metrics
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )


class CheckTWSConnectionQueryHandler(IQueryHandler[CheckTWSConnectionQuery, QueryResult]):
    """Handler for checking TWS connection."""
    
    def __init__(self, tws_client: ITWSClient):
        self.tws_client = tws_client
    
    async def execute(self, query: CheckTWSConnectionQuery) -> QueryResult:
        try:
            is_connected = await self.tws_client.check_connection()
            return QueryResult(
                success=True,
                data={"connected": is_connected}
            )
        except Exception as e:
            return QueryResult(
                success=False,
                error=str(e)
            )