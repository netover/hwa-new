from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from resync.core.dependencies import get_tws_client
from resync.core.metrics import metrics_registry
from resync.models.tws import SystemStatus
from resync.services.tws_service import OptimizedTWSClient

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- APIRouter Initialization ---
api_router = APIRouter()


# --- System Status Endpoints ---
@api_router.get("/status", response_model=SystemStatus)
async def get_system_status(tws_client: OptimizedTWSClient = Depends(get_tws_client)):
    """
    Provides a comprehensive status of the TWS environment, including
    workstations, jobs, and critical path information.
    """
    try:
        status = await tws_client.get_system_status()
        # Record metrics upon successful status retrieval
        metrics_registry.increment_counter("tws_status_requests_success")
        metrics_registry.set_gauge("tws_workstations_total", len(status.workstations))
        metrics_registry.set_gauge("tws_jobs_total", len(status.jobs))
        return status
    except ConnectionError as e:
        logger.error(
            "Failed to get TWS system status due to connection error: %s",
            e,
            exc_info=True,
        )
        metrics_registry.increment_counter("tws_status_requests_failed")
        raise HTTPException(
            status_code=503,
            detail="Service Unavailable: Could not connect to the TWS backend.",
        ) from e
    except Exception as e:
        logger.error(
            "An unexpected error occurred while fetching TWS system status: %s",
            e,
            exc_info=True,
        )
        metrics_registry.increment_counter("tws_status_requests_failed")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: An unexpected error occurred.",
        ) from e


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
        if await tws_client.check_connection():
            return {"status": "ok", "message": "Conexão com o TWS bem-sucedida."}
        raise HTTPException(
            status_code=503,
            detail="Service Unavailable: The connection check to the TWS backend failed.",
        )
    except Exception as e:
        logger.error("TWS health check failed unexpectedly: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: An unexpected error occurred during the health check.",
        ) from e


# --- Metrics Endpoint ---
@api_router.get("/metrics", summary="Get Application Metrics")
def get_metrics():
    """Returns a snapshot of all collected application metrics."""
    return metrics_registry.get_metrics()
