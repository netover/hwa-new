from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Configure logging at the very beginning
from resync.core.logger import setup_logging
setup_logging()

from resync.api.agents import agents_router
from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.endpoints import api_router
from resync.api.health import config_router, health_router
from resync.api.rag_upload import router as rag_upload_router
from resync.core.fastapi_di import inject_container
from resync.core.exceptions import (
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
from resync.settings import settings

logger = logging.getLogger(__name__)

# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)

# --- Dependency Injection Setup ---
# This should be done before including routers that might use DI
inject_container(app)

# --- Global Exception Handler ---
@app.exception_handler(ResyncException)
async def resync_exception_handler(request: Request, exc: ResyncException):
    """
    Global exception handler to catch all custom exceptions inheriting
    from ResyncException and return a standardized HTTP response.
    """
    status_code = 500  # Default for unexpected internal errors
    error_type = type(exc).__name__
    detail = str(exc)

    if isinstance(exc, NotFoundError):
        status_code = 404  # Not Found
    elif isinstance(exc, (InvalidConfigError, ParsingError)):
        status_code = 400  # Bad Request
    elif isinstance(exc, TWSConnectionError):
        status_code = 503  # Service Unavailable
    elif isinstance(exc, LLMError):
        status_code = 502  # Bad Gateway

    logger.error(
        f"HTTP Error {status_code} [{error_type}]: {detail} for request {request.method} {request.url.path}",
        exc_info=True,  # Log the full stack trace for debugging
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail, "type": error_type},
    )

# --- Template Engine ---
templates = Jinja2Templates(directory=settings.BASE_DIR / "templates")

# --- Mount Routers and Static Files ---
app.include_router(api_router, prefix="/api")
app.include_router(rag_upload_router)
app.include_router(chat_router, prefix="/ws", tags=["WebSocket Chat"])
app.include_router(audit_router)
app.include_router(health_router)
app.include_router(config_router)
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
async def get_review_page(request: Request) -> HTMLResponse:
    """Serves the human review dashboard page."""
    return templates.TemplateResponse("revisao.html", {"request": request})


@app.get("/", include_in_schema=False)
async def root():
    """Redirects the root URL to the main API docs page."""
    return RedirectResponse(url="/docs", status_code=302)

# --- Application Entry Point (for direct execution) ---
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)