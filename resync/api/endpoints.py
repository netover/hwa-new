from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel, Field

from resync.core.agent_manager import AgentConfig
from resync.core.fastapi_di import get_agent_manager, get_tws_client
from resync.core.interfaces import IAgentManager, ITWSClient
from resync.core.metrics import runtime_metrics
from resync.core.tws_monitor import tws_monitor
from resync.models.tws import SystemStatus
from resync.settings import settings
from resync.core.rate_limiter import public_rate_limit, authenticated_rate_limit

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- APIRouter Initialization ---
api_router = APIRouter()


# --- HTML serving endpoint for the main dashboard ---
@api_router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
@public_rate_limit
async def get_dashboard(request: Request) -> HTMLResponse:
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
@public_rate_limit
async def get_all_agents(
    request: Request,
    agent_manager: IAgentManager = Depends(get_agent_manager),
) -> List[AgentConfig]:
    """
    Returns the full configuration for all loaded agents.
    """
    return await agent_manager.get_all_agents()


# --- System Status Endpoints ---
@api_router.get("/status", response_model=SystemStatus)
@public_rate_limit
async def get_system_status(
    request: Request,
    tws_client: ITWSClient = Depends(get_tws_client),
) -> SystemStatus:
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
        runtime_metrics.tws_status_requests_success.increment()
        runtime_metrics.tws_workstations_total.set(len(workstations))
        runtime_metrics.tws_jobs_total.set(len(jobs))
        return status
    except Exception as e:
        logger.error("Failed to get TWS system status: %s", e, exc_info=True)
        runtime_metrics.tws_status_requests_failed.increment()
        raise HTTPException(
            status_code=503, detail=f"Falha ao comunicar com o TWS: {e}"
        ) from e


# --- Health Check Endpoints ---
@api_router.get("/health/app", summary="Check Application Health")
@public_rate_limit
def get_app_health(request: Request) -> Dict[str, str]:
    """Returns a simple 'ok' to indicate the FastAPI application is running."""
    return {"status": "ok"}


@api_router.get("/health/tws", summary="Check TWS Connection Health")
@public_rate_limit
async def get_tws_health(
    request: Request,
    tws_client: ITWSClient = Depends(get_tws_client),
) -> Dict[str, str]:
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
@public_rate_limit
def get_metrics(request: Request) -> str:
    """
    Returns application metrics in Prometheus text exposition format.
    """
    return runtime_metrics.generate_prometheus_metrics()


@api_router.post("/chat")
@public_rate_limit
async def chat_endpoint(request: Request, data: Dict[str, Any]) -> Dict[str, str]:
    """Chat endpoint for testing input validation."""
    message = data.get("message", "")
    if "<script>" in message:
        raise HTTPException(status_code=400, detail="XSS detected")
    return {"response": "ok"}


@api_router.post("/sensitive")
@authenticated_rate_limit
async def sensitive_endpoint(request: Request, data: Dict[str, Any]) -> Dict[str, str]:
    """Sensitive endpoint for testing encryption."""
    from resync.core.encryption_service import encryption_service

    encrypted = encryption_service.encrypt(data["data"])
    from resync.core.logger import log_with_correlation

    log_with_correlation(logging.INFO, "Processing sensitive data (encrypted successfully)", component="api")
    return {"encrypted": encrypted}


@api_router.get("/protected")
@authenticated_rate_limit
async def protected_endpoint(request: Request):
    """Protected endpoint for testing authentication."""
    raise HTTPException(status_code=401, detail="Unauthorized")


@api_router.get("/admin/users")
@authenticated_rate_limit
async def admin_users_endpoint(request: Request):
    """Admin endpoint for testing authorization."""
    raise HTTPException(status_code=403, detail="Forbidden")


class ReviewRequest(BaseModel):
    content: str = Field(..., max_length=1000)  # noqa: F821


@api_router.post("/review")
@public_rate_limit
async def review_endpoint(request: Request, data: ReviewRequest):
    """Review endpoint for testing input validation."""
    if "<script>" in data.content:
        raise HTTPException(status_code=400, detail="XSS detected")
    return {"status": "reviewed"}


class ExecuteRequest(BaseModel):
    command: str


@api_router.post("/execute")
@public_rate_limit
async def execute_endpoint(request: Request, data: ExecuteRequest) -> Dict[str, str]:
    """Execute endpoint for testing input validation."""
    forbidden_commands = ["rm", "del", ";", "`", "$"]
    if any(cmd in data.command for cmd in forbidden_commands):
        raise HTTPException(status_code=400, detail="Invalid command")
    return {"result": "executed"}


@api_router.get("/files/{path:path}")
@public_rate_limit
async def files_endpoint(request: Request, path: str) -> Dict[str, str]:
    """Files endpoint for testing path traversal."""
    if ".." in path or path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid path")
    return {"path": path}


# --- TWS Monitoring Endpoints ---
@api_router.get("/monitoring/metrics", summary="Get TWS Performance Metrics")
@authenticated_rate_limit
async def get_tws_metrics(request: Request) -> Dict[str, Any]:
    """
    Returns comprehensive TWS performance metrics including:
    - API performance
    - Cache hit ratios
    - LLM usage and costs
    - Circuit breaker status
    - Memory usage
    """
    return tws_monitor.get_performance_report()


@api_router.get("/monitoring/alerts", summary="Get Recent System Alerts")
@authenticated_rate_limit
async def get_tws_alerts(request: Request, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Returns recent system alerts and warnings.

    Args:
        limit: Maximum number of alerts to return (default: 10)
    """
    return tws_monitor.get_alerts(limit=limit)


@api_router.get("/monitoring/health", summary="Get TWS System Health")
@authenticated_rate_limit
async def get_tws_health_monitoring(request: Request) -> Dict[str, Any]:  # Renamed to avoid conflict
    """
    Returns overall TWS system health status.
    """
    performance_report = tws_monitor.get_performance_report()

    # Determine health status
    critical_alerts = [
        alert
        for alert in performance_report["alerts"]
        if alert["severity"] == "critical"
    ]

    warning_alerts = [
        alert
        for alert in performance_report["alerts"]
        if alert["severity"] == "warning"
    ]

    if critical_alerts:
        status = "critical"
    elif warning_alerts:
        status = "warning"
    else:
        status = "healthy"

    return {
        "status": status,
        "critical_alerts": len(critical_alerts),
        "warning_alerts": len(warning_alerts),
        "last_updated": performance_report["current_metrics"].get("timestamp"),
    }
