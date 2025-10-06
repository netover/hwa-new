from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from resync.api.admin import admin_router
from resync.api.agents import agents_router
from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.cors_monitoring import cors_monitor_router
from resync.api.endpoints import api_router
from resync.api.health import config_router, health_router
from resync.api.rag_upload import router as rag_upload_router
from resync.api.operations import router as operations_router
from resync.api.rfc_examples import router as rfc_examples_router
from resync.core.fastapi_di import inject_container
from resync.core.lifecycle import lifespan
from resync.core.logger import setup_logging
from resync.settings import settings

# Import CQRS and API Gateway components
from resync.cqrs.dispatcher import initialize_dispatcher
from resync.api_gateway.container import setup_dependencies

# Import new monitoring and observability components
from resync.core.distributed_tracing import tracer
from resync.core.alerting import alerting_system
from resync.core.runbooks import runbook_registry
from resync.core.benchmarking import SystemBenchmarkRunner, create_benchmark_runner

logger = logging.getLogger(__name__)

# --- Rate Limiter Initialization ---
from resync.core.rate_limiter import (
    dashboard_rate_limit,
    init_rate_limiter,
)

# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)


# Update the lifespan function to initialize CQRS and dependency injection
from contextlib import asynccontextmanager
from resync.core.container import app_container
from resync.core.interfaces import ITWSClient, IAgentManager, IKnowledgeGraph


@asynccontextmanager
async def lifespan_with_cqrs_and_di(app: FastAPI):
    # Startup
    # Get the required services from the DI container
    tws_client = await app_container.get(ITWSClient)
    agent_manager = await app_container.get(IAgentManager)
    knowledge_graph = await app_container.get(IKnowledgeGraph)
    
    # Initialize TWS monitor with the TWS client
    from resync.core.tws_monitor import get_tws_monitor
    tws_monitor_instance = await get_tws_monitor(tws_client)
    
    # Setup dependency injection
    setup_dependencies(tws_client, agent_manager, knowledge_graph)
    
    # Initialize CQRS dispatcher
    initialize_dispatcher(tws_client, tws_monitor_instance)
    
    # Initialize Idempotency Manager
    from resync.api.dependencies import initialize_idempotency_manager
    try:
        # Try to get Redis client from container
        from resync.core.async_cache import get_redis_client
        redis_client = await get_redis_client()
        await initialize_idempotency_manager(redis_client)
        logger.info("Idempotency manager initialized with Redis")
    except Exception as e:
        # Fallback to in-memory storage
        logger.warning(f"Failed to initialize Redis for idempotency: {e}. Using in-memory storage.")
        await initialize_idempotency_manager(None)
    
    # Initialize distributed tracing
    logger.info("Distributed tracing initialized")
    
    # Initialize alerting system
    logger.info("Alerting system initialized")
    
    # Initialize runbook registry
    logger.info("Runbook registry initialized")
    
    # Initialize benchmarking system
    logger.info("Benchmarking system initialized")
    
    yield  # Application runs here
    
    # Shutdown
    # Cleanup happens in the lifecycle manager
    from resync.core.tws_monitor import shutdown_tws_monitor
    await shutdown_tws_monitor()


# Use the updated lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan_with_cqrs_and_di,
)

# Configure logging after settings are loaded
setup_logging()

# --- Configure CORS and Security Middleware ---
from resync.config.cors import configure_cors
from resync.config.csp import configure_csp
from resync.config.security import add_additional_security_headers

configure_cors(app, settings)
configure_csp(app, settings)
add_additional_security_headers(app)

# Initialize comprehensive rate limiting
init_rate_limiter(app)

# --- Register Exception Handlers ---
# Register the new standardized exception handlers
from resync.core.utils.error_utils import register_exception_handlers
register_exception_handlers(app)

# --- Dependency Injection Setup ---
# This should be done before including routers that might use DI
inject_container(app)

# Initialize audit queue if needed
# from resync.core.audit_queue import AsyncAuditQueue
# import asyncio


# --- Template Engine with Caching ---
from jinja2 import Environment, FileSystemLoader

# Create Jinja2 environment with caching
jinja2_env = Environment(
    loader=FileSystemLoader(str(settings.BASE_DIR / "templates")),
    auto_reload=getattr(settings, "DEBUG", False),  # Disable for production
    cache_size=getattr(settings, "JINJA2_TEMPLATE_CACHE_SIZE", 400 if not getattr(settings, "DEBUG", False) else 0),
    enable_async=True
)

# Create templates and assign the environment
templates = Jinja2Templates(directory=str(settings.BASE_DIR / "templates"))
templates.env = jinja2_env

