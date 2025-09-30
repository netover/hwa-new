from __future__ import annotations

import asyncio
import ipaddress
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Optional, Union

# Configure logging first
from resync.core.logger import setup_logging

setup_logging()
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from time import time as time_func  # Use time_func for consistency
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pybreaker
from pybreaker import CircuitBreaker
from pydantic import BaseModel, Field, ValidationError, validator
from tenacity import retry, stop_after_attempt, wait_random_exponential
from watchfiles import awatch

from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.endpoints import api_router
from resync.api.rag_upload import router as rag_upload_router
from resync.core.agent_manager import agent_manager
from resync.core.config_watcher import handle_config_change
from resync.core.cache_hierarchy import get_cache_hierarchy
from resync.core.file_ingestor import FileIngestor, load_existing_rag_documents
from resync.core.di_container import get_container, ServiceScope
from resync.core.exceptions import ConfigError, FileProcessingError
from resync.core.fastapi_di import inject_container
from resync.core.interfaces import IFileIngestor, IKnowledgeGraph
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.rag_watcher import watch_rag_directory
from resync.core.tws_monitor import tws_monitor
from resync.settings import settings

logger = logging.getLogger(__name__)


# --- Correlation ID and Structured Logging ---
def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracing."""
    return str(uuid.uuid4())


def log_with_correlation(
    level: int,
    message: str,
    correlation_id: str = None,
    component: str = "main",
    operation: str = None,
    error: Exception = None,
    **extra_fields,
) -> None:
    """
    Structured logging with correlation ID and contextual information.

    Args:
        level: Logging level (logging.INFO, logging.ERROR, etc.)
        message: Log message
        correlation_id: Correlation ID for tracing
        component: Component name (main, tws_client, etc.)
        operation: Operation being performed
        error: Exception object for error logging
        extra_fields: Additional structured fields
    """
    extra = {
        "correlation_id": correlation_id or "system",
        "component": component,
        "operation": operation,
        **extra_fields,
    }

    if error:
        extra["error_type"] = type(error).__name__
        extra["error_message"] = str(error)
        logger.log(level, message, extra=extra, exc_info=error)
    else:
        logger.log(level, message, extra=extra)


class AppContext:
    """Application context for correlation ID management."""

    _current_correlation_id: str = None

    @classmethod
    def get_correlation_id(cls) -> str:
        """Get current correlation ID or generate a new one."""
        if cls._current_correlation_id is None:
            cls._current_correlation_id = generate_correlation_id()
        return cls._current_correlation_id

    @classmethod
    def set_correlation_id(cls, correlation_id: str) -> None:
        """Set correlation ID for current context."""
        cls._current_correlation_id = correlation_id

    @classmethod
    def reset_correlation_id(cls) -> None:
        """Reset correlation ID."""
        cls._current_correlation_id = None


# --- Input Sanitization ---
class SanitizedPath(BaseModel):
    """Sanitized file/directory path with security validations."""

    path: str = Field(..., min_length=1, max_length=4096)

    @validator("path")
    def validate_path(cls, v):
        """Validate path for security issues."""
        if not v or not v.strip():
            raise ValueError("Path cannot be empty")

        # Convert to Path for validation
        path_obj = Path(v).resolve()

        # Check for path traversal attempts
        try:
            path_obj.resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid path resolution: {e}")

        # Prevent absolute paths that could escape intended directories
        if path_obj.is_absolute() and not any(
            str(path_obj).startswith(str(allowed.resolve()))
            for allowed in [Path.cwd(), Path.home()]
        ):
            raise ValueError(
                "Absolute paths outside allowed directories are not permitted"
            )

        # Check for suspicious patterns
        suspicious_patterns = ["..", "\\", "\x00", "\n", "\r"]
        for pattern in suspicious_patterns:
            if pattern in v:
                raise ValueError(f"Path contains suspicious pattern: {pattern}")

        return str(path_obj)


class SanitizedHostPort(BaseModel):
    """Sanitized IP address and port combination."""

    host: str = Field(..., min_length=1, max_length=253)
    port: int = Field(..., ge=1, le=65535)

    @validator("host")
    def validate_host(cls, v):
        """Validate host as IP address or valid hostname."""
        if not v or not v.strip():
            raise ValueError("Host cannot be empty")

        # Remove whitespace
        v = v.strip()

        # Try to parse as IP address first
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            pass

        # Validate as hostname
        if not re.match(
            r"^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*$",
            v,
        ):
            raise ValueError("Invalid hostname format")

        # Prevent localhost/private IPs in production if needed
        # (This could be enhanced based on environment)

        return v

    @validator("port")
    def validate_port(cls, v):
        """Validate port number."""
        # Reserve system ports (1-1023) for privileged operations only
        if v < 1024:
            import warnings

            warnings.warn(
                f"Using privileged port {v} - ensure proper permissions", UserWarning
            )

        # Well-known ports that might be suspicious
        suspicious_ports = [
            22,
            23,
            25,
            53,
            80,
            443,
            3306,
            5432,
        ]  # SSH, Telnet, SMTP, DNS, HTTP, etc.
        if v in suspicious_ports:
            import warnings

            warnings.warn(
                f"Using well-known port {v} - verify this is intended", UserWarning
            )

        return v


class InputSanitizer:
    """Global input sanitization utilities."""

    @staticmethod
    def sanitize_path(path: Union[str, Path]) -> Path:
        """Sanitize and validate file/directory path."""
        try:
            sanitized = SanitizedPath(path=str(path))
            return Path(sanitized.path)
        except ValidationError as e:
            correlation_id = AppContext.get_correlation_id()
            log_with_correlation(
                logging.ERROR,
                f"Path sanitization failed: {path}",
                correlation_id=correlation_id,
                component="input_sanitizer",
                operation="sanitize_path",
                error=e,
                invalid_path=str(path),
            )
            raise ValueError(f"Invalid path: {e}") from e

    @staticmethod
    def sanitize_host_port(host_port: str) -> tuple[str, int]:
        """Sanitize and validate host:port combination."""
        if ":" not in host_port:
            raise ValueError("Host:port format required (host:port)")

        try:
            host, port_str = host_port.rsplit(":", 1)
            port = int(port_str)

            sanitized = SanitizedHostPort(host=host, port=port)
            return sanitized.host, sanitized.port

        except (ValueError, ValidationError) as e:
            correlation_id = AppContext.get_correlation_id()
            log_with_correlation(
                logging.ERROR,
                f"Host:port sanitization failed: {host_port}",
                correlation_id=correlation_id,
                component="input_sanitizer",
                operation="sanitize_host_port",
                error=e,
                invalid_host_port=host_port,
            )
            raise ValueError(f"Invalid host:port format: {e}") from e

    @staticmethod
    def sanitize_environment_value(
        key: str, value: Any, expected_type: type = str
    ) -> Any:
        """Sanitize environment variable value with type validation."""
        if value is None:
            raise ValueError(f"Environment variable {key} is not set")

        try:
            if expected_type == bool:
                # Handle boolean conversion
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "on")
                return bool(value)
            elif expected_type == int:
                return int(value)
            elif expected_type == float:
                return float(value)
            elif expected_type == str:
                # Basic string sanitization
                if not isinstance(value, str):
                    value = str(value)
                value = value.strip()
                if not value:
                    raise ValueError(f"Environment variable {key} cannot be empty")
                return value
            else:
                return expected_type(value)

        except (ValueError, TypeError) as e:
            correlation_id = AppContext.get_correlation_id()
            log_with_correlation(
                logging.ERROR,
                f"Environment variable sanitization failed: {key}={value}",
                correlation_id=correlation_id,
                component="input_sanitizer",
                operation="sanitize_env",
                error=e,
                env_key=key,
                env_value=str(value),
                expected_type=expected_type.__name__,
            )
            raise ValueError(f"Invalid environment variable {key}: {e}") from e

    @staticmethod
    def validate_path_exists(path: Union[str, Path], must_exist: bool = True) -> Path:
        """Validate path exists and is accessible."""
        sanitized_path = InputSanitizer.sanitize_path(path)
        resolved_path = sanitized_path.resolve()

        if must_exist:
            if not resolved_path.exists():
                correlation_id = AppContext.get_correlation_id()
                log_with_correlation(
                    logging.ERROR,
                    f"Required path does not exist: {resolved_path}",
                    correlation_id=correlation_id,
                    component="input_sanitizer",
                    operation="validate_path_exists",
                    path=str(resolved_path),
                )
                raise FileNotFoundError(f"Path does not exist: {resolved_path}")

            # Additional security check - ensure it's not a symlink to outside allowed areas
            if resolved_path.is_symlink():
                target = resolved_path.readlink()
                if not str(target).startswith(str(Path.cwd())):
                    raise ValueError(
                        f"Symlink points outside allowed directory: {resolved_path} -> {target}"
                    )

        return resolved_path


# --- Adaptive Circuit Breaker ---
class AdaptiveCircuitBreaker:
    """Adaptive circuit breaker with configurable thresholds and metrics."""

    def __init__(self, name: str, operation: str):
        self.name = name
        self.operation = operation
        self._metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "circuit_opened_count": 0,
            "last_failure_time": None,
            "failure_streak": 0,
        }
        self._circuit_breaker = None
        self._create_circuit_breaker()

    def _create_circuit_breaker(self):
        """Create circuit breaker with configurable thresholds."""
        # Get configurable thresholds from environment with defaults
        fail_max = InputSanitizer.sanitize_environment_value(
            f"CIRCUIT_BREAKER_{self.operation.upper()}_FAIL_MAX",
            os.getenv(f"CIRCUIT_BREAKER_{self.operation.upper()}_FAIL_MAX", "5"),
            int,
        )
        reset_timeout = InputSanitizer.sanitize_environment_value(
            f"CIRCUIT_BREAKER_{self.operation.upper()}_RESET_TIMEOUT",
            os.getenv(f"CIRCUIT_BREAKER_{self.operation.upper()}_RESET_TIMEOUT", "60"),
            int,
        )

        # Validate ranges
        fail_max = max(1, min(fail_max, 100))  # 1-100
        reset_timeout = max(10, min(reset_timeout, 3600))  # 10 seconds to 1 hour

        self._circuit_breaker = CircuitBreaker(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            name=f"{self.name}_{self.operation}",
            listeners=[self],
        )

        log_with_correlation(
            logging.INFO,
            f"Created adaptive circuit breaker for {self.operation}",
            correlation_id=AppContext.get_correlation_id(),
            component="circuit_breaker",
            operation="create",
            fail_max=fail_max,
            reset_timeout=reset_timeout,
        )

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        correlation_id = AppContext.get_correlation_id()
        self._metrics["total_calls"] += 1

        try:
            result = await self._circuit_breaker.call(func, *args, **kwargs)
            self._metrics["successful_calls"] += 1
            self._metrics["failure_streak"] = 0

            log_with_correlation(
                logging.DEBUG,
                f"Circuit breaker call successful for {self.operation}",
                correlation_id=correlation_id,
                component="circuit_breaker",
                operation="call_success",
                total_calls=self._metrics["total_calls"],
                success_rate=self.get_success_rate(),
            )

            return result

        except pybreaker.CircuitBreakerError as e:
            self._metrics["circuit_opened_count"] += 1
            log_with_correlation(
                logging.WARNING,
                f"Circuit breaker opened for {self.operation}",
                correlation_id=correlation_id,
                component="circuit_breaker",
                operation="circuit_opened",
                error=e,
                opened_count=self._metrics["circuit_opened_count"],
            )
            raise

        except Exception as e:
            self._metrics["failed_calls"] += 1
            self._metrics["failure_streak"] += 1
            self._metrics["last_failure_time"] = time_func()

            log_with_correlation(
                logging.WARNING,
                f"Circuit breaker call failed for {self.operation}",
                correlation_id=correlation_id,
                component="circuit_breaker",
                operation="call_failed",
                error=e,
                failure_streak=self._metrics["failure_streak"],
            )
            raise

    def get_success_rate(self) -> float:
        """Calculate success rate."""
        total = self._metrics["total_calls"]
        if total == 0:
            return 1.0
        return self._metrics["successful_calls"] / total

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        return {
            **self._metrics,
            "success_rate": self.get_success_rate(),
            "circuit_state": self._circuit_breaker.current_state.name
            if self._circuit_breaker
            else "unknown",
            "fail_max": self._circuit_breaker.fail_max if self._circuit_breaker else 0,
            "reset_timeout": self._circuit_breaker.reset_timeout
            if self._circuit_breaker
            else 0,
        }

    # CircuitBreaker listener methods
    def state_change(self, cb, old_state, new_state):
        """Called when circuit breaker state changes."""
        correlation_id = AppContext.get_correlation_id()
        log_with_correlation(
            logging.INFO,
            f"Circuit breaker state changed for {self.operation}: {old_state.name} -> {new_state.name}",
            correlation_id=correlation_id,
            component="circuit_breaker",
            operation="state_change",
            old_state=old_state.name,
            new_state=new_state.name,
        )

    def failure(self, cb, exc):
        """Called on failure."""
        pass  # Already handled in call method

    def success(self, cb):
        """Called on success."""
        pass  # Already handled in call method


class CircuitBreakerManager:
    """Manager for multiple adaptive circuit breakers."""

    def __init__(self):
        self._breakers: Dict[str, AdaptiveCircuitBreaker] = {}

    def get_breaker(self, operation: str) -> AdaptiveCircuitBreaker:
        """Get or create circuit breaker for operation."""
        if operation not in self._breakers:
            self._breakers[operation] = AdaptiveCircuitBreaker(
                name="adaptive_cb", operation=operation
            )
        return self._breakers[operation]

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers."""
        return {
            operation: breaker.get_metrics()
            for operation, breaker in self._breakers.items()
        }


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()

