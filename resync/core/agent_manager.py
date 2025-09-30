from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from time import time
from typing import Any, Dict, List, Optional

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

from resync.core.exceptions import (
    AgentError,
    ConfigError,
    DataParsingError,
    InvalidConfigError,
    MissingConfigError,
    NetworkError,
)
from resync.core.interfaces import ITWSClient
from resync.core.metrics import runtime_metrics, log_with_correlation
from resync.services.mock_tws_service import MockTWSClient
from resync.services.tws_service import OptimizedTWSClient
from resync.settings import settings
from resync.tool_definitions.tws_tools import (
    TWSToolReadOnly,
    tws_status_tool,
    tws_troubleshooting_tool,
)

# --- Logging Setup ---
logger = logging.getLogger(__name__)


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
    Dependencies are injected via the constructor.
    """

    def __init__(
        self, tws_client: ITWSClient, settings_module: Any = settings
    ) -> None:
        """
        Initializes the AgentManager with dependencies.

        Args:
            tws_client: An instance of a TWS client (real or mock).
            settings_module: The settings module to use.
        """
        correlation_id = runtime_metrics.create_correlation_id({
            "component": "agent_manager",
            "operation": "init",
        })

        try:
            # Fail-fast check for agno dependency
            if not AGNO_AVAILABLE:
                self._handle_agno_unavailable(settings_module, correlation_id)

            log_with_correlation(logging.INFO, "Initializing AgentManager.", correlation_id)
            runtime_metrics.record_health_check("agent_manager", "initializing")

            self.settings = settings_module
            self.tws_client = tws_client
            self.agents: Dict[str, Any] = {}
            self.agent_configs: List[AgentConfig] = []
            self.tools: Dict[str, Any] = self._discover_and_configure_tools()

            runtime_metrics.record_health_check("agent_manager", "healthy")
            log_with_correlation(logging.INFO, "AgentManager initialized successfully.", correlation_id)

        except Exception as e:
            runtime_metrics.record_health_check("agent_manager", "failed", {"error": str(e)})
            log_with_correlation(logging.CRITICAL, f"AgentManager initialization failed: {e}", correlation_id, exc_info=True)
            raise
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    def _handle_agno_unavailable(self, settings_module: Any, correlation_id: str) -> None:
        """Handles the case where the 'agno' library is not installed."""
        runtime_metrics.agent_mock_fallbacks.increment()
        is_production = getattr(settings_module, 'APP_ENV', 'development').lower() == 'production'
        if is_production:
            error_msg = "CRITICAL: agno.agent not available in production. Cannot proceed with MockAgent fallback."
            log_with_correlation(logging.CRITICAL, error_msg, correlation_id)
            runtime_metrics.record_health_check("agent_manager", "critical", {"error": "agno_unavailable_production"})
            raise AgentError(error_msg)
        else:
            log_with_correlation(logging.WARNING, "agno.agent not available. Using MockAgent fallback.", correlation_id)
            runtime_metrics.record_health_check("agent_manager", "degraded", {"mock_fallback": True})

    def _discover_and_configure_tools(self) -> Dict[str, Any]:
        """
        Discovers available tools and injects the TWS client into them.
        """
        tools = {
            "tws_status_tool": tws_status_tool,
            "tws_troubleshooting_tool": tws_troubleshooting_tool,
        }
        # Inject the client into tools that need it
        for tool in tools.values():
            if isinstance(tool, TWSToolReadOnly):
                tool.tws_client = self.tws_client
        logger.info(f"Discovered and configured {len(tools)} tools.")
        return tools

    async def load_agents_from_config(self, config_path: Optional[Path] = None) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        correlation_id = runtime_metrics.create_correlation_id({
            "component": "agent_manager",
            "operation": "load_agents",
            "config_path": str(config_path) if config_path else None
        })

        try:
            # Use provided config_path or get from settings, and ensure it's a Path object
            path_str = config_path or self.settings.AGENT_CONFIG_PATH
            config_path = Path(path_str)
            log_with_correlation(logging.INFO, f"Loading agent configurations from: {config_path}", correlation_id)

            if not config_path.exists():
                error_msg = f"Agent configuration file not found at {config_path}"
                log_with_correlation(logging.ERROR, error_msg, correlation_id)
                runtime_metrics.record_health_check("agent_config", "missing", {"path": str(config_path)})
                self.agents = {}
                self.agent_configs = []  # Ensure it's reset if config not found
                return

            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                config = AgentsConfig.parse_obj(config_data)
                self.agent_configs = config.agents  # Correct assignment
                self.agents = await self._create_agents(config.agents)

                log_with_correlation(logging.INFO, f"Successfully loaded {len(self.agents)} agents.", correlation_id)
                runtime_metrics.record_health_check("agent_config", "loaded", {"agent_count": len(self.agents)})

            except json.JSONDecodeError as e:
                log_with_correlation(logging.ERROR,
                    f"Error decoding JSON from {config_path}: {e}", correlation_id, exc_info=True)
                runtime_metrics.record_health_check("agent_config", "json_error", {"path": str(config_path)})
                self.agents = {}
                self.agent_configs = []
                raise DataParsingError(
                    f"Invalid JSON format in agent configuration file: {config_path}"
                ) from e
            except FileNotFoundError as e:
                log_with_correlation(logging.ERROR,
                    f"Agent configuration file not found: {e}", correlation_id, exc_info=True)
                runtime_metrics.record_health_check("agent_config", "missing", {"path": str(config_path)})
                self.agents = {}
                self.agent_configs = []
                raise MissingConfigError(
                    f"Agent configuration file not found: {config_path}"
                ) from e
            except PermissionError as e:
                log_with_correlation(logging.ERROR,
                    f"Permission denied accessing agent configuration file: {e}", correlation_id, exc_info=True)
                runtime_metrics.record_health_check("agent_config", "permission_denied", {"path": str(config_path)})
                self.agents = {}
                self.agent_configs = []
                raise ConfigError(
                    f"Permission denied accessing agent configuration file: {config_path}"
                ) from e
            except ValueError as e:
                log_with_correlation(logging.ERROR,
                    f"Invalid agent configuration data: {e}", correlation_id, exc_info=True)
                runtime_metrics.record_health_check("agent_config", "invalid_data", {"error": str(e)})
                self.agents = {}
                self.agent_configs = []
                raise InvalidConfigError(f"Invalid agent configuration data: {e}") from e
            except Exception as e:
                log_with_correlation(logging.CRITICAL,
                    f"An unexpected critical error occurred while loading agents from {config_path}: {e}",
                    correlation_id, exc_info=True)
                runtime_metrics.record_health_check("agent_config", "critical_error", {"error": str(e)})
                self.agents = {}
                self.agent_configs = []
                raise ConfigError(f"A critical error occurred while loading agent configurations from {config_path}") from e
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    async def _create_agents(self, agent_configs: List[AgentConfig]) -> Dict[str, Any]:
        """
        Creates agent instances based on the provided configurations.
        """
        correlation_id = runtime_metrics.create_correlation_id({
            "component": "agent_manager",
            "operation": "create_agents",
            "agent_count": len(agent_configs)
        })

        agents = {}
        # The TWS client is now injected via the constructor, so it's guaranteed
        # to be available here. No need to fetch it again.

        for config in agent_configs:
            agent_correlation = runtime_metrics.create_correlation_id({
                "component": "agent_manager",
                "operation": "create_single_agent",
                "agent_id": config.id,
                "parent_correlation": correlation_id
            })

            try:
                runtime_metrics.agent_initializations.increment()

                agent_tools = [
                    self.tools[tool_name]
                    for tool_name in config.tools
                    if tool_name in self.tools
                ]

                missing_tools = [tool_name for tool_name in config.tools if tool_name not in self.tools]
                if missing_tools:
                    log_with_correlation(logging.WARNING,
                        f"Tools not found for agent '{config.id}': {missing_tools}. Agent will be created without them.",
                        agent_correlation)

                # Using agno.Agent to create the agent instance
                agent = Agent(
                    tools=agent_tools,
                    # Note: The 'model' parameter in agno.Client refers to the LLM.
                    # We use 'model_name' from our config.
                    model=config.model_name,  # type: ignore[arg-type]
                    # system prompt is constructed from agent personality
                    instructions=(
                        f"You are {config.name}, a specialized AI agent. "
                        f"Your role is: {config.role}. "
                        f"Your primary goal is: {config.goal}. "
                        f"Your backstory: {config.backstory}"
                    ),
                )

                agents[config.id] = agent
                runtime_metrics.agent_active_count.set(len(agents))

                log_with_correlation(logging.DEBUG, f"Successfully created agent: {config.id}", agent_correlation)

            except KeyError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(logging.WARNING,
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it.",
                    agent_correlation)
            except ImportError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(logging.ERROR,
                    f"Failed to import dependency for agent '{config.id}': {e}",
                    agent_correlation, exc_info=True)
                raise AgentError(
                    f"Failed to import dependency for agent '{config.id}': {e}"
                ) from e
            except ValueError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(logging.ERROR,
                    f"Invalid configuration for agent '{config.id}': {e}",
                    agent_correlation, exc_info=True)
                raise AgentError(
                    f"Invalid configuration for agent '{config.id}': {e}"
                ) from e
            except TypeError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(logging.ERROR,
                    f"Type error creating agent '{config.id}': {e}", agent_correlation, exc_info=True)
                raise AgentError(f"Type error creating agent '{config.id}': {e}") from e
            except NetworkError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(logging.ERROR,
                    f"Network error initializing agent '{config.id}': {e}",
                    agent_correlation, exc_info=True)
                raise AgentError(
                    f"Network error initializing agent '{config.id}': {e}"
                ) from e
            except Exception as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(logging.CRITICAL,
                    f"Failed to create agent '{config.id}' due to an unhandled exception: {e}",
                    agent_correlation, exc_info=True)
                raise AgentError(f"An unexpected error occurred while creating agent '{config.id}': {e}") from e
            finally:
                runtime_metrics.close_correlation_id(agent_correlation)

        log_with_correlation(logging.INFO, f"Created {len(agents)} agents successfully", correlation_id)
        runtime_metrics.close_correlation_id(correlation_id)
        return agents

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Retrieves a loaded agent by its ID."""
        return self.agents.get(agent_id)

    def get_all_agents(self) -> List[AgentConfig]:
        """Returns the configuration of all loaded agents."""
        return self.agent_configs

    def get_agent_with_tool(self, agent_id: str, tool_name: str) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        correlation_id = runtime_metrics.create_correlation_id({
            "component": "agent_manager",
            "operation": "get_agent_with_tool",
            "agent_id": agent_id,
            "tool_name": tool_name
        })

        try:
            agent = self.get_agent(agent_id)
            if agent is None:
                log_with_correlation(logging.WARNING, f"Agent '{agent_id}' not found", correlation_id)
                raise ValueError(f"Agent {agent_id} not found")

            if any(t.name == tool_name for t in agent.tools):
                return agent
            else:
                log_with_correlation(logging.WARNING, f"Tool '{tool_name}' not found for agent '{agent_id}'", correlation_id)
                raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get comprehensive agent manager metrics for monitoring."""
        return {
            "total_agents": len(self.agents),
            "agent_configs": len(self.agent_configs),
            "tws_client_available": self.tws_client is not None,
            "mock_tws_client_available": self._mock_tws_client is not None,
            "initializations": runtime_metrics.agent_initializations.value,
            "creation_failures": runtime_metrics.agent_creation_failures.value,
            "mock_fallbacks": runtime_metrics.agent_mock_fallbacks.value,
            "active_count": runtime_metrics.agent_active_count.get(),
            "agent_success_rate": (
                (runtime_metrics.agent_initializations.value - runtime_metrics.agent_creation_failures.value)
                / runtime_metrics.agent_initializations.value
            ) if runtime_metrics.agent_initializations.value > 0 else 0,
            "available_tools": list(self.tools.keys()),
            "agent_details": [
                {
                    "id": config.id,
                    "name": config.name,
                    "role": config.role,
                    "tools": config.tools,
                    "model": config.model_name
                }
                for config in self.agent_configs
            ],
            "health_status": runtime_metrics.get_health_status().get("agent_manager", {}),
        }

    def create_agents_backup(self) -> Dict[str, Any]:
        """
        Create a backup of current agent configurations and state for rollback purposes.
        """
        correlation_id = runtime_metrics.create_correlation_id({
            "component": "agent_manager",
            "operation": "create_backup"
        })

        try:
            backup = {
                "timestamp": time.time(),
                "correlation_id": correlation_id,
                "agent_configs": [config.dict() for config in self.agent_configs],
                "agent_count": len(self.agents),
                "tws_client_connected": self.tws_client is not None,
                "tools_available": list(self.tools.keys()),
            }

            log_with_correlation(logging.INFO, f"Created agent manager backup with {len(self.agent_configs)} configs", correlation_id)
            return backup

        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    async def rollback_agents_to_backup(self, backup: Dict[str, Any]) -> bool:
        """
        Rollback agents to a previous backup state.
        This will recreate all agents from the backup configuration.
        """
        correlation_id = runtime_metrics.create_correlation_id({
            "component": "agent_manager",
            "operation": "rollback_backup",
            "backup_timestamp": backup.get("timestamp")
        })

        try:
            # Validate backup
            if "agent_configs" not in backup:
                log_with_correlation(logging.ERROR, "Invalid backup format - missing agent_configs", correlation_id)
                return False

            # Validate backup age (don't restore very old backups)
            backup_age = time.time() - backup["timestamp"]
            if backup_age > 3600:  # 1 hour max age
                log_with_correlation(logging.WARNING, f"Backup too old ({backup_age:.0f}s) - refusing rollback", correlation_id)
                return False

            # Clear current state
            old_count = len(self.agents)
            self.agents.clear()
            self.agent_configs.clear()

            # Restore from backup
            from pydantic import parse_obj_as
            restored_configs = [AgentConfig.parse_obj(config) for config in backup["agent_configs"]]

            # Recreate agents
            restored_agents = await self._create_agents(restored_configs)
            self.agents = restored_agents
            self.agent_configs = restored_configs

            # Update metrics
            runtime_metrics.agent_active_count.set(len(self.agents))

            log_with_correlation(logging.INFO,
                f"Rolled back agents: {old_count} -> {len(self.agents)} agents", correlation_id)
            return True

        except Exception as e:
            log_with_correlation(logging.ERROR, f"Failed to rollback agents: {e}", correlation_id, exc_info=True)
            return False
        finally:
            runtime_metrics.close_correlation_id(correlation_id)


# The global singleton `agent_manager` has been removed as part of the
# architectural refactoring to eliminate global state.
# The AgentManager class should now be instantiated and managed by the
# central dependency injection container.