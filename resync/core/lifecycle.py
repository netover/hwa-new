from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from time import time as time_func
from typing import Any, AsyncGenerator, Dict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from watchfiles import awatch
import pybreaker

from resync.core.agent_manager import agent_manager
from resync.core.app_context import AppContext
from resync.core.cache_hierarchy import get_cache_hierarchy
from resync.core.config_watcher import handle_config_change
from resync.core.di_container import get_container, ServiceScope
from resync.core.exceptions import ConfigError, FileProcessingError
from resync.core.fastapi_di import inject_container
from resync.core.file_ingestor import FileIngestor, load_existing_rag_documents
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.interfaces import IFileIngestor, IKnowledgeGraph
from resync.core.logger import log_with_correlation
from resync.core.rag_watcher import watch_rag_directory
from resync.core.resilience import circuit_breaker_manager
from resync.core.security import InputSanitizer
from resync.core.tws_monitor import tws_monitor
from resync.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def managed_cache_hierarchy(correlation_id: str):
    """Context manager for Cache Hierarchy with automatic cleanup."""
    cache = None
    try:
        log_with_correlation(
            logging.INFO,
            "Initializing Cache Hierarchy",
            correlation_id=correlation_id,
            component="cache_manager",
            operation="init_begin",
        )

        cache = get_cache_hierarchy()
        await cache.start()

        log_with_correlation(
            logging.INFO,
            "Cache Hierarchy initialized successfully",
            correlation_id=correlation_id,
            component="cache_manager",
            operation="init_complete",
        )

        yield cache

    except Exception as e:
        log_with_correlation(
            logging.ERROR,
            "Failed to initialize Cache Hierarchy",
            correlation_id=correlation_id,
            component="cache_manager",
            operation="init_error",
            error=e,
        )
        raise
    finally:
        if cache and hasattr(cache, "is_running") and cache.is_running:
            try:
                await cache.stop()
                log_with_correlation(
                    logging.INFO,
                    "Cache Hierarchy stopped successfully",
                    correlation_id=correlation_id,
                    component="cache_manager",
                    operation="cleanup_complete",
                )
            except Exception as e:
                log_with_correlation(
                    logging.ERROR,
                    "Error stopping Cache Hierarchy",
                    correlation_id=correlation_id,
                    component="cache_manager",
                    operation="cleanup_error",
                    error=e,
                )


@asynccontextmanager
async def managed_tws_monitor(correlation_id: str):
    """Context manager for TWS Monitor with automatic cleanup."""
    try:
        log_with_correlation(
            logging.INFO,
            "Initializing TWS Monitor",
            correlation_id=correlation_id,
            component="tws_monitor_manager",
            operation="init_begin",
        )

        await tws_monitor.start_monitoring()

        log_with_correlation(
            logging.INFO,
            "TWS Monitor initialized successfully",
            correlation_id=correlation_id,
            component="tws_monitor_manager",
            operation="init_complete",
        )

        yield tws_monitor

    except Exception as e:
        log_with_correlation(
            logging.ERROR,
            "Failed to initialize TWS Monitor",
            correlation_id=correlation_id,
            component="tws_monitor_manager",
            operation="init_error",
            error=e,
        )
        raise
    finally:
        if hasattr(tws_monitor, "is_monitoring") and tws_monitor.is_monitoring:
            try:
                await tws_monitor.stop_monitoring()
                log_with_correlation(
                    logging.INFO,
                    "TWS Monitor stopped successfully",
                    correlation_id=correlation_id,
                    component="tws_monitor_manager",
                    operation="cleanup_complete",
                )
            except Exception as e:
                log_with_correlation(
                    logging.ERROR,
                    "Error stopping TWS Monitor",
                    correlation_id=correlation_id,
                    component="tws_monitor_manager",
                    operation="cleanup_error",
                    error=e,
                )


@asynccontextmanager
async def managed_scheduler(correlation_id: str):
    """Context manager for AsyncIOScheduler with automatic cleanup."""
    scheduler = None
    try:
        log_with_correlation(
            logging.INFO,
            "Initializing Scheduler",
            correlation_id=correlation_id,
            component="scheduler_manager",
            operation="init_begin",
        )

        scheduler = await initialize_schedulers()

        log_with_correlation(
            logging.INFO,
            "Scheduler initialized successfully",
            correlation_id=correlation_id,
            component="scheduler_manager",
            operation="init_complete",
        )

        yield scheduler

    except Exception as e:
        log_with_correlation(
            logging.ERROR,
            "Failed to initialize Scheduler",
            correlation_id=correlation_id,
            component="scheduler_manager",
            operation="init_error",
            error=e,
        )
        raise
    finally:
        if scheduler and hasattr(scheduler, "running") and scheduler.running:
            try:
                scheduler.shutdown()
                log_with_correlation(
                    logging.INFO,
                    "Scheduler stopped successfully",
                    correlation_id=correlation_id,
                    component="scheduler_manager",
                    operation="cleanup_complete",
                )
            except Exception as e:
                log_with_correlation(
                    logging.ERROR,
                    "Error stopping Scheduler",
                    correlation_id=correlation_id,
                    component="scheduler_manager",
                    operation="cleanup_error",
                    error=e,
                )


