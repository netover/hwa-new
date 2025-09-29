from __future__ import annotations

import asyncio
import logging

# Configure logging first
from resync.core.logger import setup_logging

setup_logging()
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Dict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from time import time as time_func # Use time_func for consistency
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pybreaker import CircuitBreaker
from tenacity import retry, stop_after_attempt, wait_random_exponential
from watchfiles import awatch

from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.endpoints import api_router
from resync.api.rag_upload import router as rag_upload_router
from resync.core.agent_manager import agent_manager
from resync.core.config_watcher import handle_config_change
from resync.core.cache_hierarchy import get_cache_hierarchy
from resync.core.file_ingestor import FileIngestor
from resync.core.di_container import get_container
from resync.core.exceptions import ConfigError, FileProcessingError
from resync.core.fastapi_di import inject_container
from resync.core.interfaces import IFileIngestor, IKnowledgeGraph
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.rag_watcher import watch_rag_directory
from resync.core.tws_monitor import tws_monitor
from resync.settings import settings
logger = logging.getLogger(__name__)

# Circuit Breaker for Redis/TWS operations
redis_circuit_breaker = CircuitBreaker(
    fail_max=5,  # Open after 5 failures
    reset_timeout=60,  # Wait 60 seconds before retrying
    name="redis_circuit_breaker",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Asynchronous context manager for FastAPI application lifecycle events.
    Handles startup and shutdown procedures with proper error handling.
    """
    logger.info("--- Resync Application Startup ---")

    # Phase 0: Setup DI (synchronous)
    inject_container(app)

    try:
        # Phase 1: Validate configuration
        validate_settings()

        # Phase 2: Initialize core systems (fail-fast)
        await initialize_core_systems()

        # Phase 3: Start background services
        background_tasks = await start_background_services()

        # Phase 4: Start Cache Hierarchy and Monitoring
        await get_cache_hierarchy().start()
        await tws_monitor.start_monitoring()

        # Phase 5: Initialize schedulers
        app.state.scheduler = await initialize_schedulers()

        logger.info("✅ All systems initialized successfully")

        yield

    except KeyboardInterrupt:
        logger.info("🛑 Application startup interrupted by user")
        raise SystemExit("Startup interrupted by user") from KeyboardInterrupt
    except ImportError as e:
        logger.critical(f"❌ Missing required dependencies: {e}")
        raise SystemExit(f"Dependency error: {e}") from e
    except (OSError, IOError) as e:
        logger.critical(f"❌ File system error during startup: {e}")
        raise SystemExit(f"File system error: {e}") from e
    except Exception as e:
        logger.critical(f"❌ Unexpected error during startup: {e}", exc_info=True)
        raise SystemExit(f"Critical failure during startup: {e}") from e

    finally:
        logger.info("--- Resync Application Shutdown ---")
        await shutdown_application(app, background_tasks)


def validate_settings() -> None:
    """Validate critical settings before startup."""
    logger.info("🔧 Validating settings...")

    required_vars = [
        "TWS_HOST",
        "TWS_PORT",
        "AGENT_MODEL_NAME",
        "LLM_ENDPOINT",
        "AGENT_CONFIG_PATH",
        "RAG_DIR",
    ]
    missing = []

    for var in required_vars:
        value = getattr(settings, var, None)
        if not value or (isinstance(value, str) and not value.strip()):
            missing.append(var)

    if missing:
        error_msg = f"Missing or empty required settings: {', '.join(missing)}"
        logger.critical(f"❌ {error_msg}")
        raise ConfigError(error_msg)

    # Additional validations
    if (
        not isinstance(settings.TWS_PORT, int)
        or settings.TWS_PORT <= 0
        or settings.TWS_PORT > 65535
    ):
        error_msg = f"Invalid TWS_PORT: {settings.TWS_PORT} (must be integer 1-65535)"
        logger.critical(f"❌ {error_msg}")
        raise ConfigError(error_msg)

    if settings.APP_ENV not in ["development", "production", "staging"]:
        error_msg = f"Invalid APP_ENV: {settings.APP_ENV}"
        logger.critical(f"❌ {error_msg}")
        raise ConfigError(error_msg)

    logger.info("✅ Settings validation completed")


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
        with redis_circuit_breaker: # Applying Circuit Breaker to TWS client initialization
            await agent_manager._get_tws_client()
        logger.info("✅ TWS Client initialized")
    except Exception as e:
        logger.critical(f"❌ Failed to initialize TWS Client: {e}")
        raise SystemExit("TWS Client initialization failed") from e

    # Knowledge Graph (required)
    try:
        from resync.core.knowledge_graph import AsyncKnowledgeGraph

        logger.info("Initializing Knowledge Graph for continuous learning...")
        container = get_container()
        knowledge_graph = AsyncKnowledgeGraph()
        container.register_instance(IKnowledgeGraph, knowledge_graph)
        container.register_instance(AsyncKnowledgeGraph, knowledge_graph)
        logger.info("✅ Knowledge Graph initialized and registered")

    except Exception as e:
        logger.critical(f"❌ Failed to initialize Knowledge Graph: {e}")
        raise SystemExit("Knowledge Graph initialization failed") from e

    # File Ingestor (depends on KG)
    try:
        file_ingestor = FileIngestor(knowledge_graph=knowledge_graph)
        container.register_instance(IFileIngestor, file_ingestor)
        logger.info("✅ File Ingestor initialized and registered")
    except Exception as e:
        logger.critical(f"❌ Failed to initialize File Ingestor: {e}")
        raise SystemExit("File Ingestor initialization failed") from e


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
        # Get the file_ingestor instance from the DI container
        container = get_container()
        file_ingestor = container.resolve(IFileIngestor)
        rag_watcher_task = asyncio.create_task(watch_rag_directory(file_ingestor))
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
            analyze_and_flag_memories, job_config["type"], **job_config["config"]
        )

        # Run once on startup for immediate feedback
        if job_config.get("startup_enabled", False):
            scheduler.add_job(analyze_and_flag_memories)

        scheduler.start()
        logger.info(
            f"✅ IA Auditor scheduler initialized with {job_config['type']} schedule: {job_config['config']}"
        )
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

        # Validate frequency_hours
        if not isinstance(frequency_hours, int) or frequency_hours <= 0:
            raise ValueError(
                f"IA_AUDITOR_FREQUENCY_HOURS must be a positive integer, got: {frequency_hours}"
            )

        return {
            "type": "cron",
            "config": {"hour": f"*/{frequency_hours}"},  # Every N hours
            "startup_enabled": startup_enabled,
        }
    elif settings.APP_ENV == "development":
        # Development: More frequent for testing
        return {
            "type": "interval",
            "config": {"minutes": 30},  # Every 30 minutes
            "startup_enabled": True,
        }
    else:
        # Default: Conservative approach
        return {
            "type": "cron",
            "config": {"hour": "*/6"},  # Every 6 hours
            "startup_enabled": True,
        }

async def shutdown_application(
    app: FastAPI, background_tasks: Dict[str, asyncio.Task]
) -> None:
    """Gracefully shutdown all application components."""
    logger.info("🛑 Shutting down application...")

    # Cancel background tasks first (don't await them)
    for task_name, task in background_tasks.items():
        if not task.done():
            task.cancel()
            logger.info(f"✅ {task_name} cancellation requested")

    # Wait for tasks to complete with timeout
    if background_tasks:
        try:
            await asyncio.gather(*background_tasks.values(), return_exceptions=True)
            logger.info("✅ All background tasks completed")
        except Exception as e:
            logger.warning(f"⚠️ Some background tasks had issues during shutdown: {e}")

    # Stop Cache Hierarchy
    try:
        await get_cache_hierarchy().stop()
        logger.info("✅ Cache Hierarchy stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping Cache Hierarchy: {e}")

    # Stop TWS monitoring system
    try:
        await tws_monitor.stop_monitoring()
        logger.info("✅ TWS monitoring system stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping monitoring system: {e}")

    # Stop scheduler
    try:
        if (
            hasattr(app, "state")
            and hasattr(app.state, "scheduler")
            and app.state.scheduler
        ):
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

    # Close Knowledge Graph connection
    try:
        container = get_container()
        if container.is_registered(IKnowledgeGraph):
            kg_instance = container.resolve(IKnowledgeGraph)
            if hasattr(kg_instance, "close"):
                await kg_instance.close()
            logger.info("✅ Knowledge Graph connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing Knowledge Graph connection: {e}")


@retry(
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
    reraise=True,
)
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

# Mount static files if directory exists (for cross-platform compatibility)
static_dir = settings.BASE_DIR / "static"
if static_dir.exists() and static_dir.is_dir():
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
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


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint for monitoring system status.
    """
    health_status = {"status": "healthy", "timestamp": time_func(), "components": {}}

    try:
        # Check TWS Client
        if hasattr(agent_manager, "tws_client") and agent_manager.tws_client:
            # Improved check: Attempt a basic operation or check status
            try:
                # Assuming tws_client has a method to check connection (e.g., is_connected or ping)
                if hasattr(agent_manager.tws_client, "is_connected") and agent_manager.tws_client.is_connected:
                    health_status["components"]["tws_client"] = "connected"
                else:
                    health_status["components"]["tws_client"] = "disconnected"
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["components"]["tws_client"] = f"error: {str(e)}"
                health_status["status"] = "degraded"
        else:
            health_status["components"]["tws_client"] = "not_initialized"
            health_status["status"] = "degraded"

        # Check Scheduler
        if hasattr(app.state, "scheduler") and app.state.scheduler:
            scheduler_running = app.state.scheduler.running
            health_status["components"]["scheduler"] = (
                "running" if scheduler_running else "stopped"
            )
            if not scheduler_running:
                health_status["status"] = "degraded"
        else:
            health_status["components"]["scheduler"] = "not_initialized"
            health_status["status"] = "degraded"

        # Check Knowledge Graph
        try:
            container = get_container()
            # Check if the instance is registered
            if container.is_registered(IKnowledgeGraph):
                health_status["components"]["knowledge_graph"] = "initialized"
            else:
                health_status["components"]["knowledge_graph"] = "not_initialized"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["knowledge_graph"] = f"error: {str(e)}"
            health_status["status"] = "degraded"


        # Check Monitoring System
        try:
            monitoring_stats = tws_monitor.get_current_metrics()
            health_status["components"]["monitoring"] = (
                "active" if monitoring_stats else "inactive"
            )
        except Exception as e:
            health_status["components"]["monitoring"] = f"error: {str(e)}"
            health_status["status"] = "degraded"

    except (ConnectionError, TimeoutError) as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        logger.error(f"Health check failed due to connection issue: {e}")
    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        logger.error(f"Health check failed: {e}")

    return health_status
