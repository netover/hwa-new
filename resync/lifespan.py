from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from redis.exceptions import (
    AuthenticationError,
    BusyLoadingError,
    ConnectionError,
    ResponseError,
    TimeoutError,
)

from resync.settings import settings
from resync.core.container import app_container
from resync.core.interfaces import ITWSClient, IAgentManager, IKnowledgeGraph
from resync.core.tws_monitor import get_tws_monitor, shutdown_tws_monitor
from resync.cqrs.dispatcher import initialize_dispatcher
from resync.api_gateway.container import setup_dependencies
from resync.core.redis_init import RedisInitializer

from resync.core.structured_logger import get_logger

logger = get_logger(__name__)

class RedisStartupError(Exception):
    """Critical error during Redis initialization."""
    pass

# Create a global RedisInitializer instance
redis_initializer = RedisInitializer()

async def initialize_redis_with_retry(
    max_retries: int = 3,
    base_backoff: float = 0.1,
    max_backoff: float = 10.0
) -> None:
    """
    Initialize Redis with the robust RedisInitializer.
    
    Args:
        max_retries: Maximum number of attempts
        base_backoff: Base backoff time in seconds
        max_backoff: Maximum backoff time in seconds
        
    Raises:
        RedisStartupError: If failed after all attempts
    """
    # Environment validation
    redis_url = getattr(settings, 'REDIS_URL', None)
    if not redis_url:
        logger.critical("redis_url_not_configured")
        raise RedisStartupError("REDIS_URL environment variable not set")

    # Skip Redis initialization in development if Redis is not available
    environment = getattr(settings, 'APP_ENV', 'development')
    if environment == 'development':
        try:
            import redis
            # Quick test to see if Redis is available
            sync_client = redis.Redis.from_url(redis_url, socket_timeout=2)
            sync_client.ping()
            sync_client.close()
        except Exception as e:
            logger.warning(
                "redis_not_available_in_development",
                error=str(e),
                message="Redis not available, skipping Redis-dependent features for development"
            )
            return
    
    # Startup metrics
    startup_metrics = {
        "attempts": 0,
        "connection_failures": 0,
        "auth_failures": 0,
        "duration_seconds": 0.0
    }
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Use the robust RedisInitializer
        redis_client = await redis_initializer.initialize(
            max_retries=max_retries,
            base_backoff=base_backoff,
            max_backoff=max_backoff
        )
        
        # Initialize idempotency manager
        from resync.api.dependencies import initialize_idempotency_manager
        await initialize_idempotency_manager(redis_client)
        
        # Success
        startup_metrics["duration_seconds"] = (
            asyncio.get_event_loop().time() - start_time
        )
        
        logger.info(
            "redis_initialized_successfully",
            metrics=startup_metrics,
            duration_ms=int(startup_metrics["duration_seconds"] * 1000)
        )
        
    except (ConnectionError, TimeoutError, BusyLoadingError, AuthenticationError) as e:
        startup_metrics["connection_failures"] += 1
        logger.critical(
            "redis_initialization_failed",
            reason="initialization_failed",
            metrics=startup_metrics,
            error_type=type(e).__name__
        )
        raise RedisStartupError(
            f"Redis initialization failed: {str(e)}"
        ) from e
    except Exception as e:
        logger.critical(
            "redis_unexpected_error",
            error_type=type(e).__name__,
            message=str(e) if settings.ENVIRONMENT != "production" else None
        )
        raise RedisStartupError(f"Unexpected error during Redis initialization: {type(e).__name__}") from e


@asynccontextmanager
async def lifespan_with_improvements(app: FastAPI) -> AsyncIterator[None]:
    """Manage the application lifecycle with improvements."""
    logger.info("starting_application_with_improvements")
    
    # Startup
    try:
        # Get required services from DI container
        tws_client = await app_container.get(ITWSClient)
        agent_manager = await app_container.get(IAgentManager)
        knowledge_graph = await app_container.get(IKnowledgeGraph)
        
        # Initialize TWS monitor
        tws_monitor_instance = await get_tws_monitor(tws_client)
        
        # Setup dependency injection
        setup_dependencies(tws_client, agent_manager, knowledge_graph)
        
        # Initialize CQRS dispatcher
        initialize_dispatcher(tws_client, tws_monitor_instance)
        
        # Initialize Redis with improved retry logic
        await initialize_redis_with_retry(
            max_retries=getattr(settings, 'redis_max_startup_retries', 3),
            base_backoff=getattr(settings, 'redis_startup_backoff_base', 0.1),
            max_backoff=getattr(settings, 'redis_startup_backoff_max', 10.0)
        )
        
        logger.info("application_startup_completed_successfully")
        
        yield  # Application runs here
        
    except RedisStartupError:
        # Error already logged, propagate to FastAPI
        sys.exit(1)
    except Exception as e:
        logger.critical(
            "failed_to_start_application",
            error=str(e),
            exc_info=True
        )
        raise
    
    finally:
        # Shutdown
        logger.info("shutting_down_application")
        
        try:
            await shutdown_tws_monitor()
            logger.info("application_shutdown_completed_successfully")
        except Exception as e:
            logger.error(
                "error_during_shutdown",
                error=str(e),
                exc_info=True
            )