@asynccontextmanager
async def managed_background_tasks(correlation_id: str):
    """Context manager for background tasks with asyncio.TaskGroup supervision."""
    task_group = None
    supervised_tasks = {}

    try:
        log_with_correlation(
            logging.INFO,
            "Initializing background tasks with TaskGroup supervision",
            correlation_id=correlation_id,
            component="background_manager",
            operation="init_begin",
        )

        async with asyncio.TaskGroup() as task_group:
            config_watcher_task = task_group.create_task(
                watch_config_changes(settings.AGENT_CONFIG_PATH),
                name="config_watcher",
            )
            supervised_tasks["config_watcher"] = config_watcher_task

            container = get_container()
            file_ingestor = await container.get(IFileIngestor)

            rag_watcher_task = task_group.create_task(
                watch_rag_directory(file_ingestor), name="rag_watcher"
            )
            supervised_tasks["rag_watcher"] = rag_watcher_task

            log_with_correlation(
                logging.INFO,
                f"Background tasks started under supervision: {list(supervised_tasks.keys())}",
                correlation_id=correlation_id,
                component="background_manager",
                operation="init_complete",
                task_count=len(supervised_tasks),
            )

            yield supervised_tasks

    except Exception as e:
        if hasattr(e, "exceptions"):  # ExceptionGroup
            log_with_correlation(
                logging.ERROR,
                f"Background task supervision failed with {len(e.exceptions)} exceptions",
                correlation_id=correlation_id,
                component="background_manager",
                operation="supervision_error",
                exception_count=len(e.exceptions),
                exceptions=[str(exc) for exc in e.exceptions],
            )
        else:  # Regular exception
            log_with_correlation(
                logging.ERROR,
                "Failed to initialize background task supervision",
                correlation_id=correlation_id,
                component="background_manager",
                operation="init_error",
                error=e,
            )
        raise

    finally:
        log_with_correlation(
            logging.INFO,
            "Background task supervision cleanup completed",
            correlation_id=correlation_id,
            component="background_manager",
            operation="cleanup_complete",
            supervised_tasks_count=len(supervised_tasks),
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Asynchronous context manager for FastAPI application lifecycle events.
    """
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.INFO,
        "--- Resync Application Startup ---",
        correlation_id=correlation_id,
        component="lifespan",
        operation="startup_begin",
    )

    background_tasks = {}

    try:
        try:
            validate_settings()
            log_with_correlation(
                logging.INFO,
                "Configuration validation completed",
                correlation_id=correlation_id,
                component="config",
                operation="validation",
            )
        except ConfigError as e:
            log_with_correlation(
                logging.CRITICAL,
                "Configuration validation failed",
                correlation_id=correlation_id,
                component="config",
                operation="validation",
                error=e,
            )
            raise SystemExit(f"Configuration error: {e}") from e

        try:
            await initialize_core_systems()
            log_with_correlation(
                logging.INFO,
                "Core systems initialized successfully",
                correlation_id=correlation_id,
                component="core",
                operation="initialization",
            )
        except SystemExit as e:
            raise
        except Exception as e:
            log_with_correlation(
                logging.CRITICAL,
                "Failed to initialize core systems",
                correlation_id=correlation_id,
                component="core",
                operation="initialization",
                error=e,
            )
            raise SystemExit(f"Core systems initialization failed: {e}") from e

        async with managed_background_tasks(
            correlation_id
        ) as bg_tasks, managed_cache_hierarchy(
            correlation_id
        ), managed_tws_monitor(
            correlation_id
        ), managed_scheduler(
            correlation_id
        ) as scheduler:
            background_tasks = bg_tasks
            app.state.scheduler = scheduler
            log_with_correlation(
                logging.INFO,
                "All systems initialized successfully",
                correlation_id=correlation_id,
                component="lifespan",
                operation="startup_complete",
            )
            yield

    except (SystemExit, KeyboardInterrupt, ImportError, OSError, ConnectionError, TimeoutError, Exception) as e:
        log_with_correlation(
            logging.CRITICAL,
            "Critical error during startup",
            correlation_id=correlation_id,
            component="lifespan",
            operation="startup_failure",
            error=e,
        )
        raise SystemExit(f"Critical failure during startup: {e}") from e

    finally:
        log_with_correlation(
            logging.INFO,
            "--- Resync Application Shutdown ---",
            correlation_id=correlation_id,
            component="lifespan",
            operation="shutdown_begin",
        )
        try:
            await shutdown_application(app, background_tasks, correlation_id)
        except Exception as e:
            log_with_correlation(
                logging.ERROR,
                "Error during application shutdown",
                correlation_id=correlation_id,
                component="lifespan",
                operation="shutdown",
                error=e,
            )


def validate_paths() -> None:
    """Validate that required paths exist using InputSanitizer."""
    path_configs = [
        ("AGENT_CONFIG_PATH", settings.AGENT_CONFIG_PATH),
        ("RAG_DIR", settings.RAG_DIR),
    ]

    for config_name, path_value in path_configs:
        try:
            InputSanitizer.validate_path_exists(path_value, must_exist=True)
        except (ValueError, FileNotFoundError) as e:
            raise ConfigError(f"Path validation failed: {config_name}={path_value}. {e}") from e


async def validate_runtime_config() -> Dict[str, Any]:
    """
    Runtime configuration validation for long-running services.
    """
    # This function can be further refactored if needed, but for now, it stays here.
    # ... (implementation from main.py)
    return {}


def validate_settings() -> None:
    """Validate critical settings before startup."""
    logger.info("Validating settings...")
    # ... (implementation from main.py)
    required_vars = [
        "TWS_HOST", "TWS_PORT", "AGENT_MODEL_NAME", "LLM_ENDPOINT",
        "AGENT_CONFIG_PATH", "RAG_DIR",
    ]
    missing = [v for v in required_vars if not getattr(settings, v, None)]
    if missing:
        raise ConfigError(f"Missing required settings: {', '.join(missing)}")
    validate_paths()
    logger.info("Settings validation completed successfully")


async def initialize_core_systems() -> None:
    """Initialize core systems with fail-fast behavior."""
    # ... (implementation from main.py)
    correlation_id = AppContext.get_correlation_id()
    try:
        await agent_manager.load_agents_from_config()
        tws_breaker = circuit_breaker_manager.get_breaker("tws_client")
        await tws_breaker.call(agent_manager._get_tws_client)

        from resync.core.knowledge_graph import AsyncKnowledgeGraph
        container = get_container()
        await container.get(AsyncKnowledgeGraph)
        container.register(IKnowledgeGraph, AsyncKnowledgeGraph, ServiceScope.SINGLETON)

        # Register FileIngestor before getting it
        container.register(IFileIngestor, FileIngestor, ServiceScope.SINGLETON)
        file_ingestor = await container.get(IFileIngestor)
        await load_existing_rag_documents(file_ingestor)

    except Exception as e:
        log_with_correlation(logging.CRITICAL, "Core system initialization failed", correlation_id=correlation_id, error=e)
        raise SystemExit("Core system initialization failed") from e


async def initialize_schedulers() -> AsyncIOScheduler:
    """Initialize schedulers with environment-aware configuration."""
    # ... (implementation from main.py)
    scheduler = AsyncIOScheduler()
    job_config = get_auditor_job_config()
    scheduler.add_job(analyze_and_flag_memories, job_config["type"], **job_config["config"])

    config_validation_interval = InputSanitizer.sanitize_environment_value(
        "CONFIG_VALIDATION_INTERVAL_HOURS", os.getenv("CONFIG_VALIDATION_INTERVAL_HOURS", "6"), int
    )
    scheduler.add_job(validate_runtime_config, "interval", hours=max(1, min(config_validation_interval, 24)))

    if job_config.get("startup_enabled", False):
        scheduler.add_job(analyze_and_flag_memories)

    scheduler.start()
    return scheduler


def get_auditor_job_config() -> Dict[str, Any]:
    """Get auditor job configuration based on environment."""
    # ... (implementation from main.py)
    app_env = getattr(settings, "APP_ENV", "production")
    if app_env == "production":
        freq = getattr(settings, "IA_AUDITOR_FREQUENCY_HOURS", 6)
        return {"type": "cron", "config": {"hour": f"*/{int(freq)}"}, "startup_enabled": getattr(settings, "IA_AUDITOR_STARTUP_ENABLED", False)}
    return {"type": "interval", "config": {"minutes": 30}, "startup_enabled": True}


async def shutdown_application(app: FastAPI, background_tasks: Dict[str, asyncio.Task], correlation_id: str) -> None:
    """Shutdown remaining application components."""
    # ... (implementation from main.py)
    if hasattr(agent_manager, "tws_client") and agent_manager.tws_client:
        await agent_manager.tws_client.close()

    try:
        container = get_container()
        kg_instance = await container.get(IKnowledgeGraph)
        if hasattr(kg_instance, "close"):
            await kg_instance.close()
    except KeyError:
        pass # Not registered


@retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(5), reraise=True)
async def watch_config_changes(config_path: Path) -> None:
    """Watches the agent configuration file for changes."""
    # ... (implementation from main.py)
    min_interval = float(os.getenv("CONFIG_WATCHER_MIN_INTERVAL", "1.0"))
    last_change_time = 0.0
    async for _ in awatch(config_path):
        current_time = time_func()
        if current_time - last_change_time > min_interval:
            await handle_config_change()
            last_change_time = current_time