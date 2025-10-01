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
    AgentError,  # Renamed from AgentExecutionError for broader scope
    ConfigurationError,
    InvalidConfigError,
    MissingConfigError,
    NetworkError,
    ParsingError,
)
from resync.core.metrics import runtime_metrics, log_with_correlation
from resync.core import get_global_correlation_id, get_environment_tags
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
    Implements the singleton pattern to ensure a single instance.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AgentManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, settings_module: Any = settings) -> None:
        """
        Initializes the AgentManager.
        Note: Due to the singleton pattern, this will only run the first time.
        """
        # Prevent re-initialization
        if hasattr(self, "_initialized"):
            return
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
                    log_with_correlation(logging.CRITICAL, error_msg, correlation_id)
                    runtime_metrics.record_health_check(
                        "agent_manager",
                        "critical",
                        {"error": "agno_unavailable_production"},
                    )
                    raise AgentError(error_msg)

                log_with_correlation(
                    logging.WARNING,
                    "agno.agent not available in non-production environment. Using MockAgent fallback.",
                    correlation_id,
                )
                runtime_metrics.record_health_check(
                    "agent_manager", "degraded", {"mock_fallback": True}
                )

            logger.info("Initializing AgentManager.")
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
            log_with_correlation(
                logging.INFO, "AgentManager initialized successfully", correlation_id
            )

        except AgentError as e:
            # Capture specific, known critical errors during initialization
            runtime_metrics.record_health_check(
                "agent_manager", "failed", {"error": str(e)}
            )
            log_with_correlation(logging.CRITICAL, f"AgentManager failed to initialize: {e}", correlation_id, exc_info=True)
            raise  # Re-raise the specific AgentError
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    def _discover_tools(self) -> Dict[str, Any]:
        """
        Discovers and registers available tools for the agents.
        This makes the system extensible for new tools.
        """
        # In a real application, this could be dynamic using entry points
        # For now, we manually register the known tools
        return {
            "tws_status_tool": tws_status_tool,
            "tws_troubleshooting_tool": tws_troubleshooting_tool,
        }

    async def _get_tws_client(self) -> OptimizedTWSClient:
        """
        Lazily initializes and returns the TWS client.
        Ensures a single client instance is reused with async-safe initialization.
        """
        if not self.tws_client:
            # Use async lock to prevent race conditions during initialization
            async with self._tws_init_lock:
                # Double-check pattern: verify the client wasn't created while waiting for the lock
                if not self.tws_client:
                    logger.info("Initializing OptimizedTWSClient for the first time.")
                    self.tws_client = OptimizedTWSClient(
                        hostname=self.settings.TWS_HOST,
            port=self.settings.TWS_PORT,
                        username=self.settings.TWS_USER,
                        password=self.settings.TWS_PASSWORD,
                        engine_name=self.settings.TWS_ENGINE_NAME,
                        engine_owner=self.settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def load_agents_from_config(self, config_path: Optional[Path] = None) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {
                "component": "agent_manager",
                "operation": "load_agents",
                "config_path": str(config_path) if config_path else None,
            }
        )

        try:
            # Use provided config_path or get from settings
            config_path = config_path or self.settings.AGENT_CONFIG_PATH
            log_with_correlation(
                logging.INFO,
                f"Loading agent configurations from: {config_path}",
                correlation_id,
            )

            config_path = Path(config_path)
            if not config_path.exists():
                error_msg = f"Agent configuration file not found at {config_path}"
                log_with_correlation(logging.ERROR, error_msg, correlation_id)
                self.agents = {}
                self.agent_configs = []
                return

            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                config = AgentsConfig.parse_obj(config_data)
                self.agent_configs = config.agents
                self.agents = await self._create_agents(config.agents)

                log_with_correlation(
                    logging.INFO,
                    f"Successfully loaded {len(self.agents)} agents.",
                    correlation_id,
                )
                runtime_metrics.record_health_check(
                    "agent_config", "loaded", {"agent_count": len(self.agents)}
                )

            except json.JSONDecodeError as e:
                log_with_correlation(
                    logging.ERROR,
                    f"Error decoding JSON from {config_path}: {e}",
                    correlation_id,
                    exc_info=True,
                )
                runtime_metrics.record_health_check(
                    "agent_config", "json_error", {"path": str(config_path)}
                )
                self.agents = {}
                self.agent_configs = []
                raise ParsingError(
                    f"Invalid JSON format in agent configuration file: {config_path}"
                ) from e
            except FileNotFoundError as e:
                log_with_correlation(
                    logging.ERROR,
                    f"Agent configuration file not found: {e}",
                    correlation_id,
                    exc_info=True,
                )
                runtime_metrics.record_health_check(
                    "agent_config", "missing", {"path": str(config_path)}
                )
                self.agents = {}
                self.agent_configs = []
                raise MissingConfigError(
                    f"Agent configuration file not found: {config_path}"
                ) from e
            except PermissionError as e:
                log_with_correlation(
                    logging.ERROR,
                    f"Permission denied accessing agent configuration file: {e}",
                    correlation_id,
                    exc_info=True,
                )
                runtime_metrics.record_health_check(
                    "agent_config", "permission_denied", {"path": str(config_path)}
                )
                self.agents = {}
                self.agent_configs = []
                raise ConfigurationError(
                    f"Permission denied accessing agent configuration file: {config_path}"
                ) from e
            except ValueError as e:
                log_with_correlation(
                    logging.ERROR,
                    f"Invalid agent configuration data: {e}",
                    correlation_id,
                    exc_info=True,
                )
                runtime_metrics.record_health_check(
                    "agent_config", "invalid_data", {"error": str(e)}
                )
                self.agents = {}
                self.agent_configs = []
                raise InvalidConfigError(
                    f"Invalid agent configuration data: {e}"
                ) from e
        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    async def _create_agents(self, agent_configs: List[AgentConfig]) -> Dict[str, Any]:
        """
        Creates agent instances based on the provided configurations.
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {
                "component": "agent_manager",
                "operation": "create_agents",
                "agent_count": len(agent_configs),
            }
        )

        agents = {}
        # Ensure the TWS client is ready before creating agents that might need it
        await self._get_tws_client()

        for config in agent_configs:
            agent_correlation = runtime_metrics.create_correlation_id(
                {
                    "component": "agent_manager",
                    "operation": "create_single_agent",
                    "agent_id": config.id,
                    "parent_correlation": correlation_id,
                }
            )

            try:
                runtime_metrics.agent_initializations.increment()

                agent_tools = [
                    self.tools[tool_name]
                    for tool_name in config.tools
                    if tool_name in self.tools
                ]

                missing_tools = [
                    tool_name
                    for tool_name in config.tools
                    if tool_name not in self.tools
                ]
                if missing_tools:
                    log_with_correlation(
                        logging.WARNING,
                        f"Tools not found for agent '{config.id}': {missing_tools}. Agent will be created without them.",
                        agent_correlation,
                    )

                # Using agno.Agent to create the agent instance
                agent = Agent(
                    tools=agent_tools,
                    model=config.model_name,
                    instructions=(
                        f"You are {config.name}, a specialized AI agent. "
                        f"Your role is: {config.role}. "
                        f"Your primary goal is: {config.goal}. "
                        f"Your backstory: {config.backstory}"
                    ),
                )

                agents[config.id] = agent
                runtime_metrics.agent_active_count.set(len(agents))

                log_with_correlation(
                    logging.DEBUG,
                    f"Successfully created agent: {config.id}",
                    agent_correlation,
                )

            except KeyError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(
                    logging.WARNING,
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it.",
                    agent_correlation,
                )
            except ImportError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(
                    logging.ERROR,
                    f"Failed to import dependency for agent '{config.id}': {e}",
                    agent_correlation,
                    exc_info=True,
                )
                raise AgentError(
                    f"Failed to import dependency for agent '{config.id}': {e}"
                ) from e
            except ValueError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(
                    logging.ERROR,
                    f"Invalid configuration for agent '{config.id}': {e}",
                    agent_correlation,
                    exc_info=True,
                )
                raise AgentError(
                    f"Invalid configuration for agent '{config.id}': {e}"
                ) from e
            except TypeError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(
                    logging.ERROR,
                    f"Type error creating agent '{config.id}': {e}",
                    agent_correlation,
                    exc_info=True,
                )
                raise AgentError(f"Type error creating agent '{config.id}': {e}") from e
            except NetworkError as e:
                runtime_metrics.agent_creation_failures.increment()
                log_with_correlation(
                    logging.ERROR,
                    f"Network error initializing agent '{config.id}': {e}",
                    agent_correlation,
                    exc_info=True,
                )
                raise AgentError(
                    f"Network error initializing agent '{config.id}': {e}"
                ) from e
            finally:
                runtime_metrics.close_correlation_id(agent_correlation)

        log_with_correlation(
            logging.INFO, f"Created {len(agents)} agents successfully", correlation_id
        )
        runtime_metrics.close_correlation_id(correlation_id)
        return agents

    async def get_agent(self, agent_id: str) -> Optional[Any]:
        """
        Retrieves a loaded agent by its ID.
        """
        return self.agents.get(agent_id)

    async def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """Retrieves the configuration for a single agent by its ID."""
        # This is a fast, in-memory lookup
        for config in self.agent_configs:
            if config.id == agent_id:
                return config
        return None

    async def get_all_agents(self) -> List[AgentConfig]:
        """
        Returns the configuration of all loaded agents.
        """
        return self.agent_configs

    async def get_agent_with_tool(self, agent_id: str, tool_name: str) -> Optional[Any]:
        """Retrieves an agent if it has the specified tool, raising ValueError if not found."""
        correlation_id = runtime_metrics.create_correlation_id(
            {
                "component": "agent_manager",
                "operation": "get_agent_with_tool",
                "agent_id": agent_id,
                "tool_name": tool_name,
            }
        )

        try:
            agent = await self.get_agent(agent_id)
            if agent is None:
                log_with_correlation(
                    logging.WARNING, f"Agent '{agent_id}' not found", correlation_id
                )
                raise ValueError(f"Agent {agent_id} not found")

            # Correctly check against the agent's configuration
            agent_config = next(
                (c for c in self.agent_configs if c.id == agent_id), None
            )

            if agent_config and tool_name in agent_config.tools:
                return agent
            else:
                log_with_correlation(
                    logging.WARNING,
                    f"Tool '{tool_name}' not found for agent '{agent_id}'",
                    correlation_id,
                )
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
                (
                    (
                        runtime_metrics.agent_initializations.value
                        - runtime_metrics.agent_creation_failures.value
                    )
                    / runtime_metrics.agent_initializations.value
                )
                if runtime_metrics.agent_initializations.value > 0
                else 0
            ),
            "available_tools": list(self.tools.keys()),
            "agent_details": [
                {
                    "id": config.id,
                    "name": config.name,
                    "role": config.role,
                    "tools": config.tools,
                    "model": config.model_name,
                }
                for config in self.agent_configs
            ],
            "health_status": runtime_metrics.get_health_status().get(
                "agent_manager", {}
            ),
            "environment": get_environment_tags(),
        }

    def create_agents_backup(self) -> Dict[str, Any]:
        """
        Create a backup of current agent configurations and state for rollback purposes.
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {"component": "agent_manager", "operation": "create_backup"}
        )

        try:
            backup = {
                "timestamp": time.time(),
                "correlation_id": correlation_id,
                "agent_configs": [config.dict() for config in self.agent_configs],
                "agent_count": len(self.agents),
                "tws_client_connected": self.tws_client is not None,
                "tools_available": list(self.tools.keys()),
                "environment": get_environment_tags(),
            }

            log_with_correlation(
                logging.INFO,
                f"Created agent manager backup with {len(self.agent_configs)} configs",
                correlation_id,
            )
            return backup

        finally:
            runtime_metrics.close_correlation_id(correlation_id)

    async def rollback_agents_to_backup(self, backup: Dict[str, Any]) -> bool:
        """
        Rollback agents to a previous backup state.
        This will recreate all agents from the backup configuration.
        """
        correlation_id = runtime_metrics.create_correlation_id(
            {
                "component": "agent_manager",
                "operation": "rollback_backup",
                "backup_timestamp": backup.get("timestamp"),
            }
        )

        try:
            # Validate backup
            if "agent_configs" not in backup:
                log_with_correlation(
                    logging.ERROR,
                    "Invalid backup format - missing agent_configs",
                    correlation_id,
                )
                return False

            # Validate backup age (don't restore very old backups)
            backup_age = time.time() - backup["timestamp"]
            if backup_age > 3600:  # 1 hour max age
                log_with_correlation(
                    logging.WARNING,
                    f"Backup too old ({backup_age:.0f}s) - refusing rollback",
                    correlation_id,
                )
                return False

            # Clear current state
            old_count = len(self.agents)
            self.agents.clear()
            self.agent_configs.clear()

            # Restore from backup
            from pydantic import parse_obj_as

            restored_configs = [
                AgentConfig.parse_obj(config) for config in backup["agent_configs"]
            ]

            # Recreate agents
            restored_agents = await self._create_agents(restored_configs)
            self.agents = restored_agents
            self.agent_configs = restored_configs

            # Update metrics
            runtime_metrics.agent_active_count.set(len(self.agents))

            log_with_correlation(
                logging.INFO,
                f"Rolled back agents: {old_count} -> {len(self.agents)} agents",
                correlation_id,
            )
            return True

        except Exception as e:
            log_with_correlation(
                logging.ERROR,
                f"Failed to rollback agents: {e}",
                correlation_id,
                exc_info=True,
            )
            return False
        finally:
            runtime_metrics.close_correlation_id(correlation_id)


# Global singleton instance for backwards compatibility
agent_manager = AgentManager()