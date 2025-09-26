from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Callable, Dict, Optional

from pydantic import BaseModel

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


# --- Common Models ---
class BaseModelWithTime(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# --- Authentication Models ---
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# --- RAG Upload Models ---
class RAGFileMetaData(BaseModel):
    filename: str
    content_type: str
    uploaded_by: Optional[str] = None
    description: Optional[str] = None


class RAGFileCreate(BaseModelWithTime):
    filename: str
    content_type: str
    metadata: Optional[RAGFileMetaData] = None


class RAGFileDetail(RAGFileCreate):
    id: str
    file_size: int
    ingestion_status: str


# --- Agent Models ---
class AgentType(str, Enum):
    LOCAL_SCRIPT = "local_script"
    EXTERNAL_API = "external_api"
    DATABASE_QUERY = "database_query"


class AgentConfig(BaseModel):
    agent_id: str
    name: str
    type: AgentType
    description: Optional[str] = None
    configuration: Dict[str, Any] = {}


# --- System Monitoring Models ---
class SystemHealthStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class SystemMetric(BaseModelWithTime):
    metric_name: str
    value: float
    status: SystemHealthStatus


# --- Common Fields ---
class PaginationRequest(BaseModel):
    page: int = 1
    page_size: int = 10


class PaginationResponse(BaseModel):
    total_items: int
    total_pages: int
    current_page: int
    page_size: int
