"""
Command implementations for TWS operations in the CQRS pattern.
"""
from dataclasses import dataclass
from typing import List, Optional
from resync.cqrs.base import ICommand
from resync.models.tws import JobStatus, WorkstationStatus, CriticalJob


@dataclass
class GetSystemStatusCommand(ICommand):
    """
    Command to retrieve the overall TWS system status.
    """
    pass


@dataclass
class GetWorkstationsStatusCommand(ICommand):
    """
    Command to retrieve the status of all TWS workstations.
    """
    pass


@dataclass
class GetJobsStatusCommand(ICommand):
    """
    Command to retrieve the status of all TWS jobs.
    """
    pass


@dataclass
class GetCriticalPathStatusCommand(ICommand):
    """
    Command to retrieve the status of TWS critical path jobs.
    """
    pass


@dataclass
class GetJobStatusBatchCommand(ICommand):
    """
    Command to retrieve the status of multiple TWS jobs in a batch.
    """
    job_ids: List[str]


@dataclass
class UpdateJobStatusCommand(ICommand):
    """
    Command to update the status of a specific TWS job.
    """
    job_id: str
    new_status: str


@dataclass
class ExecuteJobCommand(ICommand):
    """
    Command to execute a specific TWS job.
    """
    job_id: str


@dataclass
class GetSystemHealthCommand(ICommand):
    """
    Command to retrieve system health metrics.
    """
    pass