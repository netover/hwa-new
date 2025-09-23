from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# from agno import Agent
# from agno.tools import Tool


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
    This class is a singleton, ensuring a single source of truth for agent state.
    """

    _instance: Optional[AgentManager] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> AgentManager:
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("Initializing AgentManager singleton.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = [] # Correct initialization
        self.tools: Dict[str, Tool] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True


    def _discover_tools(self) -> Dict[str, Tool]:
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
                        hostname=settings.TWS_HOST,
                        port=settings.TWS_PORT,
                        username=settings.TWS_USER,
                        password=settings.TWS_PASSWORD,
                        engine_name=settings.TWS_ENGINE_NAME,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool.model, TWSToolReadOnly):
                            tool.model.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def load_agents_from_config(self, config_path: Path = settings.AGENT_CONFIG_PATH):
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = [] # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(f"An unexpected error occurred while loading agents", exc_info=True)
            self.agents = {}
            self.agent_configs = []

    async def _create_agents(self, agent_configs: List[AgentConfig]) -> Dict[str, Any]:
        """
        Creates agent instances based on the provided configurations.
        """
        agents = {}
        # Ensure the TWS client is ready before creating agents that might need it
        await self._get_tws_client()

        for config in agent_configs:
            try:
                agent_tools = [self.tools[tool_name] for tool_name in config.tools if tool_name in self.tools]

                # Using agno.Agent to create the agent instance
                agent = Agent(
                    tools=agent_tools,
                    # Note: The 'model' parameter in agno.Client refers to the LLM.
                    # We use 'model_name' from our config.
                    model=config.model_name,
                    # system prompt is constructed from agent personality
                    system=(
                        f"You are {config.name}, a specialized AI agent. "
                        f"Your role is: {config.role}. "
                        f"Your primary goal is: {config.goal}. "
                        f"Your backstory: {config.backstory}"
                    ),
                    verbose=config.verbose,
                )
                agents[config.id] = agent
                logger.debug(f"Successfully created agent: {config.id}")
            except KeyError as e:
                logger.warning(f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it.")
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Retrieves a loaded agent by its ID."""
        return self.agents.get(agent_id)

    def get_all_agents(self) -> List[AgentConfig]:
        """Returns the configuration of all loaded agents."""
        return self.agent_configs


# --- Singleton Instance ---
# Create a single, globally accessible instance of the AgentManager.
agent_manager = AgentManager()