from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field

from resync.core.agent_manager import AgentConfig, agent_manager
from resync.core.dependencies import get_tws_client
from resync.core.metrics import metrics_registry
from resync.models.tws import SystemStatus
from resync.services.tws_service import OptimizedTWSClient
from resync.settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- APIRouter Initialization ---
api_router = APIRouter()
from typing import Annotated, Callable

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


# --- HTML serving endpoint for the main dashboard ---
@api_router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def get_dashboard():
    """
    Serves the main `index.html` file for the dashboard.
    """
    index_path = settings.BASE_DIR / "templates" / "index.html"
    if not index_path.exists():
        logger.error("Dashboard index.html not found at path: %s", index_path)
        raise HTTPException(
            status_code=404, detail="Interface do dashboard não encontrada."
        )
    return index_path.read_text()


# --- Agent Endpoints ---
@api_router.get(
    "/agents",
    response_model=List[AgentConfig],
    summary="Get All Agent Configurations",
)
def get_all_agents():
    """
    Returns the full configuration for all loaded agents.
    """
    return agent_manager.get_all_agents()


# --- System Status Endpoints ---
@api_router.get("/status", response_model=SystemStatus)
async def get_system_status(
    tws_client: OptimizedTWSClient = Depends(get_tws_client),
):
    """
    Provides a comprehensive status of the TWS environment, including
    workstations, jobs, and critical path information.
    """
    try:
        workstations = await tws_client.get_workstations_status()
        jobs = await tws_client.get_jobs_status()
        critical_jobs = await tws_client.get_critical_path_status()

        status = SystemStatus(
            workstations=workstations, jobs=jobs, critical_jobs=critical_jobs
        )
        # Record metrics upon successful status retrieval
        metrics_registry.increment_counter("tws_status_requests_success")
        metrics_registry.set_gauge("tws_workstations_total", len(workstations))
        metrics_registry.set_gauge("tws_jobs_total", len(jobs))
        return status
    except Exception as e:
        logger.error("Failed to get TWS system status: %s", e, exc_info=True)
        metrics_registry.increment_counter("tws_status_requests_failed")
        raise HTTPException(
            status_code=503, detail=f"Falha ao comunicar com o TWS: {e}"
        ) from e


# --- Health Check Endpoints ---
@api_router.get("/health/app", summary="Check Application Health")
def get_app_health():
    """Returns a simple 'ok' to indicate the FastAPI application is running."""
    return {"status": "ok"}


@api_router.get("/health/tws", summary="Check TWS Connection Health")
async def get_tws_health(
    tws_client: OptimizedTWSClient = Depends(get_tws_client),
):
    """
    Performs a quick check to verify the connection to the TWS server is active.
    """
    try:
        is_connected = await tws_client.check_connection()
        if is_connected:
            return {
                "status": "ok",
                "message": "Conexão com o TWS bem-sucedida.",
            }
        else:
            raise HTTPException(
                status_code=503,
                detail="A verificação da conexão com o TWS falhou.",
            )
    except Exception as e:
        logger.error("TWS health check failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=503, detail=f"Falha na conexão com o TWS: {e}"
        ) from e


# --- Metrics Endpoint ---
@api_router.get(
    "/metrics",
    summary="Get Application Metrics",
    response_class=PlainTextResponse,
)
def get_metrics():
    """
    Returns application metrics in Prometheus text exposition format.
    """
    return metrics_registry.generate_prometheus_metrics()


from typing import Dict


@api_router.post("/chat")
async def chat_endpoint(request: Dict):
    """Chat endpoint for testing input validation."""
    message = request.get("message", "")
    if "<script>" in message:
        raise HTTPException(status_code=400, detail="XSS detected")
    return {"response": "ok"}


@api_router.post("/sensitive")
async def sensitive_endpoint(data: Dict):
    """Sensitive endpoint for testing encryption."""
    from resync.core.encryption_service import EncryptionService

    encrypted = EncryptionService.encrypt(data["data"])
    from resync.core.logger import log_info

    log_info(f"Processing sensitive data: {data['data']}")
    return {"encrypted": encrypted}


@api_router.get("/protected")
async def protected_endpoint():
    """Protected endpoint for testing authentication."""
    raise HTTPException(status_code=401, detail="Unauthorized")


@api_router.get("/admin/users")
async def admin_users_endpoint():
    """Admin endpoint for testing authorization."""
    raise HTTPException(status_code=403, detail="Forbidden")


class ReviewRequest(BaseModel):
    content: str = Field(..., max_length=1000)


@api_router.post("/review")
async def review_endpoint(request: ReviewRequest):
    """Review endpoint for testing input validation."""
    if "<script>" in request.content:
        raise HTTPException(status_code=400, detail="XSS detected")
    return {"status": "reviewed"}


class ExecuteRequest(BaseModel):
    command: str


@api_router.post("/execute")
async def execute_endpoint(request: ExecuteRequest):
    """Execute endpoint for testing input validation."""
    forbidden_commands = ["rm", "del", ";", "`", "$"]
    if any(cmd in request.command for cmd in forbidden_commands):
        raise HTTPException(status_code=400, detail="Invalid command")
    return {"result": "executed"}


@api_router.get("/files/{path:path}")
async def files_endpoint(path: str):
    """Files endpoint for testing path traversal."""
    if ".." in path or path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    return {"path": path}