# Legacy circuit breaker for backward compatibility
redis_circuit_breaker = circuit_breaker_manager.get_breaker("tws_client")._circuit_breaker


# --- Resource Context Managers ---
class ResourceContext:
    """Base class for resource context management with rollback capabilities."""

    def __init__(self, correlation_id: str, resource_name: str):
        self.correlation_id = correlation_id
        self.resource_name = resource_name
        self._initialized = False
        self._resource = None

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup(exc_type, exc_val, exc_tb)

    async def initialize(self):
        """Initialize the resource. Override in subclasses."""
        pass

    async def cleanup(self, exc_type=None, exc_val=None, exc_tb=None):
        """Cleanup the resource. Override in subclasses."""
        pass

    def is_initialized(self) -> bool:
        """Check if resource is properly initialized."""
        return self._initialized


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

        # Create TaskGroup for supervision
        async with asyncio.TaskGroup() as task_group:
            # Create supervised tasks
            config_watcher_task = task_group.create_task(
                watch_config_changes(settings.AGENT_CONFIG_PATH),
                name="config_watcher",
            )
            supervised_tasks["config_watcher"] = config_watcher_task

            # Get file ingestor from DI container
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
        # Handle task supervision errors
        # Check if it's an ExceptionGroup (Python 3.11+) or regular exception
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
        # TaskGroup automatically cancels and waits for all tasks
        # Additional logging for cleanup completion
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
    Handles startup and shutdown procedures with proper error handling and correlation IDs.
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
        # Phase 0: Setup DI (synchronous)
        try:
            inject_container(app)
            log_with_correlation(
                logging.INFO,
                "Dependency injection container initialized",
                correlation_id=correlation_id,
                component="di",
                operation="setup",
            )
        except Exception as e:
            log_with_correlation(
                logging.CRITICAL,
                "Failed to setup dependency injection",
                correlation_id=correlation_id,
                component="di",
                operation="setup",
                error=e,
            )
            raise SystemExit(f"DI setup failed: {e}") from e

        # Phase 1: Validate configuration
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
        except Exception as e:
            log_with_correlation(
                logging.CRITICAL,
                "Unexpected error during configuration validation",
                correlation_id=correlation_id,
                component="config",
                operation="validation",
                error=e,
            )
            raise SystemExit(f"Configuration validation failed: {e}") from e

        # Phase 2: Initialize core systems (fail-fast)
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
            # Re-raise SystemExit from core systems
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

        # Phase 3-5: Initialize infrastructure components using context managers
        # These will be automatically cleaned up even if errors occur later
        async with managed_background_tasks(
            correlation_id
        ) as background_tasks, managed_cache_hierarchy(
            correlation_id
        ) as cache, managed_tws_monitor(
            correlation_id
        ) as monitor, managed_scheduler(
            correlation_id
        ) as scheduler:
            # Store scheduler reference for health checks
            app.state.scheduler = scheduler

            log_with_correlation(
                logging.INFO,
                "All systems initialized successfully",
                correlation_id=correlation_id,
                component="lifespan",
                operation="startup_complete",
            )

            yield

    except KeyboardInterrupt as e:
        log_with_correlation(
            logging.INFO,
            "Application startup interrupted by user",
            correlation_id=correlation_id,
            component="lifespan",
            operation="interrupt",
            error=e,
        )
        raise SystemExit("Startup interrupted by user") from e
    except SystemExit:
        # Re-raise SystemExit (already logged upstream)
        raise
    except ImportError as e:
        log_with_correlation(
            logging.CRITICAL,
            "Missing required dependencies",
            correlation_id=correlation_id,
            component="dependencies",
            operation="import",
            error=e,
        )
        raise SystemExit(f"Dependency error: {e}") from e
    except (OSError, IOError) as e:
        log_with_correlation(
            logging.CRITICAL,
            "File system error during startup",
            correlation_id=correlation_id,
            component="filesystem",
            operation="access",
            error=e,
        )
        raise SystemExit(f"File system error: {e}") from e
    except (ConnectionError, TimeoutError) as e:
        log_with_correlation(
            logging.CRITICAL,
            "Network connectivity error during startup",
            correlation_id=correlation_id,
            component="network",
            operation="connect",
            error=e,
        )
        raise SystemExit(f"Network error: {e}") from e
    except Exception as e:
        log_with_correlation(
            logging.CRITICAL,
            "Unexpected critical error during startup",
            correlation_id=correlation_id,
            component="lifespan",
            operation="startup",
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


def validate_tws_host(host: str) -> None:
    """Validate TWS_HOST format (IP:port) using InputSanitizer."""
    try:
        sanitized_host, sanitized_port = InputSanitizer.sanitize_host_port(host)
        log_with_correlation(
            logging.DEBUG,
            f"TWS host validation successful: {sanitized_host}:{sanitized_port}",
            correlation_id=AppContext.get_correlation_id(),
            component="validation",
            operation="tws_host",
            host=sanitized_host,
            port=sanitized_port,
        )
    except ValueError as e:
        raise ConfigError(f"Invalid TWS_HOST format: {host}. {e}") from e


def validate_paths() -> None:
    """Validate that required paths exist using InputSanitizer."""
    path_configs = [
        ("AGENT_CONFIG_PATH", settings.AGENT_CONFIG_PATH),
        ("RAG_DIR", settings.RAG_DIR),
    ]

    correlation_id = AppContext.get_correlation_id()

    for config_name, path_value in path_configs:
        try:
            validated_path = InputSanitizer.validate_path_exists(
                path_value, must_exist=True
            )
            log_with_correlation(
                logging.DEBUG,
                f"Path validation successful: {config_name}={validated_path}",
                correlation_id=correlation_id,
                component="validation",
                operation="path_exists",
                config_name=config_name,
                path=str(validated_path),
            )
        except (ValueError, FileNotFoundError) as e:
            raise ConfigError(f"Path validation failed: {config_name}={path_value}. {e}") from e


async def validate_runtime_config() -> Dict[str, Any]:
    """
    Runtime configuration validation for long-running services.
    Re-validates configuration that may change during runtime.

    Returns:
        Dict with validation results and any issues found.
    """
    correlation_id = AppContext.get_correlation_id()
    validation_results = {
        "timestamp": time_func(),
        "correlation_id": correlation_id,
        "overall_status": "valid",
        "checks": {},
        "issues": [],
    }

    log_with_correlation(
        logging.DEBUG,
        "Starting runtime configuration validation",
        correlation_id=correlation_id,
        component="config_validation",
        operation="start",
    )

    try:
        # 1. Validate environment settings
        try:
            app_env = getattr(settings, "APP_ENV", "production")
            if app_env not in ["development", "production", "staging"]:
                validation_results["issues"].append(
                    {
                        "type": "invalid_environment",
                        "severity": "error",
                        "message": f"Invalid APP_ENV: {app_env}",
                        "current_value": app_env,
                        "expected_values": ["development", "production", "staging"],
                    }
                )
                validation_results["overall_status"] = "invalid"
            else:
                validation_results["checks"]["environment"] = {
                    "status": "valid",
                    "value": app_env,
                }
        except Exception as e:
            validation_results["issues"].append(
                {
                    "type": "environment_check_error",
                    "severity": "error",
                    "message": f"Error checking environment: {e}",
                }
            )
            validation_results["overall_status"] = "invalid"

        # 2. Validate TWS connection
        try:
            tws_host = getattr(settings, "TWS_HOST", None)
            tws_port = getattr(settings, "TWS_PORT", None)

            if tws_host and tws_port:
                # Re-validate host:port format
                try:
                    sanitized_host, sanitized_port = InputSanitizer.sanitize_host_port(
                        f"{tws_host}:{tws_port}"
                    )
                    validation_results["checks"]["tws_connection"] = {
                        "status": "valid",
                        "host": sanitized_host,
                        "port": sanitized_port,
                    }
                except ValueError as e:
                    validation_results["issues"].append(
                        {
                            "type": "invalid_tws_connection",
                            "severity": "error",
                            "message": f"Invalid TWS connection format: {tws_host}:{tws_port} - {e}",
                        }
                    )
                    validation_results["overall_status"] = "invalid"
            else:
                validation_results["issues"].append(
                    {
                        "type": "missing_tws_connection",
                        "severity": "error",
                        "message": "TWS_HOST or TWS_PORT not configured",
                    }
                )
                validation_results["overall_status"] = "invalid"
        except Exception as e:
            validation_results["issues"].append(
                {
                    "type": "tws_connection_check_error",
                    "severity": "error",
                    "message": f"Error validating TWS connection: {e}",
                }
            )
            validation_results["overall_status"] = "invalid"

        # 3. Validate critical paths still exist
        try:
            validate_paths()  # Reuse existing validation
            validation_results["checks"]["critical_paths"] = {
                "status": "valid",
                "paths": {
                    "agent_config": settings.AGENT_CONFIG_PATH,
                    "rag_dir": settings.RAG_DIR,
                },
            }
        except ConfigError as e:
            validation_results["issues"].append(
                {
                    "type": "critical_paths_invalid",
                    "severity": "error",
                    "message": f"Critical paths validation failed: {e}",
                }
            )
            validation_results["overall_status"] = "invalid"
        except Exception as e:
            validation_results["issues"].append(
                {
                    "type": "critical_paths_check_error",
                    "severity": "error",
                    "message": f"Error validating critical paths: {e}",
                }
            )
            validation_results["overall_status"] = "invalid"

        # 4. Validate model configuration
        try:
            agent_model = getattr(settings, "AGENT_MODEL_NAME", None)
            llm_endpoint = getattr(settings, "LLM_ENDPOINT", None)

            if not agent_model or not agent_model.strip():
                validation_results["issues"].append(
                    {
                        "type": "missing_agent_model",
                        "severity": "error",
                        "message": "AGENT_MODEL_NAME not configured or empty",
                    }
                )
                validation_results["overall_status"] = "invalid"
            else:
                validation_results["checks"]["agent_model"] = {
                    "status": "valid",
                    "model_name": agent_model,
                }

            if not llm_endpoint or not llm_endpoint.strip():
                validation_results["issues"].append(
                    {
                        "type": "missing_llm_endpoint",
                        "severity": "error",
                        "message": "LLM_ENDPOINT not configured or empty",
                    }
                )
                validation_results["overall_status"] = "invalid"
            else:
                validation_results["checks"]["llm_endpoint"] = {
                    "status": "valid",
                    "endpoint": llm_endpoint,
                }
        except Exception as e:
            validation_results["issues"].append(
                {
                    "type": "model_config_check_error",
                    "severity": "error",
                    "message": f"Error validating model configuration: {e}",
                }
            )
            validation_results["overall_status"] = "invalid"

        # 5. Validate DI container health
        try:
            container = get_container()
            di_health = await container.get_health_status()

            if di_health.get("overall_status") == "healthy":
                validation_results["checks"]["di_container"] = {
                    "status": "valid",
                    "services_count": len(di_health.get("services", {})),
                }
            else:
                validation_results["issues"].append(
                    {
                        "type": "di_container_unhealthy",
                        "severity": "warning",
                        "message": f"DI container reports unhealthy status: {di_health.get('overall_status')}",
                        "di_status": di_health,
                    }
                )
                # Don't set overall_status to invalid for DI issues (might be temporary)
        except Exception as e:
            validation_results["issues"].append(
                {
                    "type": "di_container_check_error",
                    "severity": "warning",
                    "message": f"Error checking DI container health: {e}",
                }
            )

    except Exception as e:
        validation_results["issues"].append(
            {
                "type": "validation_runtime_error",
                "severity": "error",
                "message": f"Runtime validation failed with unexpected error: {e}",
            }
        )
        validation_results["overall_status"] = "error"

    # Log summary
    issues_count = len(validation_results["issues"])
    log_with_correlation(
        logging.INFO
        if validation_results["overall_status"] == "valid"
        else logging.WARNING,
        f"Runtime configuration validation completed: {validation_results['overall_status']} with {issues_count} issues",
        correlation_id=correlation_id,
        component="config_validation",
        operation="complete",
        overall_status=validation_results["overall_status"],
        issues_count=issues_count,
    )

    return validation_results


def validate_settings() -> None:
    """Validate critical settings before startup."""
    logger.info("Validating settings...")

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
        logger.critical(f"{error_msg}")
        raise ConfigError(error_msg)

    # Enhanced validations
    try:
        # TWS_HOST format validation
        validate_tws_host(settings.TWS_HOST)

        # Path existence validation
        validate_paths()

        # Port validation
        if (
            not isinstance(settings.TWS_PORT, int)
            or settings.TWS_PORT <= 0
            or settings.TWS_PORT > 65535
        ):
            error_msg = (
                f"Invalid TWS_PORT: {settings.TWS_PORT} (must be integer 1-65535)"
            )
            logger.critical(f"{error_msg}")
            raise ConfigError(error_msg)

        # Environment validation
        if settings.APP_ENV not in ["development", "production", "staging"]:
            error_msg = f"Invalid APP_ENV: {settings.APP_ENV}"
            logger.critical(f"{error_msg}")
            raise ConfigError(error_msg)

    except ConfigError:
        raise  # Re-raise ConfigError as-is
    except Exception as e:
        logger.critical(f"Unexpected error during settings validation: {e}")
        raise ConfigError(f"Settings validation failed: {e}") from e

    logger.info("Settings validation completed successfully")


async def initialize_core_systems() -> None:
    """Initialize core systems with fail-fast behavior and granular error handling."""
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.INFO,
        "Initializing core systems",
        correlation_id=correlation_id,
        component="core_init",
        operation="begin",
    )

    # Agent Manager (required)
    try:
        await agent_manager.load_agents_from_config()
        log_with_correlation(
            logging.INFO,
            "Agent Manager initialized successfully",
            correlation_id=correlation_id,
            component="core_init",
            operation="agent_manager_init",
        )
    except (ConfigError, FileNotFoundError) as e:
        log_with_correlation(
            logging.CRITICAL,
            "Configuration error initializing Agent Manager",
            correlation_id=correlation_id,
            component="core_init",
            operation="agent_manager_config_error",
            error=e,
        )
        raise SystemExit("Agent Manager configuration failed") from e
    except (ConnectionError, TimeoutError) as e:
        log_with_correlation(
            logging.CRITICAL,
            "Network error initializing Agent Manager",
            correlation_id=correlation_id,
            component="core_init",
            operation="agent_manager_network_error",
            error=e,
        )
        raise SystemExit("Agent Manager network connection failed") from e
    except Exception as e:
        log_with_correlation(
            logging.CRITICAL,
            "Unexpected error initializing Agent Manager",
            correlation_id=correlation_id,
            component="core_init",
            operation="agent_manager_unexpected_error",
            error=e,
        )
        raise SystemExit("Agent Manager initialization failed") from e

    # TWS Client (required for agents)
    try:
        # Use adaptive circuit breaker for TWS client initialization
        tws_breaker = circuit_breaker_manager.get_breaker("tws_client")
        await tws_breaker.call(agent_manager._get_tws_client)
        log_with_correlation(
            logging.INFO,
            "TWS Client initialized successfully",
            correlation_id=correlation_id,
            component="core_init",
            operation="tws_client_init",
            circuit_metrics=tws_breaker.get_metrics(),
        )
    except pybreaker.CircuitBreakerError as e:
        log_with_correlation(
            logging.CRITICAL,
            "Circuit breaker open for TWS Client initialization",
            correlation_id=correlation_id,
            component="core_init",
            operation="tws_client_circuit_breaker",
            error=e,
        )
        raise SystemExit("TWS Client circuit breaker open") from e
    except (ConnectionError, TimeoutError) as e:
        log_with_correlation(
            logging.CRITICAL,
            "Network error initializing TWS Client",
            correlation_id=correlation_id,
            component="core_init",
            operation="tws_client_network_error",
            error=e,
        )
        raise SystemExit("TWS Client network connection failed") from e
    except Exception as e:
        log_with_correlation(
            logging.CRITICAL,
            "Unexpected error initializing TWS Client",
            correlation_id=correlation_id,
            component="core_init",
            operation="tws_client_unexpected_error",
            error=e,
        )
        raise SystemExit("TWS Client initialization failed") from e

        # Knowledge Graph (required)
    knowledge_graph = None
    try:
        from resync.core.knowledge_graph import AsyncKnowledgeGraph

        log_with_correlation(
            logging.INFO,
            "Initializing Knowledge Graph for continuous learning",
            correlation_id=correlation_id,
            component="core_init",
            operation="kg_init_begin",
        )
        container = get_container()
        knowledge_graph = await container.get(AsyncKnowledgeGraph)
        # Register concrete implementation for interface
        container.register(
            IKnowledgeGraph, AsyncKnowledgeGraph, ServiceScope.SINGLETON
        )
        log_with_correlation(
            logging.INFO,
            "Knowledge Graph initialized and registered successfully",
            correlation_id=correlation_id,
            component="core_init",
            operation="kg_init_complete",
        )

    except ImportError as e:
        log_with_correlation(
            logging.CRITICAL,
            "Failed to import Knowledge Graph module",
            correlation_id=correlation_id,
            component="core_init",
            operation="kg_import_error",
            error=e,
        )
        raise SystemExit("Knowledge Graph import failed") from e
    except (ConnectionError, TimeoutError) as e:
        log_with_correlation(
            logging.CRITICAL,
            "Network/database error initializing Knowledge Graph",
            correlation_id=correlation_id,
            component="core_init",
            operation="kg_connection_error",
            error=e,
        )
        raise SystemExit("Knowledge Graph connection failed") from e
    except Exception as e:
        log_with_correlation(
            logging.CRITICAL,
            "Unexpected error initializing Knowledge Graph",
            correlation_id=correlation_id,
            component="core_init",
            operation="kg_unexpected_error",
            error=e,
        )
        raise SystemExit("Knowledge Graph initialization failed") from e

    # File Ingestor (depends on KG)
    try:
        if knowledge_graph is None:
            raise RuntimeError("Knowledge Graph not available for File Ingestor")

        file_ingestor = await container.get(FileIngestor)
        # Register concrete implementation for interface
        container.register(IFileIngestor, FileIngestor, ServiceScope.SINGLETON)
        log_with_correlation(
            logging.INFO,
            "File Ingestor initialized and registered successfully",
            correlation_id=correlation_id,
            component="core_init",
            operation="file_ingestor_init",
        )

        # Load existing RAG documents into knowledge graph
        log_with_correlation(
            logging.INFO,
            "Loading existing RAG documents",
            correlation_id=correlation_id,
            component="core_init",
            operation="rag_loading_begin",
        )
        loaded_docs = await load_existing_rag_documents(file_ingestor)
        log_with_correlation(
            logging.INFO,
            f"Loaded {loaded_docs} existing RAG documents into knowledge graph",
            correlation_id=correlation_id,
            component="core_init",
            operation="rag_loading_complete",
            documents_loaded=loaded_docs,
        )

    except (FileNotFoundError, PermissionError) as e:
        log_with_correlation(
            logging.CRITICAL,
            "File system error initializing File Ingestor",
            correlation_id=correlation_id,
            component="core_init",
            operation="file_ingestor_fs_error",
            error=e,
        )
        raise SystemExit("File Ingestor file system error") from e
    except (ConnectionError, TimeoutError) as e:
        log_with_correlation(
            logging.CRITICAL,
            "Network/database error initializing File Ingestor",
            correlation_id=correlation_id,
            component="core_init",
            operation="file_ingestor_connection_error",
            error=e,
        )
        raise SystemExit("File Ingestor connection failed") from e
    except RuntimeError as e:
        log_with_correlation(
            logging.CRITICAL,
            "Dependency error initializing File Ingestor",
            correlation_id=correlation_id,
            component="core_init",
            operation="file_ingestor_dependency_error",
            error=e,
        )
        raise SystemExit("File Ingestor dependency error") from e
    except Exception as e:
        log_with_correlation(
            logging.CRITICAL,
            "Unexpected error initializing File Ingestor",
            correlation_id=correlation_id,
            component="core_init",
            operation="file_ingestor_unexpected_error",
            error=e,
        )
        raise SystemExit("File Ingestor initialization failed") from e


