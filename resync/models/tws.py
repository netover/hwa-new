from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class WorkstationStatus(BaseModel):
    """Represents the status of a single TWS workstation."""

    name: str = Field(..., description="The name of the workstation.")
    status: str = Field(
        ...,
        description="The current status of the workstation (e.g., 'LINKED', 'DOWN').",
    )
    type: str = Field(
        ..., description="The type of the workstation (e.g., 'FTA', 'MASTER')."
    )


class JobStatus(BaseModel):
    """Represents the status of a single TWS job."""

    name: str = Field(..., description="The name of the job.")
    workstation: str = Field(..., description="The workstation where the job runs.")
    status: str = Field(
        ..., description="The current status of the job (e.g., 'SUCC', 'ABEND')."
    )
    job_stream: str = Field(..., description="The job stream the job belongs to.")


class CriticalJob(BaseModel):
    """Represents a job that is part of the critical path (TWS 'plan')."""

    job_id: int = Field(
        ..., description="The unique identifier for the job in the plan."
    )
    job_name: str = Field(..., description="The name of the job.")
    status: str = Field(..., description="The status of the critical job.")
    start_time: str = Field(..., description="The scheduled start time for the job.")


class SystemStatus(BaseModel):
    """A composite model representing the overall status of the TWS environment."""

    workstations: List[WorkstationStatus]
    jobs: List[JobStatus]
    critical_jobs: List[CriticalJob]
