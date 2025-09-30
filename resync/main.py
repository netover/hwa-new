from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Configure logging at the very beginning
from resync.core.logger import setup_logging
setup_logging()

from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.endpoints import api_router
from resync.api.health import config_router, health_router
from resync.api.rag_upload import router as rag_upload_router
from resync.core.fastapi_di import inject_container
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

# --- Template Engine ---
templates = Jinja2Templates(directory=settings.BASE_DIR / "templates")

# --- Mount Routers and Static Files ---
app.include_router(api_router, prefix="/api")
app.include_router(rag_upload_router)
app.include_router(chat_router)
app.include_router(audit_router)
app.include_router(health_router)
app.include_router(config_router)

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