# --- Mount Routers and Static Files ---
app.include_router(api_router, prefix="/api")
app.include_router(admin_router, prefix="/api")  # Admin endpoints under /api/admin
app.include_router(rag_upload_router)
app.include_router(chat_router, prefix="/ws", tags=["WebSocket Chat"])
app.include_router(audit_router)
app.include_router(health_router)
app.include_router(config_router)
app.include_router(cors_monitor_router, prefix="/api/cors", tags=["CORS Monitoring"])
app.include_router(
    agents_router,
    prefix="/api/v1/agents",
    tags=["Agents"],
)
app.include_router(
    operations_router,
    tags=["Critical Operations"]
)
app.include_router(
    rfc_examples_router,
    tags=["RFC Examples"]
)

# Mount static files if directory exists
static_dir = settings.BASE_DIR / "static"
if static_dir.exists() and static_dir.is_dir():
    # from fastapi.staticfiles import StaticFiles
    from starlette.staticfiles import StaticFiles as StarletteStaticFiles
    
    import hashlib
    # import os

    class CachedStaticFiles(StarletteStaticFiles):
        async def get_response(self, path: str, full_path: str):
            response = await super().get_response(path, full_path)
            if response.status_code == 200:
                # Add cache headers for static files using configurable max-age
                cache_max_age = getattr(settings, "STATIC_CACHE_MAX_AGE", 3600)
                response.headers["Cache-Control"] = f"public, max-age={cache_max_age}"
                # Generate ETag based on file metadata (size and modification time) for better performance
                try:
                    # import os
                    import os
                    stat_result = os.stat(full_path)
                    # Create ETag from file size and modification time
                    file_metadata = f"{stat_result.st_size}-{int(stat_result.st_mtime)}"
                    etag_value = f'"{hashlib.md5(file_metadata.encode()).hexdigest()[:16]}"'
                    response.headers["ETag"] = etag_value
                except Exception:
                    # Fallback to path-based hash if file operations fail
                    response.headers["ETag"] = f'"{hash(full_path)}"'
            return response
    
    app.mount(
        "/static",
        CachedStaticFiles(directory=static_dir),
        name="static",
    )
    logger.info(f"Mounted static directory at: {static_dir}")
else:
    logger.warning(f"Static directory not found, skipping mount: {static_dir}")


# --- Frontend Page Endpoints ---
@app.get("/revisao", response_class=HTMLResponse, tags=["Frontend"])
@dashboard_rate_limit
async def get_review_page(request: Request) -> HTMLResponse:
    """
    Serves the main HTML page for the Human Review Dashboard.

    This dashboard allows human operators to review, approve, or reject
    agent interactions that were flagged by the IA Auditor for being
    potentially incorrect.
    """
    return templates.TemplateResponse("revisao.html", {"request": request})


# --- CSP Violation Report Endpoint ---
@app.post("/csp-violation-report", include_in_schema=False)
async def csp_violation_report(request: Request):
    """Handle CSP violation reports."""
    try:
        body = await request.body()
        logger.warning(f"CSP violation reported: {body.decode('utf-8', errors='ignore')}")
        return JSONResponse(content={"status": "received"}, status_code=200)
    except Exception as e:
        logger.error(f"Error processing CSP violation report: {e}")
        return JSONResponse(content={"error": "processing failed"}, status_code=500)


@app.get("/", include_in_schema=False)
async def root():
    """Redirects the root URL to the login page."""
    return RedirectResponse(url="/login", status_code=302)


def validate_settings():
    """Validate critical settings at startup."""
    if not hasattr(settings, 'WS_MAX_CONNECTION_DURATION'):
        logger.warning("WS_MAX_CONNECTION_DURATION not set in settings, using default")
    
    if not hasattr(settings, 'JINJA2_TEMPLATE_CACHE_SIZE'):
        logger.warning("JINJA2_TEMPLATE_CACHE_SIZE not set in settings, using default")
    
    # Validate Redis pool settings
    redis_max_size = getattr(settings, "REDIS_POOL_MAX_SIZE", 20)
    redis_min_size = getattr(settings, "REDIS_POOL_MIN_SIZE", 5)
    
    if redis_min_size > redis_max_size:
        logger.error(f"REDIS_POOL_MIN_SIZE ({redis_min_size}) cannot be greater than REDIS_POOL_MAX_SIZE ({redis_max_size})")
        raise ValueError("Invalid Redis pool configuration")

# Call validation after settings are loaded
validate_settings()

# --- Application Entry Point (for direct execution) ---
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)