async def start_background_services() -> Dict[str, asyncio.Task]:
    """Start background services and return task references."""
    logger.info(" Starting background services...")

    tasks = {}

    # Configuration watcher
    try:
        config_watcher_task: asyncio.Task[None] = asyncio.create_task(
            watch_config_changes(settings.AGENT_CONFIG_PATH)
        )
        tasks["config_watcher"] = config_watcher_task
        logger.info(" Configuration watcher started")
    except Exception as e:
        logger.error(f" Failed to start configuration watcher: {e}")
        raise

    # RAG directory watcher
    try:
        # Get the file_ingestor instance from the DI container
        container = get_container()
        file_ingestor = await container.get(IFileIngestor)
        rag_watcher_task: asyncio.Task[None] = asyncio.create_task(
            watch_rag_directory(file_ingestor)
        )
        tasks["rag_watcher"] = rag_watcher_task
        logger.info(" RAG directory watcher started")
    except Exception as e:
        logger.error(f" Failed to start RAG watcher: {e}")
        # Don't fail completely, but log the error
        logger.warning("Continuing without RAG watcher")

    return tasks


async def initialize_schedulers() -> AsyncIOScheduler:
    """Initialize schedulers with environment-aware configuration and granular error handling."""
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.INFO,
        "Initializing schedulers",
        correlation_id=correlation_id,
        component="scheduler_init",
        operation="begin",
    )

    scheduler = AsyncIOScheduler()

    try:
        # Configure IA Auditor frequency based on environment
        job_config = get_auditor_job_config()
        log_with_correlation(
            logging.INFO,
            f"IA Auditor job configuration: {job_config}",
            correlation_id=correlation_id,
            component="scheduler_init",
            operation="config_loaded",
            job_type=job_config["type"],
            startup_enabled=job_config.get("startup_enabled", False),
        )

        # Add recurring job
        try:
            scheduler.add_job(
                analyze_and_flag_memories, job_config["type"], **job_config["config"]
            )
            log_with_correlation(
                logging.INFO,
                f"IA Auditor recurring job added with {job_config['type']} schedule",
                correlation_id=correlation_id,
                component="scheduler_init",
                operation="recurring_job_added",
                schedule_type=job_config["type"],
                schedule_config=job_config["config"],
            )
        except ValueError as e:
            log_with_correlation(
                logging.CRITICAL,
                "Invalid job configuration for IA Auditor",
                correlation_id=correlation_id,
                component="scheduler_init",
                operation="job_config_error",
                error=e,
            )
            raise SystemExit("Invalid scheduler job configuration") from e

        # Add periodic configuration validation job
        try:
            config_validation_interval = InputSanitizer.sanitize_environment_value(
                "CONFIG_VALIDATION_INTERVAL_HOURS",
                os.getenv("CONFIG_VALIDATION_INTERVAL_HOURS", "6"),
                int,
            )
            config_validation_interval = max(
                1, min(config_validation_interval, 24)
            )  # 1-24 hours

            scheduler.add_job(
                validate_runtime_config,
                "interval",
                hours=config_validation_interval,
                id="config_validation",
                name="Runtime Configuration Validation",
            )
            log_with_correlation(
                logging.INFO,
                f"Configuration validation job added (every {config_validation_interval} hours)",
                correlation_id=correlation_id,
                component="scheduler_init",
                operation="config_validation_job_added",
                interval_hours=config_validation_interval,
            )
        except Exception as e:
            log_with_correlation(
                logging.WARNING,
                "Failed to add configuration validation job",
                correlation_id=correlation_id,
                component="scheduler_init",
                operation="config_validation_job_error",
                error=e,
            )
            # Don't fail startup for this

        # Run once on startup for immediate feedback
        if job_config.get("startup_enabled", False):
            try:
                scheduler.add_job(analyze_and_flag_memories)
                log_with_correlation(
                    logging.INFO,
                    "IA Auditor startup job added",
                    correlation_id=correlation_id,
                    component="scheduler_init",
                    operation="startup_job_added",
                )
            except Exception as e:
                log_with_correlation(
                    logging.WARNING,
                    "Failed to add startup job for IA Auditor",
                    correlation_id=correlation_id,
                    component="scheduler_init",
                    operation="startup_job_error",
                    error=e,
                )
                # Don't fail startup for this, just log warning

        # Start the scheduler
        try:
            scheduler.start()
            log_with_correlation(
                logging.INFO,
                "IA Auditor scheduler started successfully",
                correlation_id=correlation_id,
                component="scheduler_init",
                operation="scheduler_started",
                job_type=job_config["type"],
                schedule_config=job_config["config"],
                startup_enabled=job_config.get("startup_enabled", False),
            )
        except RuntimeError as e:
            log_with_correlation(
                logging.CRITICAL,
                "Failed to start scheduler - already running or invalid state",
                correlation_id=correlation_id,
                component="scheduler_init",
                operation="scheduler_start_error",
                error=e,
            )
            raise SystemExit("Scheduler start failed") from e

    except SystemExit:
        # Re-raise SystemExit from nested functions
        raise
    except Exception as e:
        log_with_correlation(
            logging.CRITICAL,
            "Unexpected error initializing scheduler",
            correlation_id=correlation_id,
            component="scheduler_init",
            operation="unexpected_error",
            error=e,
        )
        raise SystemExit("Scheduler initialization failed") from e

    return scheduler


