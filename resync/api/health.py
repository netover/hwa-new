from __future__ import annotations

import logging
from time import time as time_func
from typing import Any, Dict

from fastapi import APIRouter, Depends

from resync.core.agent_manager import agent_manager
from resync.core.app_context import AppContext
from resync.core.cache_hierarchy import get_cache_hierarchy
from resync.core.di_container import get_container
from resync.core.interfaces import IFileIngestor, IKnowledgeGraph
from resync.core.lifecycle import validate_runtime_config
from resync.core.logger import log_with_correlation
from resync.core.resilience import circuit_breaker_manager
from resync.core.tws_monitor import tws_monitor
from resync.settings import settings

logger = logging.getLogger(__name__)
health_router = APIRouter(prefix="/health", tags=["Health"])
config_router = APIRouter(prefix="/config", tags=["Configuration"])


@health_router.get("/")
async def health_check(app_state: dict = Depends(lambda: {})) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint for monitoring system status.
    """
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.DEBUG,
        "Global health check requested",
        correlation_id=correlation_id,
        component="health",
        operation="global_check",
    )

    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time_func(),
        "correlation_id": correlation_id,
        "components": {},
    }

    try:
        core_health = await health_check_core()
        infra_health = await health_check_infrastructure(app_state)
        services_health = await health_check_services()

        health_status["components"].update(core_health["components"])
        health_status["components"].update(infra_health["components"])
        health_status["components"].update(services_health["components"])

        subsystem_statuses = [
            core_health["status"],
            infra_health["status"],
            services_health["status"],
        ]
        if "error" in subsystem_statuses:
            health_status["status"] = "error"
        elif "degraded" in subsystem_statuses:
            health_status["status"] = "degraded"

    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)

    return health_status


@health_router.get("/di")
async def health_check_di() -> Dict[str, Any]:
    """Health check for Dependency Injection container."""
    container = get_container()
    return await container.get_health_status()


@config_router.get("/validate")
async def validate_config_endpoint() -> Dict[str, Any]:
    """Runtime configuration validation endpoint."""
    return await validate_runtime_config()


@health_router.get("/core")
async def health_check_core() -> Dict[str, Any]:
    """Health check for core application components."""
    status: Dict[str, Any] = {"status": "healthy", "components": {}}
    try:
        container = get_container()
        # Check Agent Manager
        status["components"]["agent_manager"] = "initialized" if agent_manager.agents else "not_initialized"
        # Check Knowledge Graph
        await container.get(IKnowledgeGraph)
        status["components"]["knowledge_graph"] = "initialized"
        # Check File Ingestor
        await container.get(IFileIngestor)
        status["components"]["file_ingestor"] = "initialized"
    except Exception as e:
        status["status"] = "error"
        status["error"] = str(e)
    return status


@health_router.get("/infrastructure")
async def health_check_infrastructure(app_state: dict = Depends(lambda: {})) -> Dict[str, Any]:
    """Health check for infrastructure components."""
    status: Dict[str, Any] = {"status": "healthy", "components": {}}
    # Check Cache
    cache = get_cache_hierarchy()
    status["components"]["cache_hierarchy"] = "running" if cache.is_running else "stopped"
    # Check Scheduler
    scheduler = app_state.get("scheduler")
    status["components"]["scheduler"] = "running" if scheduler and scheduler.running else "stopped"
    # Check TWS Monitor
    status["components"]["tws_monitor"] = "active" if tws_monitor.is_running else "inactive"

    if any(v != "running" and v != "active" for v in status["components"].values()):
        status["status"] = "degraded"
    return status


@health_router.get("/services")
async def health_check_services() -> Dict[str, Any]:
    """Health check for external services."""
    status: Dict[str, Any] = {"status": "healthy", "components": {}}
    # Check TWS Client
    try:
        if agent_manager.tws_client and hasattr(agent_manager.tws_client, "ping"):
            await agent_manager.tws_client.ping()
            status["components"]["tws_client"] = "reachable"
        else:
            status["components"]["tws_client"] = "unknown"
            status["status"] = "degraded"
    except Exception as e:
        status["components"]["tws_client"] = f"error: {str(e)}"
        status["status"] = "degraded"

    # Check Circuit Breakers
    metrics = circuit_breaker_manager.get_all_metrics()
    status["components"]["circuit_breakers"] = metrics
    if any(m.get("circuit_state") == "open" for m in metrics.values()):
        status["status"] = "degraded"

    return status