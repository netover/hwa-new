from __future__ import annotations

from typing import Annotated, Callable, List

from pydantic import BaseModel, Field

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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
        ...,
        description="The current status of the job (e.g., 'SUCC', 'ABEND').",
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