def get_auditor_job_config() -> Dict[str, Any]:
    """Get auditor job configuration based on environment and settings with validation."""
    correlation_id = AppContext.get_correlation_id()
    try:
        app_env = getattr(settings, "APP_ENV", "production")
        log_with_correlation(
            logging.DEBUG,
            f"Getting IA Auditor config for environment: {app_env}",
            correlation_id=correlation_id,
            component="scheduler_config",
            operation="env_check",
            app_env=app_env,
        )

        if app_env == "production":
            frequency_hours = getattr(settings, "IA_AUDITOR_FREQUENCY_HOURS", 6)
            startup_enabled = getattr(
                settings, "IA_AUDITOR_STARTUP_ENABLED", False
            )

            if not isinstance(frequency_hours, (int, float)) or frequency_hours <= 0:
                error_msg = (
                    f"IA_AUDITOR_FREQUENCY_HOURS must be a positive number, got: {frequency_hours} "
                    f"(type: {type(frequency_hours).__name__})"
                )
                log_with_correlation(
                    logging.ERROR,
                    error_msg,
                    correlation_id=correlation_id,
                    component="scheduler_config",
                    operation="validation_error",
                    invalid_value=frequency_hours,
                    expected_type="positive number",
                )
                raise ValueError(error_msg)

            if frequency_hours > 24:
                log_with_correlation(
                    logging.WARNING,
                    f"IA_AUDITOR_FREQUENCY_HOURS is very high: {frequency_hours} hours",
                    correlation_id=correlation_id,
                    component="scheduler_config",
                    operation="range_warning",
                    frequency_hours=frequency_hours,
                )

            config = {
                "type": "cron",
                "config": {"hour": f"*/{int(frequency_hours)}"},
                "startup_enabled": bool(startup_enabled),
            }
            log_with_correlation(
                logging.INFO,
                f"Production IA Auditor config: every {frequency_hours} hours, startup={startup_enabled}",
                correlation_id=correlation_id,
                component="scheduler_config",
                operation="config_complete",
                config=config,
            )
            return config

        elif app_env == "development":
            config = {
                "type": "interval",
                "config": {"minutes": 30},
                "startup_enabled": True,
            }
            log_with_correlation(
                logging.INFO,
                "Development IA Auditor config: every 30 minutes with startup",
                correlation_id=correlation_id,
                component="scheduler_config",
                operation="config_complete",
                config=config,
            )
            return config
        else:
            log_with_correlation(
                logging.WARNING,
                f"Unknown APP_ENV '{app_env}', using default configuration",
                correlation_id=correlation_id,
                component="scheduler_config",
                operation="unknown_env",
                app_env=app_env,
            )
            config = {
                "type": "cron",
                "config": {"hour": "*/6"},
                "startup_enabled": True,
            }
            log_with_correlation(
                logging.INFO,
                "Default IA Auditor config: every 6 hours with startup",
                correlation_id=correlation_id,
                component="scheduler_config",
                operation="config_complete",
                config=config,
            )
            return config

    except AttributeError as e:
        log_with_correlation(
            logging.ERROR,
            "Missing required settings attribute",
            correlation_id=correlation_id,
            component="scheduler_config",
            operation="attribute_error",
            error=e,
        )
        raise ConfigError(f"Settings configuration error: {e}") from e
    except Exception as e:
        log_with_correlation(
            logging.ERROR,
            "Unexpected error getting IA Auditor configuration",
            correlation_id=correlation_id,
            component="scheduler_config",
            operation="unexpected_error",
            error=e,
        )
        raise ConfigError(f"IA Auditor configuration failed: {e}") from e


