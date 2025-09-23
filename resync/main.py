from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from watchfiles import awatch
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.endpoints import api_router
from resync.core.agent_manager import agent_manager
from resync.core.config_watcher import handle_config_change
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.knowledge_graph import knowledge_graph
from resync.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager for FastAPI application lifecycle events.
    Handles startup and shutdown procedures.
    """
    logger.info("--- Resync Application Startup ---")
    # Initial load of agents from the configuration file
    agent_manager.load_agents_from_config()

    # Start the configuration file watcher in the background
    watcher_task = asyncio.create_task(watch_config_changes(settings.AGENT_CONFIG_PATH))
    logger.info(f"Started configuration watcher for '{settings.AGENT_CONFIG_PATH}'")

    # Initialize the Knowledge Graph
    logger.info("Initializing Knowledge Graph for continuous learning...")
    knowledge_graph  # Ensure it's loaded

    # --- IA Auditor Scheduler ---
    logger.info("Initializing background scheduler for IA Auditor.")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(analyze_and_flag_memories, "cron", hour=2, minute=0)  # Every night at 2 AM
    scheduler.add_job(analyze_and_flag_memories)  # Also run on startup
    scheduler.start()
    app.state.scheduler = scheduler

    yield

    logger.info("--- Resync Application Shutdown ---")
    # Gracefully stop the watcher and scheduler
    watcher_task.cancel()
    if app.state.scheduler:
        app.state.scheduler.shutdown()
        logger.info("IA Auditor scheduler stopped.")
    try:
        await watcher_task
    except asyncio.CancelledError:
        logger.info("Configuration watcher stopped successfully.")

    # Clean up resources
    if agent_manager.tws_client:
        await agent_manager.tws_client.close()
        logger.info("TWS client closed.")


async def watch_config_changes(config_path: Path):
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(config_path):
            await handle_config_change(changes)
    except Exception as e:
        logger.error(f"Error in configuration watcher: {e}", exc_info=True)


# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)

# --- Template Engine ---
templates = Jinja2Templates(directory=settings.BASE_DIR / "templates")

# --- Mount Routers and Static Files ---
app.include_router(api_router, prefix="/api")
app.include_router(chat_router)
app.include_router(audit_router)

app.mount(
    "/static",
    StaticFiles(directory=settings.BASE_DIR / "static"),
    name="static",
)

# --- Frontend Page Endpoints ---
@app.get("/revisao", response_class=HTMLResponse)
async def get_review_page(request: Request):
    """Serves the human review dashboard page."""
    return templates.TemplateResponse("revisao.html", {"request": request})


@app.get("/", include_in_schema=False)
async def root():
    """
    Redirects the root URL to the main API docs page.
    """
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/api/docs", status_code=302)
