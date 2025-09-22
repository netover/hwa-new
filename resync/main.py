from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from watchfiles import awatch

from resync.api.chat import chat_router
from resync.api.endpoints import api_router
from resync.core.agent_manager import agent_manager
from resync.core.config_watcher import handle_config_change
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

    yield

    logger.info("--- Resync Application Shutdown ---")
    # Gracefully stop the watcher task
    watcher_task.cancel()
    try:
        await watcher_task
    except asyncio.CancelledError:
        logger.info("Configuration watcher stopped successfully.")
    # Clean up resources, like closing the TWS client
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

# --- Mount Routers and Static Files ---
# API routers for application logic
app.include_router(api_router, prefix="/api")
app.include_router(chat_router)

# Serve static files (CSS, JS) from the 'static' directory
app.mount("/static", StaticFiles(directory=settings.BASE_DIR / "static"), name="static")

# Serve the main dashboard html file from the 'templates' directory
app.mount(
    "/dashboard",
    StaticFiles(directory=settings.BASE_DIR / "templates", html=True),
    name="dashboard",
)


# --- Root Endpoint ---
@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    """
    Redirects the root URL to the main dashboard page.
    This is a convenience for users accessing the base URL.
    """
    return RedirectResponse(url="/dashboard/index.html", status_code=302)
