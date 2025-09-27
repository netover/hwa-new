from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from agno.agent import Agent
except ImportError:

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
    """

    def __init__(self, settings_module: Any = settings) -> None:
        """
        Initializes the AgentManager with dependencies.

        Args:
            settings_module: The settings module to use (default: global settings).
        """
        logger.info("Initializing AgentManager.")
        self.settings = settings_module
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        self._mock_tws_client: Optional[MockTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()

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

    async def load_agents_from_config(self, config_path: Path = None) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        # Use provided config_path or get from settings
        config_path = config_path or self.settings.AGENT_CONFIG_PATH
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError as e:
            logger.error(
                "Error decoding JSON from %s: %s", config_path, e, exc_info=True
            )
            self.agents = {}
            self.agent_configs = []
            raise DataParsingError(
                f"Invalid JSON format in agent configuration file: {config_path}"
            ) from e
        except FileNotFoundError as e:
            logger.error("Agent configuration file not found: %s", e, exc_info=True)
            self.agents = {}
            self.agent_configs = []
            raise MissingConfigError(
                f"Agent configuration file not found: {config_path}"
            ) from e
        except PermissionError as e:
            logger.error(
                "Permission denied accessing agent configuration file: %s",
                e,
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []
            raise ConfigError(
                f"Permission denied accessing agent configuration file: {config_path}"
            ) from e
        except ValueError as e:
            logger.error("Invalid agent configuration data: %s", e, exc_info=True)
            self.agents = {}
            self.agent_configs = []
            raise InvalidConfigError(f"Invalid agent configuration data: {e}") from e
        except Exception as e:
            logger.error(
                "An unexpected error occurred while loading agents: %s",
                e,
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []
            raise ConfigError(f"Failed to load agent configurations: {e}") from e

    async def _create_agents(self, agent_configs: List[AgentConfig]) -> Dict[str, Any]:
        """
        Creates agent instances based on the provided configurations.
        """
        agents = {}
        # Ensure the TWS client is ready before creating agents that might need it
        await self._get_tws_client()

        for config in agent_configs:
            try:
                agent_tools = [
                    self.tools[tool_name]
                    for tool_name in config.tools
                    if tool_name in self.tools
                ]

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
                logger.debug(f"Successfully created agent: {config.id}")
            except KeyError as e:
                logger.warning(
                    "Tool '%s' not found for agent '%s'. Agent will be created without it.",
                    e.args[0],
                    config.id,
                )
            except ImportError as e:
                logger.error(
                    "Failed to import dependency for agent '%s': %s",
                    config.id,
                    e,
                    exc_info=True,
                )
                raise AgentError(
                    f"Failed to import dependency for agent '{config.id}': {e}"
                ) from e
            except ValueError as e:
                logger.error(
                    "Invalid configuration for agent '%s': %s",
                    config.id,
                    e,
                    exc_info=True,
                )
                raise AgentError(
                    f"Invalid configuration for agent '{config.id}': {e}"
                ) from e
            except TypeError as e:
                logger.error(
                    "Type error creating agent '%s': %s", config.id, e, exc_info=True
                )
                raise AgentError(f"Type error creating agent '{config.id}': {e}") from e
            except NetworkError as e:
                logger.error(
                    "Network error initializing agent '%s': %s",
                    config.id,
                    e,
                    exc_info=True,
                )
                raise AgentError(
                    f"Network error initializing agent '{config.id}': {e}"
                ) from e
            except Exception as e:
                logger.error(
                    "Failed to create agent '%s': %s", config.id, e, exc_info=True
                )
                raise AgentError(f"Failed to create agent '{config.id}': {e}") from e
        return agents

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Retrieves a loaded agent by its ID."""
        return self.agents.get(agent_id)

    def get_all_agents(self) -> List[AgentConfig]:
        """Returns the configuration of all loaded agents."""
        return self.agent_configs

    def get_agent_with_tool(self, agent_id: str, tool_name: str) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = self.get_agent(agent_id)
        if agent is None:
            logger.warning(f"Agent '{agent_id}' not found")
            raise ValueError(f"Agent {agent_id} not found")

        if any(t.name == tool_name for t in agent.tools):
            return agent
        else:
            logger.warning(f"Tool '{tool_name}' not found for agent '{agent_id}'")
            raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")


# Factory function for creating AgentManager instances
def create_agent_manager(settings_module: Any = settings) -> AgentManager:
    """Create and return a new AgentManager instance."""
    return AgentManager(settings_module=settings_module)


# Legacy compatibility: create a default instance
# This will be removed once all code is migrated to DI
import warnings

warnings.warn(
    "The global agent_manager instance is deprecated and will be removed in a future version. "
    "Use dependency injection with IAgentManager instead.",
    DeprecationWarning,
    stacklevel=2,
)
agent_manager = create_agent_manager()