async def shutdown_application(
    app: FastAPI, background_tasks: Dict[str, asyncio.Task], correlation_id: str
) -> None:
    """
    Shutdown remaining application components not handled by context managers.
    Note: Most resources are now managed by context managers in lifespan().
    """
    log_with_correlation(
        logging.INFO,
        "Shutting down remaining application components",
        correlation_id=correlation_id,
        component="shutdown",
        operation="begin",
    )

    shutdown_errors = []

    # Clean up TWS client connection (not managed by context managers)
    try:
        if hasattr(agent_manager, "tws_client") and agent_manager.tws_client:
            # Check if client has active connections before closing
            if (
                hasattr(agent_manager.tws_client, "is_connected")
                and agent_manager.tws_client.is_connected
            ):
                await agent_manager.tws_client.close()
                log_with_correlation(
                    logging.INFO,
                    "TWS client closed successfully",
                    correlation_id=correlation_id,
                    component="shutdown",
                    operation="tws_client_close",
                )
            else:
                log_with_correlation(
                    logging.INFO,
                    "TWS client was not connected, skipping close",
                    correlation_id=correlation_id,
                    component="shutdown",
                    operation="tws_client_skip",
                )
        else:
            log_with_correlation(
                logging.INFO,
                "TWS client not available, skipping close",
                correlation_id=correlation_id,
                component="shutdown",
                operation="tws_client_not_found",
            )
    except Exception as e:
        log_with_correlation(
            logging.ERROR,
            "Error closing TWS client",
            correlation_id=correlation_id,
            component="shutdown",
            operation="tws_client_error",
            error=e,
        )
        shutdown_errors.append(("tws_client", str(e)))

    # Close Knowledge Graph connection (not managed by context managers)
    try:
        container = get_container()
        try:
            kg_instance = await container.get(IKnowledgeGraph)
            if hasattr(kg_instance, "close") and kg_instance is not None:
                # Check if connection is active before closing
                if hasattr(kg_instance, "_driver") and kg_instance._driver:
                    await kg_instance.close()
                    log_with_correlation(
                        logging.INFO,
                        "Knowledge Graph connection closed successfully",
                        correlation_id=correlation_id,
                        component="shutdown",
                        operation="kg_close",
                    )
                else:
                    log_with_correlation(
                        logging.INFO,
                        "Knowledge Graph was not connected, skipping close",
                        correlation_id=correlation_id,
                        component="shutdown",
                        operation="kg_skip",
                    )
            else:
                log_with_correlation(
                    logging.INFO,
                    "Knowledge Graph instance not available, skipping close",
                    correlation_id=correlation_id,
                    component="shutdown",
                    operation="kg_not_available",
                )
        except KeyError as e:
            log_with_correlation(
                logging.WARNING,
                "Knowledge Graph not registered in container, skipping close",
                correlation_id=correlation_id,
                component="shutdown",
                operation="kg_not_registered",
                error=e,
            )
    except Exception as e:
        log_with_correlation(
            logging.ERROR,
            "Error closing Knowledge Graph connection",
            correlation_id=correlation_id,
            component="shutdown",
            operation="kg_error",
            error=e,
        )
        shutdown_errors.append(("knowledge_graph", str(e)))

    # Log shutdown summary
    if shutdown_errors:
        log_with_correlation(
            logging.WARNING,
            f"Shutdown completed with {len(shutdown_errors)} errors",
            correlation_id=correlation_id,
            component="shutdown",
            operation="complete_with_errors",
            error_count=len(shutdown_errors),
            errors=shutdown_errors,
        )
    else:
        log_with_correlation(
            logging.INFO,
            "Shutdown completed successfully",
            correlation_id=correlation_id,
            component="shutdown",
            operation="complete_success",
        )


