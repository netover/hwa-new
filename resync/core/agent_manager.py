from __future__ import annotations

import asyncio
import threading
import json
import structlog
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path
from time import time
from typing import Any, Dict, List, Optional

import aiofiles

try:
    from agno.agent import Agent

    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False

    class MockAgent:
        """Mock Agent class for testing when agno is not available."""

        def __init__(
            self,
            tools: Any = None,
            model: Any = None,
            instructions: Any = None,
            **kwargs: Any,
        ) -> None:
            self.tools = tools or []
            self.model = model
            self.instructions = instructions
            # Mock methods that might be called
            self.run = self._mock_run
            self._mock_run: Any = lambda *args, **kwargs: None


from pydantic import BaseModel

from .global_utils import get_environment_tags, get_global_correlation_id
from resync.core.exceptions import (
    AgentError,  # Renamed from AgentExecutionError for broader scope
    ConfigurationError,
    InvalidConfigError,
    MissingConfigError,
    NetworkError,
    ParsingError,
)
from resync.core.metrics import log_with_correlation, runtime_metrics
from resync.services.mock_tws_service import MockTWSClient
from resync.services.tws_service import OptimizedTWSClient
from resync.settings import settings
from resync.tool_definitions.tws_tools import (
    TWSToolReadOnly,
    tws_status_tool,
    tws_troubleshooting_tool,
)

# --- Logging Setup ---
logger = structlog.get_logger(__name__)


# --- Pydantic Models for Agent Configuration ---
class AgentConfig(BaseModel):
    """Represents the configuration for a single AI agent."""

    id: str
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str]
    model_name: str = "llama3:latest"
    memory: bool = True
    verbose: bool = False


class AgentsConfig(BaseModel):
    """
    Represents the top-level structure of the agent configuration file.
    """

    agents: List[AgentConfig]


# --- Agent Manager Class ---
class AgentManager:
    """
    Manages the lifecycle and operations of AI agents.
    Implements the Borg pattern for thread-safe singleton behavior.
    """
    
    _shared_state: Dict[str, Any] = {}
    _lock = threading.RLock()
    _initialized = False
    
    def __new__(cls):
        """Implementação Borg Pattern - mais pythônico que Singleton clássico."""
        obj = super().__new__(cls)
        obj.__dict__ = cls._shared_state
        return obj

    async def load_agents_from_config(self) -> None:
        """Loads agent configurations from settings."""
        # Implementation for loading agents from config
        pass

    async def get_agent(self, agent_id: str) -> Any:
        """Retrieves an agent by its ID."""
        return self.agents.get(agent_id)

    async def get_all_agents(self) -> List[AgentConfig]:
        """Returns the configuration of all loaded agents."""
        return self.agent_configs

    def _discover_tools(self) -> Dict[str, Any]:
        """Discover available tools for agents."""
        try:
            from resync.tool_definitions.tws_tools import (
                get_workstations_status_tool,
                get_jobs_status_tool,
                get_system_status_tool,
                check_tws_connection_tool,
                invalidate_tws_cache_tool,
            )

            return {
                "get_workstations_status": get_workstations_status_tool,
                "get_jobs_status": get_jobs_status_tool,
                "get_system_status": get_system_status_tool,
                "check_tws_connection": check_tws_connection_tool,
                "invalidate_tws_cache": invalidate_tws_cache_tool,
            }
        except ImportError as e:
            logger.warning(f"Could not import TWS tools: {e}")
            return {}

    def __init__(self, settings_module: Any = settings) -> None:
        """
        Initializes the AgentManager with thread-safe initialization.
        """
        with self._lock:
            if not self._initialized:
                self._initialized = True
                
                global_correlation = get_global_correlation_id()
                correlation_id = runtime_metrics.create_correlation_id(
                    {
                        "component": "agent_manager",
                        "operation": "init",
                        "global_correlation": global_correlation,
                        "environment": get_environment_tags(),
                    }
                )

                try:
                    # Fail-fast check: No MockAgent in production
                    if not AGNO_AVAILABLE:
                        runtime_metrics.agent_mock_fallbacks.increment()
                        is_production = (
                            getattr(settings_module, "ENVIRONMENT", "development").lower()
                            == "production"
                        )
                        if is_production:
                            error_msg = "CRITICAL: agno.agent not available in production environment. Cannot proceed with MockAgent fallback."
                            logger.critical("agno_agent_unavailable_production", error=error_msg, correlation_id=correlation_id)
                            runtime_metrics.record_health_check(
                                "agent_manager",
                                "critical",
                                {"error": "agno_unavailable_production"},
                            )
                            raise AgentError(error_msg)

                        logger.warning(
                            "agno_agent_not_available_non_production",
                            message="agno.agent not available in non-production environment. Using MockAgent fallback.",
                            correlation_id=correlation_id,
                        )
                        runtime_metrics.record_health_check(
                            "agent_manager", "degraded", {"mock_fallback": True}
                        )

                    logger.info("initializing_agent_manager")
                    runtime_metrics.record_health_check("agent_manager", "initializing")

                    self.settings = settings_module
                    self.agents: Dict[str, Any] = {}
                    self.agent_configs: List[AgentConfig] = []
                    self.tools: Dict[str, Any] = self._discover_tools()
                    self.tws_client: Optional[OptimizedTWSClient] = None
                    self._mock_tws_client: Optional[MockTWSClient] = None
                    # Async lock to prevent race conditions during TWS client initialization
                    self._tws_init_lock: asyncio.Lock = asyncio.Lock()

                    runtime_metrics.record_health_check("agent_manager", "healthy")
                    logger.info("agent_manager_initialized_successfully", correlation_id=correlation_id)

                except AgentError as e:
                    # Capture specific, known critical errors during initialization
                    runtime_metrics.record_health_check(
                        "agent_manager", "failed", {"error": str(e)}
                    )
                    logger.critical("agent_manager_initialization_failed", error=str(e), correlation_id=correlation_id, exc_info=True)
                    raise  # Re-raise the specific AgentError
                finally:
                    runtime_metrics.close_correlation_id(correlation_id)


# Global singleton instance for backwards compatibility
agent_manager = AgentManager()
