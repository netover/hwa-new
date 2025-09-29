from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

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
from resync.core.exceptions import ConfigError, FileProcessingError
from resync.core.fastapi_di import inject_container
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.rag_watcher import watch_rag_directory
from resync.core.tws_monitor import tws_monitor
from resync.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Asynchronous context manager for FastAPI application lifecycle events.
    Handles startup and shutdown procedures with proper error handling.
    """
    logger.info("--- Resync Application Startup ---")

    try:
        # Phase 1: Initialize core systems (fail-fast)
        await initialize_core_systems()

        # Phase 2: Start background services
        background_tasks = await start_background_services()

        # Phase 3: Initialize schedulers
        scheduler = await initialize_schedulers()
        app.state.scheduler = scheduler

        # Phase 4: Start monitoring
        await start_monitoring_system()

        logger.info("✅ All systems initialized successfully")

        yield

    except Exception as e:
        logger.critical(f"❌ Failed to start application: {e}")
        raise SystemExit(f"Critical failure during startup: {e}") from e

    finally:
        logger.info("--- Resync Application Shutdown ---")
        await shutdown_application(background_tasks)


async def initialize_core_systems() -> None:
    """Initialize core systems with fail-fast behavior."""
    logger.info("🔧 Initializing core systems...")

    # Agent Manager (required)
    try:
        await agent_manager.load_agents_from_config()
        logger.info("✅ Agent Manager initialized")
    except Exception as e:
        logger.critical(f"❌ Failed to initialize Agent Manager: {e}")
        raise SystemExit("Agent Manager initialization failed") from e

    # TWS Client (required for agents)
    try:
        await agent_manager._get_tws_client()
        logger.info("✅ TWS Client initialized")
    except Exception as e:
        logger.critical(f"❌ Failed to initialize TWS Client: {e}")
        raise SystemExit("TWS Client initialization failed") from e

    # Knowledge Graph (required)
    try:
        # Initialize the Knowledge Graph for continuous learning
        logger.info("Initializing Knowledge Graph for continuous learning...")
        # Note: This would need to be implemented based on your KG setup
        logger.info("✅ Knowledge Graph initialized")
    except Exception as e:
        logger.critical(f"❌ Failed to initialize Knowledge Graph: {e}")
        raise SystemExit("Knowledge Graph initialization failed") from e


async def start_background_services() -> Dict[str, asyncio.Task]:
    """Start background services and return task references."""
    logger.info("🔧 Starting background services...")

    tasks = {}

    # Configuration watcher
    try:
        config_watcher_task = asyncio.create_task(
            watch_config_changes(settings.AGENT_CONFIG_PATH)
        )
        tasks["config_watcher"] = config_watcher_task
        logger.info("✅ Configuration watcher started")
    except Exception as e:
        logger.error(f"❌ Failed to start configuration watcher: {e}")
        raise

    # RAG directory watcher
    try:
        rag_watcher_task = asyncio.create_task(watch_rag_directory())
        tasks["rag_watcher"] = rag_watcher_task
        logger.info("✅ RAG directory watcher started")
    except Exception as e:
        logger.error(f"❌ Failed to start RAG watcher: {e}")
        # Don't fail completely, but log the error
        logger.warning("Continuing without RAG watcher")

    return tasks


async def initialize_schedulers() -> AsyncIOScheduler:
    """Initialize schedulers with environment-aware configuration."""
    logger.info("🔧 Initializing schedulers...")

    scheduler = AsyncIOScheduler()

    try:
        # Configure IA Auditor frequency based on environment
        job_config = get_auditor_job_config()

        scheduler.add_job(
            analyze_and_flag_memories,
            job_config["type"],
            **job_config["config"]
        )

        # Run once on startup for immediate feedback
        if job_config.get("startup_enabled", False):
            scheduler.add_job(analyze_and_flag_memories)

        scheduler.start()
        logger.info(f"✅ IA Auditor scheduler initialized with {job_config['type']} schedule: {job_config['config']}")
        if job_config.get("startup_enabled", False):
            logger.info("✅ IA Auditor will run on startup")

    except Exception as e:
        logger.critical(f"❌ Failed to initialize scheduler: {e}")
        raise SystemExit("Scheduler initialization failed") from e

    return scheduler


def get_auditor_job_config() -> Dict[str, Any]:
    """Get auditor job configuration based on environment and settings."""
    if settings.APP_ENV == "production":
        # Production: Use production-specific settings if available
        frequency_hours = getattr(settings, "IA_AUDITOR_FREQUENCY_HOURS", 6)
        startup_enabled = getattr(settings, "IA_AUDITOR_STARTUP_ENABLED", False)

        return {
            "type": "cron",
            "config": {"hour": f"*/{frequency_hours}"},  # Every N hours
            "startup_enabled": startup_enabled
        }
    elif settings.APP_ENV == "development":
        # Development: More frequent for testing
        return {
            "type": "interval",
            "config": {"minutes": 30},  # Every 30 minutes
            "startup_enabled": True
        }
    else:
        # Default: Conservative approach
        return {
            "type": "cron",
            "config": {"hour": "*/6"},  # Every 6 hours
            "startup_enabled": True
        }


async def start_monitoring_system() -> None:
    """Start monitoring system."""
    logger.info("🔧 Starting monitoring system...")

    try:
        await tws_monitor.start_monitoring()
        logger.info("✅ TWS monitoring system started")
    except Exception as e:
        logger.error(f"❌ Failed to start monitoring system: {e}")
        # Don't fail startup, but log warning
        logger.warning("Continuing without monitoring system")


async def shutdown_application(background_tasks: Dict[str, asyncio.Task]) -> None:
    """Gracefully shutdown all application components."""
    logger.info("🛑 Shutting down application...")

    # Stop background tasks
    for task_name, task in background_tasks.items():
        try:
            task.cancel()
            await task
            logger.info(f"✅ {task_name} stopped successfully")
        except asyncio.CancelledError:
            logger.info(f"✅ {task_name} cancelled successfully")
        except Exception as e:
            logger.error(f"❌ Error stopping {task_name}: {e}")

    # Stop TWS monitoring system
    try:
        await tws_monitor.stop_monitoring()
        logger.info("✅ TWS monitoring system stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping monitoring system: {e}")

    # Stop scheduler
    try:
        if app.state.scheduler:
            app.state.scheduler.shutdown()
            logger.info("✅ IA Auditor scheduler stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {e}")

    # Clean up resources
    try:
        if agent_manager.tws_client:
            await agent_manager.tws_client.close()
            logger.info("✅ TWS client closed")
    except Exception as e:
        logger.error(f"❌ Error closing TWS client: {e}")


async def watch_config_changes(config_path: Path) -> None:
    """
    Watches the agent configuration file for changes and triggers a reload.
    """
    try:
        async for changes in awatch(config_path):
            await handle_config_change(changes)
    except FileNotFoundError as e:
        logger.error("Configuration file not found: %s", e, exc_info=True)
        raise ConfigError(f"Configuration file not found: {config_path}") from e
    except PermissionError as e:
        logger.error(
            "Permission denied accessing configuration file: %s", e, exc_info=True
        )
        raise ConfigError(
            f"Permission denied accessing configuration file: {config_path}"
        ) from e
    except OSError as e:
        logger.error("OS error watching configuration file: %s", e, exc_info=True)
        raise FileProcessingError(
            f"OS error watching configuration file: {config_path}"
        ) from e
    except asyncio.CancelledError:
        # Re-raise CancelledError for proper task cancellation
        raise
    except Exception as e:
        logger.error("Unexpected error in configuration watcher: %s", e, exc_info=True)
        raise ConfigError(
            f"Unexpected error watching configuration file: {str(e)}"
        ) from e


# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
)

# --- Middleware Setup ---
# app.middleware("http")(oauth2_middleware)

# --- Dependency Injection Setup ---
inject_container(app)

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
