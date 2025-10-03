from __future__ import annotations

import logging
import redis.asyncio as redis
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from resync.api.agents import agents_router
from resync.api.admin import admin_router
from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.endpoints import api_router
from resync.api.health import config_router, health_router
from resync.api.rag_upload import router as rag_upload_router
from resync.api.cors_monitoring import cors_monitor_router
from resync.core.fastapi_di import inject_container
from resync.core.exceptions_enhanced import (
    ResyncException,
    ConfigurationError,
    NotFoundError,
    ParsingError,
    TWSConnectionError,
    LLMError,
    InvalidConfigError,
)
from fastapi.responses import JSONResponse
from resync.core.lifecycle import lifespan
from resync.core.logger import setup_logging
from resync.api.middleware.csp_middleware import create_csp_middleware
from resync.api.middleware.cors_middleware import create_cors_middleware, add_cors_middleware
from resync.settings import settings

logger = logging.getLogger(__name__)

# --- Rate Limiter Initialization ---
from resync.core.rate_limiter import init_rate_limiter, error_handler_rate_limit, dashboard_rate_limit
# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)

# Configure logging after settings are loaded
setup_logging()

# --- Add CORS Middleware ---
cors_enabled = getattr(settings, "CORS_ENABLED", True)
if cors_enabled:
    cors_environment = getattr(settings, "CORS_ENVIRONMENT", "development")
    
    # Parse allowed origins from settings
    cors_origins_str = getattr(settings, "CORS_ALLOWED_ORIGINS", "")
    allowed_origins = []
    if cors_origins_str:
        allowed_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
    
    # Create CORS middleware with environment-specific configuration
    try:
        cors_middleware = create_cors_middleware(
            app=app,
            environment=cors_environment,
        )
        
        # Override with custom origins if provided
        if allowed_origins:
            from resync.api.middleware.cors_config import CORSPolicy, Environment
            custom_policy = CORSPolicy(
                environment=Environment(cors_environment),
                allowed_origins=allowed_origins,
                allow_all_origins=False,
                allow_credentials=getattr(settings, "CORS_ALLOW_CREDENTIALS", False),
                log_violations=getattr(settings, "CORS_LOG_VIOLATIONS", True),
            )
            cors_middleware = create_cors_middleware(
                app=app,
                environment=cors_environment,
                custom_policy=custom_policy
            )
        
        app.add_middleware(type(cors_middleware), **cors_middleware.__dict__)
        logger.info(f"CORS middleware added for environment: {cors_environment}")
    except Exception as e:
        logger.error(f"Failed to add CORS middleware: {e}")
        logger.info("Continuing without CORS middleware")
else:
    logger.info("CORS middleware disabled")

# --- Add CSP Middleware ---
# Create and add CSP middleware
from resync.api.middleware.csp_middleware import CSPMiddleware
csp_enabled = getattr(settings, "CSP_ENABLED", True)
if csp_enabled:
    report_only = getattr(settings, "CSP_REPORT_ONLY", False)
    app.add_middleware(CSPMiddleware, report_only=report_only)
    logger.info(f"CSP middleware added (report_only={report_only})")

# Initialize comprehensive rate limiting
init_rate_limiter(app)

# --- Register Exception Handlers ---
# Register the new standardized exception handlers
register_exception_handlers(app)

# --- Dependency Injection Setup ---
# This should be done before including routers that might use DI
inject_container(app)

# --- Global Exception Handler (Legacy - kept for backward compatibility) ---
@app.exception_handler(ResyncException)
@error_handler_rate_limit
async def resync_exception_handler(request: Request, exc: ResyncException):
    """
    Legacy global exception handler for backward compatibility.
    New code should use the standardized error response system.
    """
    # Use the new standardized error response system
    from resync.core.utils.error_utils import generate_correlation_id
    correlation_id = getattr(request.state, 'correlation_id', generate_correlation_id())
    
    error_response = create_error_response_from_exception(exc, request, correlation_id)
    
    logger.error(
        f"HTTP Error {error_response.error_code} [{type(exc).__name__}]: {exc} for request {request.method} {request.url.path}",
        exc_info=settings.DEBUG,
    )
    
    return create_json_response_from_error(error_response)

# --- Template Engine ---
templates = Jinja2Templates(directory=settings.BASE_DIR / "templates")

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

# Mount static files if directory exists
static_dir = settings.BASE_DIR / "static"
if static_dir.exists() and static_dir.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
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

# --- Application Entry Point (for direct execution) ---
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)