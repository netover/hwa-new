"""
Query implementations for TWS operations in the CQRS pattern.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from resync.cqrs.base import IQuery
from resync.models.tws import JobStatus, WorkstationStatus, CriticalJob


@dataclass
class GetSystemStatusQuery(IQuery):
    """
    Query to retrieve the overall TWS system status.
    """
    pass


@dataclass
class GetWorkstationsStatusQuery(IQuery):
    """
    Query to retrieve the status of all TWS workstations.
    """
    pass


@dataclass
class GetJobsStatusQuery(IQuery):
    """
    Query to retrieve the status of all TWS jobs.
    """
    pass


@dataclass
class GetCriticalPathStatusQuery(IQuery):
    """
    Query to retrieve the status of TWS critical path jobs.
    """
    pass


@dataclass
class GetJobStatusQuery(IQuery):
    """
    Query to retrieve the status of a specific TWS job.
    """
    job_id: str


@dataclass
class GetJobStatusBatchQuery(IQuery):
    """
    Query to retrieve the status of multiple TWS jobs in a batch.
    """
    job_ids: List[str]


@dataclass
class GetSystemHealthQuery(IQuery):
    """
    Query to retrieve system health metrics.
    """
    pass


@dataclass
class SearchJobsQuery(IQuery):
    """
    Query to search for jobs based on specific criteria.
    """
    search_term: str
    limit: int = 10


@dataclass
class GetPerformanceMetricsQuery(IQuery):
    """
    Query to retrieve system performance metrics.
    """
    pass


@dataclass
class CheckTWSConnectionQuery(IQuery):
    """
    Query to check the TWS connection status.
    """
    pass