@retry(
    wait=wait_random_exponential(multiplier=1, max=60),
    stop=stop_after_attempt(5),
    reraise=True,
)
async def watch_config_changes(config_path: Path) -> None:
    """
    Watches the agent configuration file for changes and triggers a reload.
    Includes rate limiting, backoff, and platform-specific error handling.
    """
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.INFO,
        "Starting configuration watcher with rate limiting",
        correlation_id=correlation_id,
        component="watcher",
        operation="start",
        config_path=str(config_path),
        platform=os.name,
    )

    # Rate limiting configuration
    min_interval = InputSanitizer.sanitize_environment_value(
        "CONFIG_WATCHER_MIN_INTERVAL", os.getenv("CONFIG_WATCHER_MIN_INTERVAL", "1.0"), float
    )
    max_burst_events = InputSanitizer.sanitize_environment_value(
        "CONFIG_WATCHER_MAX_BURST", os.getenv("CONFIG_WATCHER_MAX_BURST", "5"), int
    )

    # Rate limiting state
    last_change_time = 0.0
    recent_changes = []

    try:
        async for changes in awatch(config_path):
            current_time = time_func()

            # Rate limiting: enforce minimum interval between changes
            time_since_last = current_time - last_change_time
            if time_since_last < min_interval:
                log_with_correlation(
                    logging.DEBUG,
                    f"Rate limiting: change too soon ({time_since_last:.2f}s < {min_interval}s)",
                    correlation_id=correlation_id,
                    component="watcher",
                    operation="rate_limited",
                    time_since_last=time_since_last,
                    min_interval=min_interval,
                )
                continue

            # Burst protection: limit rapid successive changes
            recent_changes = [
                t for t in recent_changes if current_time - t < 60.0
            ]  # Clean old entries
            if len(recent_changes) >= max_burst_events:
                log_with_correlation(
                    logging.WARNING,
                    f"Burst protection: too many changes ({len(recent_changes)} >= {max_burst_events})",
                    correlation_id=correlation_id,
                    component="watcher",
                    operation="burst_protected",
                    recent_changes_count=len(recent_changes),
                    max_burst=max_burst_events,
                )
                await asyncio.sleep(min_interval)  # Backoff
                continue

            try:
                # Handle the config change
                await handle_config_change()
                last_change_time = current_time
                recent_changes.append(current_time)

                log_with_correlation(
                    logging.INFO,
                    "Configuration change handled successfully",
                    correlation_id=correlation_id,
                    component="watcher",
                    operation="change_handled",
                    changes_count=len(changes),
                    time_since_last=time_since_last,
                )

            except Exception as e:
                log_with_correlation(
                    logging.ERROR,
                    "Error handling config change",
                    correlation_id=correlation_id,
                    component="watcher",
                    operation="change_error",
                    error=e,
                )
                # Continue watching despite individual change errors
                await asyncio.sleep(min_interval * 2)  # Extra backoff on error

    except FileNotFoundError as e:
        log_with_correlation(
            logging.ERROR,
            "Configuration file not found",
            correlation_id=correlation_id,
            component="watcher",
            operation="file_not_found",
            error=e,
        )
        raise ConfigError(f"Configuration file not found: {config_path}") from e
    except PermissionError as e:
        log_with_correlation(
            logging.ERROR,
            "Permission denied accessing configuration file",
            correlation_id=correlation_id,
            component="watcher",
            operation="permission_denied",
            error=e,
        )
        raise ConfigError(
            f"Permission denied accessing configuration file: {config_path}"
        ) from e
    except OSError as e:
        # Platform-specific OS error handling
        error_type = "windows_os_error" if os.name == "nt" else "unix_os_error"
        log_with_correlation(
            logging.ERROR,
            f"OS error watching config file: {error_type}",
            correlation_id=correlation_id,
            component="watcher",
            operation=error_type,
            error=e,
        )
        raise FileProcessingError(
            f"OS error watching configuration file: {config_path}"
        ) from e
    except asyncio.CancelledError:
        log_with_correlation(
            logging.INFO,
            "Configuration watcher cancelled",
            correlation_id=correlation_id,
            component="watcher",
            operation="cancelled",
        )
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
async def get_review_page(request: Request) -> HTMLResponse:
    """Serves the human review dashboard page."""
    return templates.TemplateResponse("revisao.html", {"request": request})


