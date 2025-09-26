from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from watchfiles import awatch

from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.endpoints import api_router
from resync.api.rag_upload import router as rag_upload_router
from resync.core.agent_manager import agent_manager
from resync.core.config_watcher import handle_config_change
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.rag_watcher import watch_rag_directory
from resync.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous context manager for FastAPI application lifecycle events.
    Handles startup and shutdown procedures.
    """
    logger.info("--- Resync Application Startup ---")
    # Initial load of agents from the configuration file
    await agent_manager.load_agents_from_config()

    # Start background watchers
    config_watcher_task = asyncio.create_task(
        watch_config_changes(settings.AGENT_CONFIG_PATH)
    )
    logger.info(f"Started configuration watcher for '{settings.AGENT_CONFIG_PATH}'")

    rag_watcher_task = asyncio.create_task(watch_rag_directory())
    logger.info("Started RAG directory watcher.")

    # Initialize the Knowledge Graph
    logger.info("Initializing Knowledge Graph for continuous learning...")

    # --- IA Auditor Scheduler ---
    logger.info("Initializing background scheduler for IA Auditor.")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        analyze_and_flag_memories, "cron", hour=2, minute=0
    )  # Every night at 2 AM
    scheduler.add_job(analyze_and_flag_memories)  # Also run on startup
    scheduler.start()
    app.state.scheduler = scheduler

    yield

    logger.info("--- Resync Application Shutdown ---")
    # Gracefully stop the watchers and scheduler
    config_watcher_task.cancel()
    rag_watcher_task.cancel()
    if app.state.scheduler:
        app.state.scheduler.shutdown()
        logger.info("IA Auditor scheduler stopped.")
    try:
        await config_watcher_task
    except asyncio.CancelledError:
        logger.info("Configuration watcher stopped successfully.")
    try:
        await rag_watcher_task
    except asyncio.CancelledError:
        logger.info("RAG directory watcher stopped successfully.")

    # Clean up resources
    if agent_manager.tws_client:
        await agent_manager.tws_client.close()
        logger.info("TWS client closed.")


async def x_watch_config_changes__mutmut_orig(config_path: Path):
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(config_path):
            await handle_config_change(changes)
    except Exception as e:
        logger.error(f"Error in configuration watcher: {e}", exc_info=True)


async def x_watch_config_changes__mutmut_1(config_path: Path):
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(None):
            await handle_config_change(changes)
    except Exception as e:
        logger.error(f"Error in configuration watcher: {e}", exc_info=True)


async def x_watch_config_changes__mutmut_2(config_path: Path):
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(config_path):
            await handle_config_change(None)
    except Exception as e:
        logger.error(f"Error in configuration watcher: {e}", exc_info=True)


async def x_watch_config_changes__mutmut_3(config_path: Path):
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(config_path):
            await handle_config_change(changes)
    except Exception:
        logger.error(None, exc_info=True)


async def x_watch_config_changes__mutmut_4(config_path: Path):
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(config_path):
            await handle_config_change(changes)
    except Exception as e:
        logger.error(f"Error in configuration watcher: {e}", exc_info=None)


async def x_watch_config_changes__mutmut_5(config_path: Path):
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(config_path):
            await handle_config_change(changes)
    except Exception:
        logger.error(exc_info=True)


async def x_watch_config_changes__mutmut_6(config_path: Path):
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(config_path):
            await handle_config_change(changes)
    except Exception as e:
        logger.error(
            f"Error in configuration watcher: {e}",
        )


async def x_watch_config_changes__mutmut_7(config_path: Path):
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(config_path):
            await handle_config_change(changes)
    except Exception as e:
        logger.error(f"Error in configuration watcher: {e}", exc_info=False)


x_watch_config_changes__mutmut_mutants: ClassVar[MutantDict] = {
    "x_watch_config_changes__mutmut_1": x_watch_config_changes__mutmut_1,
    "x_watch_config_changes__mutmut_2": x_watch_config_changes__mutmut_2,
    "x_watch_config_changes__mutmut_3": x_watch_config_changes__mutmut_3,
    "x_watch_config_changes__mutmut_4": x_watch_config_changes__mutmut_4,
    "x_watch_config_changes__mutmut_5": x_watch_config_changes__mutmut_5,
    "x_watch_config_changes__mutmut_6": x_watch_config_changes__mutmut_6,
    "x_watch_config_changes__mutmut_7": x_watch_config_changes__mutmut_7,
}


def watch_config_changes(*args, **kwargs):
    result = _mutmut_trampoline(
        x_watch_config_changes__mutmut_orig,
        x_watch_config_changes__mutmut_mutants,
        args,
        kwargs,
    )
    return result


watch_config_changes.__signature__ = _mutmut_signature(
    x_watch_config_changes__mutmut_orig
)
x_watch_config_changes__mutmut_orig.__name__ = "x_watch_config_changes"


# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)

# --- Middleware Setup ---
# app.middleware("http")(oauth2_middleware)

# --- Template Engine ---
templates = Jinja2Templates(directory=settings.BASE_DIR / "templates")

# --- Mount Routers and Static Files ---
app.include_router(api_router, prefix="/api")
app.include_router(rag_upload_router)
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
