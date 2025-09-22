from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from resync.core.dependencies import get_tws_client
from resync.core.metrics import metrics_registry
from resync.models.tws import (
    CriticalJob,
    JobStatus,
    SystemStatus,
    WorkstationStatus,
)
from resync.services.tws_service import OptimizedTWSClient
from resync.settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- APIRouter Initialization ---
api_router = APIRouter()


# --- HTML serving endpoint for the main dashboard ---
@api_router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def get_dashboard():
    """
    Serves the main `index.html` file for the dashboard.
    """
    index_path = settings.BASE_DIR / "templates" / "index.html"
    if not index_path.exists():
        logger.error("Dashboard index.html not found at path: %s", index_path)
        raise HTTPException(status_code=404, detail="Interface do dashboard não encontrada.")
    return index_path.read_text()


# --- System Status Endpoints ---
@api_router.get("/status", response_model=SystemStatus)
async def get_system_status(tws_client: OptimizedTWSClient = Depends(get_tws_client)):
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
        )


# --- Health Check Endpoints ---
@api_router.get("/health/app", summary="Check Application Health")
def get_app_health():
    """Returns a simple 'ok' to indicate the FastAPI application is running."""
    return {"status": "ok"}


@api_router.get("/health/tws", summary="Check TWS Connection Health")
async def get_tws_health(tws_client: OptimizedTWSClient = Depends(get_tws_client)):
    """
    Performs a quick check to verify the connection to the TWS server is active.
    """
    try:
        is_connected = await tws_client.check_connection()
        if is_connected:
            return {"status": "ok", "message": "Conexão com o TWS bem-sucedida."}
        else:
            raise HTTPException(status_code=503, detail="A verificação da conexão com o TWS falhou.")
    except Exception as e:
        logger.error("TWS health check failed: %s", e, exc_info=True)
        raise HTTPException(status_code=503, detail=f"Falha na conexão com o TWS: {e}")


# --- Metrics Endpoint ---
@api_router.get("/metrics", summary="Get Application Metrics")
def get_metrics():
    """Returns a snapshot of all collected application metrics."""
    return metrics_registry.get_metrics()