@app.get("/", include_in_schema=False)
async def root():
    """
    Redirects the root URL to the main API docs page.
    """
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs", status_code=302)


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint for monitoring system status.
    Includes active component pings and state validation.
    """
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.DEBUG,
        "Global health check requested",
        correlation_id=correlation_id,
        component="health",
        operation="global_check",
    )

    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time_func(),
        "correlation_id": correlation_id,
        "components": {},
    }

    try:
        # Aggregate health from all subsystems
        core_health = await health_check_core()
        infra_health = await health_check_infrastructure()
        services_health = await health_check_services()

        health_status["components"].update(core_health["components"])
        health_status["components"].update(infra_health["components"])
        health_status["components"].update(services_health["components"])

        # Determine overall status - any subsystem failure makes overall status degraded
        subsystem_statuses = [
            core_health["status"],
            infra_health["status"],
            services_health["status"],
        ]
        if "error" in subsystem_statuses:
            health_status["status"] = "error"
        elif "degraded" in subsystem_statuses:
            health_status["status"] = "degraded"

        health_status["subsystems"] = {
            "core": core_health["status"],
            "infrastructure": infra_health["status"],
            "services": services_health["status"],
        }

        log_with_correlation(
            logging.DEBUG,
            f"Global health check completed: {health_status['status']}",
            correlation_id=correlation_id,
            component="health",
            operation="global_check_complete",
            overall_status=health_status["status"],
            subsystem_statuses=health_status["subsystems"],
        )

    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        log_with_correlation(
            logging.ERROR,
            "Global health check failed",
            correlation_id=correlation_id,
            component="health",
            operation="global_check_error",
            error=e,
        )

    return health_status


@app.get("/health/di")
async def health_check_di() -> Dict[str, Any]:
    """
    Health check for Dependency Injection container and registered services.
    """
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.DEBUG,
        "DI health check requested",
        correlation_id=correlation_id,
        component="health",
        operation="di_check",
    )

    try:
        container = get_container()
        health_status = await container.get_health_status()
        health_status["correlation_id"] = correlation_id

        log_with_correlation(
            logging.DEBUG,
            f"DI health check completed: {health_status['overall_status']}",
            correlation_id=correlation_id,
            component="health",
            operation="di_check_complete",
            overall_status=health_status["overall_status"],
        )

        return health_status

    except Exception as e:
        health_status = {
            "status": "error",
            "correlation_id": correlation_id,
            "error": str(e),
            "timestamp": time_func(),
        }
        log_with_correlation(
            logging.ERROR,
            "DI health check failed",
            correlation_id=correlation_id,
            component="health",
            operation="di_check_error",
            error=e,
        )
        return health_status


@app.get("/config/validate")
async def validate_config_endpoint() -> Dict[str, Any]:
    """
    Runtime configuration validation endpoint.
    Useful for monitoring configuration health in long-running services.
    """
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.INFO,
        "Runtime configuration validation requested",
        correlation_id=correlation_id,
        component="config",
        operation="validate_request",
    )

    try:
        validation_result = await validate_runtime_config()
        validation_result["correlation_id"] = correlation_id

        log_with_correlation(
            logging.INFO,
            f"Configuration validation completed: {validation_result['overall_status']}",
            correlation_id=correlation_id,
            component="config",
            operation="validate_complete",
            overall_status=validation_result["overall_status"],
            issues_count=len(validation_result.get("issues", [])),
        )

        return validation_result

    except Exception as e:
        error_result = {
            "overall_status": "error",
            "correlation_id": correlation_id,
            "timestamp": time_func(),
            "error": str(e),
            "issues": [
                {
                    "type": "endpoint_error",
                    "severity": "error",
                    "message": f"Configuration validation endpoint failed: {e}",
                }
            ],
        }
        log_with_correlation(
            logging.ERROR,
            "Configuration validation endpoint failed",
            correlation_id=correlation_id,
            component="config",
            operation="validate_error",
            error=e,
        )
        return error_result


@app.get("/health/core")
async def health_check_core() -> Dict[str, Any]:
    """
    Health check for core application components.
    Critical components that must be operational for basic functionality.
    """
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.DEBUG,
        "Core health check requested",
        correlation_id=correlation_id,
        component="health",
        operation="core_check",
    )

    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time_func(),
        "correlation_id": correlation_id,
        "components": {},
    }

    try:
        # Check Agent Manager (critical)
        try:
            # Agent manager is initialized at startup, check if it's accessible
            if hasattr(agent_manager, "agents") and agent_manager.agents is not None:
                health_status["components"]["agent_manager"] = "initialized"
        except Exception as e:
            health_status["components"]["agent_manager"] = f"error: {str(e)}"
            health_status["status"] = "error"

        # Check Knowledge Graph (critical)
        try:
            container = get_container()
            kg_instance = await container.get(IKnowledgeGraph)
            if kg_instance is not None:
                health_status["components"]["knowledge_graph"] = "initialized"
            else:
                health_status["components"]["knowledge_graph"] = "not_initialized"
                health_status["status"] = "error"
        except KeyError:
            health_status["components"]["knowledge_graph"] = "not_registered"
            health_status["status"] = "error"
        except Exception as e:
            health_status["components"]["knowledge_graph"] = f"error: {str(e)}"
            health_status["status"] = "error"

        # Check File Ingestor (critical)
        try:
            container = get_container()
            file_ingestor = await container.get(IFileIngestor)
            if file_ingestor is not None:
                health_status["components"]["file_ingestor"] = "initialized"
            else:
                health_status["components"]["file_ingestor"] = "not_initialized"
                health_status["status"] = "error"
        except KeyError:
            health_status["components"]["file_ingestor"] = "not_registered"
            health_status["status"] = "error"
        except Exception as e:
            health_status["components"]["file_ingestor"] = f"error: {str(e)}"
            health_status["status"] = "error"

    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        log_with_correlation(
            logging.ERROR,
            "Core health check failed",
            correlation_id=correlation_id,
            component="health",
            operation="core_check_error",
            error=e,
        )

    return health_status


@app.get("/health/infrastructure")
async def health_check_infrastructure() -> Dict[str, Any]:
    """
    Health check for infrastructure components.
    Components that support the application but may have graceful degradation.
    """
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.DEBUG,
        "Infrastructure health check requested",
        correlation_id=correlation_id,
        component="health",
        operation="infra_check",
    )

    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time_func(),
        "correlation_id": correlation_id,
        "components": {},
    }

    try:
        # Check Cache Hierarchy (important but not critical)
        try:
            cache_hierarchy = get_cache_hierarchy()
            if hasattr(cache_hierarchy, "is_running") and cache_hierarchy.is_running:
                health_status["components"]["cache_hierarchy"] = "running"
            else:
                health_status["components"]["cache_hierarchy"] = "stopped"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["cache_hierarchy"] = f"error: {str(e)}"
            health_status["status"] = "degraded"

        # Check Scheduler (important but not critical)
        try:
            if hasattr(app.state, "scheduler") and app.state.scheduler:
                scheduler_running = getattr(app.state.scheduler, "running", False)
                health_status["components"]["scheduler"] = (
                    "running" if scheduler_running else "stopped"
                )
                if not scheduler_running:
                    health_status["status"] = "degraded"
            else:
                health_status["components"]["scheduler"] = "not_initialized"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["scheduler"] = f"error: {str(e)}"
            health_status["status"] = "degraded"

        # Check TWS Monitor (important but not critical)
        try:
            if hasattr(tws_monitor, "is_monitoring") and tws_monitor.is_monitoring:
                health_status["components"]["tws_monitor"] = "active"
            else:
                health_status["components"]["tws_monitor"] = "inactive"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["tws_monitor"] = f"error: {str(e)}"
            health_status["status"] = "degraded"

    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        log_with_correlation(
            logging.ERROR,
            "Infrastructure health check failed",
            correlation_id=correlation_id,
            component="health",
            operation="infra_check_error",
            error=e,
        )

    return health_status


@app.get("/health/services")
async def health_check_services() -> Dict[str, Any]:
    """
    Health check for external services.
    Services that may be temporarily unavailable without breaking core functionality.
    """
    correlation_id = AppContext.get_correlation_id()
    log_with_correlation(
        logging.DEBUG,
        "Services health check requested",
        correlation_id=correlation_id,
        component="health",
        operation="services_check",
    )

    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": time_func(),
        "correlation_id": correlation_id,
        "components": {},
    }

    try:
        # Check TWS Client (external service)
        if hasattr(agent_manager, "tws_client") and agent_manager.tws_client:
            try:
                # Try to ping the TWS server for active verification
                if hasattr(agent_manager.tws_client, "ping"):
                    await agent_manager.tws_client.ping()
                    health_status["components"]["tws_client"] = "reachable"
                elif (
                    hasattr(agent_manager.tws_client, "is_connected")
                    and agent_manager.tws_client.is_connected
                ):
                    health_status["components"]["tws_client"] = "connected"
                else:
                    health_status["components"]["tws_client"] = "unknown"
                    health_status["status"] = "degraded"
            except Exception as e:
                health_status["components"]["tws_client"] = f"error: {str(e)}"
                health_status["status"] = "degraded"
        else:
            health_status["components"]["tws_client"] = "not_initialized"
            health_status["status"] = "degraded"

        # Check Circuit Breaker metrics
        try:
            circuit_metrics = circuit_breaker_manager.get_all_metrics()
            health_status["components"]["circuit_breakers"] = circuit_metrics

            # Check if any circuit breakers are open
            open_breakers = []
            for operation, metrics in circuit_metrics.items():
                if metrics.get("circuit_state") == "open":
                    open_breakers.append(operation)

            if open_breakers:
                health_status["components"][
                    "circuit_breakers_status"
                ] = f"open_circuits: {open_breakers}"
                health_status["status"] = "degraded"
            else:
                health_status["components"]["circuit_breakers_status"] = "all_closed"

        except Exception as e:
            health_status["components"]["circuit_breakers"] = f"error: {str(e)}"
            health_status["status"] = "degraded"

    except (ConnectionError, TimeoutError) as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        log_with_correlation(
            logging.ERROR,
            "Services health check failed due to connectivity",
            correlation_id=correlation_id,
            component="health",
            operation="services_check_error",
            error=e,
        )
    except Exception as e:
        health_status["status"] = "error"
        health_status["error"] = str(e)
        log_with_correlation(
            logging.ERROR,
            "Services health check failed",
            correlation_id=correlation_id,
            component="health",
            operation="services_check_error",
            error=e,
        )

    return health_status