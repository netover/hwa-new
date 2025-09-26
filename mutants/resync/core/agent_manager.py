from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from agno.agent import Agent
except ImportError:

    class Agent:
        """Mock Agent class for testing when agno is not available."""

        def __init__(self, tools=None, model=None, instructions=None, **kwargs):
            self.tools = tools or []
            self.model = model
            self.instructions = instructions
            # Mock methods that might be called
            self.run = self._mock_run
            self._mock_run = lambda *args, **kwargs: None


from pydantic import BaseModel

from resync.services.tws_service import OptimizedTWSClient
from resync.settings import settings
from resync.tool_definitions.tws_tools import (
    TWSToolReadOnly,
    tws_status_tool,
    tws_troubleshooting_tool,
)

# --- Logging Setup ---
logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


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

    def xǁAgentManagerǁ__init____mutmut_orig(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("Initializing AgentManager singleton.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_1(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info(None)
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_2(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("XXInitializing AgentManager singleton.XX")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_3(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("initializing agentmanager singleton.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_4(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("INITIALIZING AGENTMANAGER SINGLETON.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_5(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("Initializing AgentManager singleton.")
        self.agents: Dict[str, Any] = None
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_6(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("Initializing AgentManager singleton.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = None  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_7(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("Initializing AgentManager singleton.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = None
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_8(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("Initializing AgentManager singleton.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = ""
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_9(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("Initializing AgentManager singleton.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = None
        self._initialized = True

    def xǁAgentManagerǁ__init____mutmut_10(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("Initializing AgentManager singleton.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = None

    def xǁAgentManagerǁ__init____mutmut_11(self):
        """
        Initializes the AgentManager.
        The singleton pattern ensures this runs only once.
        """
        if self._initialized:
            return
        logger.info("Initializing AgentManager singleton.")
        self.agents: Dict[str, Any] = {}
        self.agent_configs: List[AgentConfig] = []  # Correct initialization
        self.tools: Dict[str, Any] = self._discover_tools()
        self.tws_client: Optional[OptimizedTWSClient] = None
        # Async lock to prevent race conditions during TWS client initialization
        self._tws_init_lock: asyncio.Lock = asyncio.Lock()
        self._initialized = False

    xǁAgentManagerǁ__init____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAgentManagerǁ__init____mutmut_1": xǁAgentManagerǁ__init____mutmut_1,
        "xǁAgentManagerǁ__init____mutmut_2": xǁAgentManagerǁ__init____mutmut_2,
        "xǁAgentManagerǁ__init____mutmut_3": xǁAgentManagerǁ__init____mutmut_3,
        "xǁAgentManagerǁ__init____mutmut_4": xǁAgentManagerǁ__init____mutmut_4,
        "xǁAgentManagerǁ__init____mutmut_5": xǁAgentManagerǁ__init____mutmut_5,
        "xǁAgentManagerǁ__init____mutmut_6": xǁAgentManagerǁ__init____mutmut_6,
        "xǁAgentManagerǁ__init____mutmut_7": xǁAgentManagerǁ__init____mutmut_7,
        "xǁAgentManagerǁ__init____mutmut_8": xǁAgentManagerǁ__init____mutmut_8,
        "xǁAgentManagerǁ__init____mutmut_9": xǁAgentManagerǁ__init____mutmut_9,
        "xǁAgentManagerǁ__init____mutmut_10": xǁAgentManagerǁ__init____mutmut_10,
        "xǁAgentManagerǁ__init____mutmut_11": xǁAgentManagerǁ__init____mutmut_11,
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAgentManagerǁ__init____mutmut_orig"),
            object.__getattribute__(self, "xǁAgentManagerǁ__init____mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    __init__.__signature__ = _mutmut_signature(xǁAgentManagerǁ__init____mutmut_orig)
    xǁAgentManagerǁ__init____mutmut_orig.__name__ = "xǁAgentManagerǁ__init__"

    def xǁAgentManagerǁ_discover_tools__mutmut_orig(self) -> Dict[str, Any]:
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

    def xǁAgentManagerǁ_discover_tools__mutmut_1(self) -> Dict[str, Any]:
        """
        Discovers and registers available tools for the agents.
        This makes the system extensible for new tools.
        """
        # In a real application, this could be dynamic using entry points
        # For now, we manually register the known tools
        return {
            "XXtws_status_toolXX": tws_status_tool,
            "tws_troubleshooting_tool": tws_troubleshooting_tool,
        }

    def xǁAgentManagerǁ_discover_tools__mutmut_2(self) -> Dict[str, Any]:
        """
        Discovers and registers available tools for the agents.
        This makes the system extensible for new tools.
        """
        # In a real application, this could be dynamic using entry points
        # For now, we manually register the known tools
        return {
            "TWS_STATUS_TOOL": tws_status_tool,
            "tws_troubleshooting_tool": tws_troubleshooting_tool,
        }

    def xǁAgentManagerǁ_discover_tools__mutmut_3(self) -> Dict[str, Any]:
        """
        Discovers and registers available tools for the agents.
        This makes the system extensible for new tools.
        """
        # In a real application, this could be dynamic using entry points
        # For now, we manually register the known tools
        return {
            "tws_status_tool": tws_status_tool,
            "XXtws_troubleshooting_toolXX": tws_troubleshooting_tool,
        }

    def xǁAgentManagerǁ_discover_tools__mutmut_4(self) -> Dict[str, Any]:
        """
        Discovers and registers available tools for the agents.
        This makes the system extensible for new tools.
        """
        # In a real application, this could be dynamic using entry points
        # For now, we manually register the known tools
        return {
            "tws_status_tool": tws_status_tool,
            "TWS_TROUBLESHOOTING_TOOL": tws_troubleshooting_tool,
        }

    xǁAgentManagerǁ_discover_tools__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAgentManagerǁ_discover_tools__mutmut_1": xǁAgentManagerǁ_discover_tools__mutmut_1,
        "xǁAgentManagerǁ_discover_tools__mutmut_2": xǁAgentManagerǁ_discover_tools__mutmut_2,
        "xǁAgentManagerǁ_discover_tools__mutmut_3": xǁAgentManagerǁ_discover_tools__mutmut_3,
        "xǁAgentManagerǁ_discover_tools__mutmut_4": xǁAgentManagerǁ_discover_tools__mutmut_4,
    }

    def _discover_tools(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁAgentManagerǁ_discover_tools__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁAgentManagerǁ_discover_tools__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    _discover_tools.__signature__ = _mutmut_signature(
        xǁAgentManagerǁ_discover_tools__mutmut_orig
    )
    xǁAgentManagerǁ_discover_tools__mutmut_orig.__name__ = (
        "xǁAgentManagerǁ_discover_tools"
    )

    async def xǁAgentManagerǁ_get_tws_client__mutmut_orig(self) -> OptimizedTWSClient:
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_1(self) -> OptimizedTWSClient:
        """
        Lazily initializes and returns the TWS client.
        Ensures a single client instance is reused with async-safe initialization.
        """
        if self.tws_client:
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_2(self) -> OptimizedTWSClient:
        """
        Lazily initializes and returns the TWS client.
        Ensures a single client instance is reused with async-safe initialization.
        """
        if not self.tws_client:
            # Use async lock to prevent race conditions during initialization
            async with self._tws_init_lock:
                # Double-check pattern: verify the client wasn't created while waiting for the lock
                if self.tws_client:
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_3(self) -> OptimizedTWSClient:
        """
        Lazily initializes and returns the TWS client.
        Ensures a single client instance is reused with async-safe initialization.
        """
        if not self.tws_client:
            # Use async lock to prevent race conditions during initialization
            async with self._tws_init_lock:
                # Double-check pattern: verify the client wasn't created while waiting for the lock
                if not self.tws_client:
                    logger.info(None)
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_4(self) -> OptimizedTWSClient:
        """
        Lazily initializes and returns the TWS client.
        Ensures a single client instance is reused with async-safe initialization.
        """
        if not self.tws_client:
            # Use async lock to prevent race conditions during initialization
            async with self._tws_init_lock:
                # Double-check pattern: verify the client wasn't created while waiting for the lock
                if not self.tws_client:
                    logger.info(
                        "XXInitializing OptimizedTWSClient for the first time.XX"
                    )
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_5(self) -> OptimizedTWSClient:
        """
        Lazily initializes and returns the TWS client.
        Ensures a single client instance is reused with async-safe initialization.
        """
        if not self.tws_client:
            # Use async lock to prevent race conditions during initialization
            async with self._tws_init_lock:
                # Double-check pattern: verify the client wasn't created while waiting for the lock
                if not self.tws_client:
                    logger.info("initializing optimizedtwsclient for the first time.")
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_6(self) -> OptimizedTWSClient:
        """
        Lazily initializes and returns the TWS client.
        Ensures a single client instance is reused with async-safe initialization.
        """
        if not self.tws_client:
            # Use async lock to prevent race conditions during initialization
            async with self._tws_init_lock:
                # Double-check pattern: verify the client wasn't created while waiting for the lock
                if not self.tws_client:
                    logger.info("INITIALIZING OPTIMIZEDTWSCLIENT FOR THE FIRST TIME.")
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_7(self) -> OptimizedTWSClient:
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
                    self.tws_client = None
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_8(self) -> OptimizedTWSClient:
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
                        hostname=None,
                        port=settings.TWS_PORT,
                        username=settings.TWS_USER,
                        password=settings.TWS_PASSWORD,
                        engine_name=settings.TWS_ENGINE_NAME,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_9(self) -> OptimizedTWSClient:
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
                        port=None,
                        username=settings.TWS_USER,
                        password=settings.TWS_PASSWORD,
                        engine_name=settings.TWS_ENGINE_NAME,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_10(self) -> OptimizedTWSClient:
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
                        username=None,
                        password=settings.TWS_PASSWORD,
                        engine_name=settings.TWS_ENGINE_NAME,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_11(self) -> OptimizedTWSClient:
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
                        password=None,
                        engine_name=settings.TWS_ENGINE_NAME,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_12(self) -> OptimizedTWSClient:
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
                        engine_name=None,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_13(self) -> OptimizedTWSClient:
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
                        engine_owner=None,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_14(self) -> OptimizedTWSClient:
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
                        port=settings.TWS_PORT,
                        username=settings.TWS_USER,
                        password=settings.TWS_PASSWORD,
                        engine_name=settings.TWS_ENGINE_NAME,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_15(self) -> OptimizedTWSClient:
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
                        username=settings.TWS_USER,
                        password=settings.TWS_PASSWORD,
                        engine_name=settings.TWS_ENGINE_NAME,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_16(self) -> OptimizedTWSClient:
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
                        password=settings.TWS_PASSWORD,
                        engine_name=settings.TWS_ENGINE_NAME,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_17(self) -> OptimizedTWSClient:
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
                        engine_name=settings.TWS_ENGINE_NAME,
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_18(self) -> OptimizedTWSClient:
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
                        engine_owner=settings.TWS_ENGINE_OWNER,
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_19(self) -> OptimizedTWSClient:
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
                    )
                    # Inject the client into tools that need it
                    for tool in self.tools.values():
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_20(self) -> OptimizedTWSClient:
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = None
                    logger.info("TWS client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_21(self) -> OptimizedTWSClient:
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info(None)
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_22(self) -> OptimizedTWSClient:
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("XXTWS client initialization completed successfully.XX")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_23(self) -> OptimizedTWSClient:
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("tws client initialization completed successfully.")
        return self.tws_client

    async def xǁAgentManagerǁ_get_tws_client__mutmut_24(self) -> OptimizedTWSClient:
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
                        if isinstance(tool, TWSToolReadOnly):
                            tool.tws_client = self.tws_client
                    logger.info("TWS CLIENT INITIALIZATION COMPLETED SUCCESSFULLY.")
        return self.tws_client

    xǁAgentManagerǁ_get_tws_client__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAgentManagerǁ_get_tws_client__mutmut_1": xǁAgentManagerǁ_get_tws_client__mutmut_1,
        "xǁAgentManagerǁ_get_tws_client__mutmut_2": xǁAgentManagerǁ_get_tws_client__mutmut_2,
        "xǁAgentManagerǁ_get_tws_client__mutmut_3": xǁAgentManagerǁ_get_tws_client__mutmut_3,
        "xǁAgentManagerǁ_get_tws_client__mutmut_4": xǁAgentManagerǁ_get_tws_client__mutmut_4,
        "xǁAgentManagerǁ_get_tws_client__mutmut_5": xǁAgentManagerǁ_get_tws_client__mutmut_5,
        "xǁAgentManagerǁ_get_tws_client__mutmut_6": xǁAgentManagerǁ_get_tws_client__mutmut_6,
        "xǁAgentManagerǁ_get_tws_client__mutmut_7": xǁAgentManagerǁ_get_tws_client__mutmut_7,
        "xǁAgentManagerǁ_get_tws_client__mutmut_8": xǁAgentManagerǁ_get_tws_client__mutmut_8,
        "xǁAgentManagerǁ_get_tws_client__mutmut_9": xǁAgentManagerǁ_get_tws_client__mutmut_9,
        "xǁAgentManagerǁ_get_tws_client__mutmut_10": xǁAgentManagerǁ_get_tws_client__mutmut_10,
        "xǁAgentManagerǁ_get_tws_client__mutmut_11": xǁAgentManagerǁ_get_tws_client__mutmut_11,
        "xǁAgentManagerǁ_get_tws_client__mutmut_12": xǁAgentManagerǁ_get_tws_client__mutmut_12,
        "xǁAgentManagerǁ_get_tws_client__mutmut_13": xǁAgentManagerǁ_get_tws_client__mutmut_13,
        "xǁAgentManagerǁ_get_tws_client__mutmut_14": xǁAgentManagerǁ_get_tws_client__mutmut_14,
        "xǁAgentManagerǁ_get_tws_client__mutmut_15": xǁAgentManagerǁ_get_tws_client__mutmut_15,
        "xǁAgentManagerǁ_get_tws_client__mutmut_16": xǁAgentManagerǁ_get_tws_client__mutmut_16,
        "xǁAgentManagerǁ_get_tws_client__mutmut_17": xǁAgentManagerǁ_get_tws_client__mutmut_17,
        "xǁAgentManagerǁ_get_tws_client__mutmut_18": xǁAgentManagerǁ_get_tws_client__mutmut_18,
        "xǁAgentManagerǁ_get_tws_client__mutmut_19": xǁAgentManagerǁ_get_tws_client__mutmut_19,
        "xǁAgentManagerǁ_get_tws_client__mutmut_20": xǁAgentManagerǁ_get_tws_client__mutmut_20,
        "xǁAgentManagerǁ_get_tws_client__mutmut_21": xǁAgentManagerǁ_get_tws_client__mutmut_21,
        "xǁAgentManagerǁ_get_tws_client__mutmut_22": xǁAgentManagerǁ_get_tws_client__mutmut_22,
        "xǁAgentManagerǁ_get_tws_client__mutmut_23": xǁAgentManagerǁ_get_tws_client__mutmut_23,
        "xǁAgentManagerǁ_get_tws_client__mutmut_24": xǁAgentManagerǁ_get_tws_client__mutmut_24,
    }

    def _get_tws_client(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁAgentManagerǁ_get_tws_client__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁAgentManagerǁ_get_tws_client__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    _get_tws_client.__signature__ = _mutmut_signature(
        xǁAgentManagerǁ_get_tws_client__mutmut_orig
    )
    xǁAgentManagerǁ_get_tws_client__mutmut_orig.__name__ = (
        "xǁAgentManagerǁ_get_tws_client"
    )

    async def xǁAgentManagerǁload_agents_from_config__mutmut_orig(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_1(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(None)
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_2(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if config_path.exists():
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_3(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(None)
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_4(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = None
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_5(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = None  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_6(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(None, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_7(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, None, encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_8(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding=None) as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_9(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open("r", encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_10(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_11(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(
                config_path,
                "r",
            ) as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_12(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "XXrXX", encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_13(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "R", encoding="utf-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_14(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="XXutf-8XX") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_15(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="UTF-8") as f:
                config_data = json.load(f)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_16(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = None

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_17(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(None)

            config = AgentsConfig.parse_obj(config_data)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_18(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                json.load(f)

            config = None
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_19(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
        logger.info(f"Loading agent configurations from: {config_path}")
        if not config_path.exists():
            logger.error(f"Agent configuration file not found at {config_path}")
            self.agents = {}
            self.agent_configs = []  # Ensure it's reset if config not found
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                json.load(f)

            config = AgentsConfig.parse_obj(None)
            self.agent_configs = config.agents  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_20(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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
            self.agent_configs = None  # Correct assignment
            self.agents = await self._create_agents(config.agents)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_21(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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
            self.agents = None
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_22(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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
            self.agents = await self._create_agents(None)
            logger.info(f"Successfully loaded {len(self.agents)} agents.")

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_23(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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
            logger.info(None)

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_24(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(None, exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_25(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=None)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_26(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_27(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(
                f"Error decoding JSON from {config_path}",
            )
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_28(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=False)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_29(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = None
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_30(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = None
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_31(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                None,
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_32(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=None,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_33(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_34(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_35(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "XXAn unexpected error occurred while loading agentsXX",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_36(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "an unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_37(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "AN UNEXPECTED ERROR OCCURRED WHILE LOADING AGENTS",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_38(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=False,
            )
            self.agents = {}
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_39(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = None
            self.agent_configs = []

    async def xǁAgentManagerǁload_agents_from_config__mutmut_40(
        self, config_path: Path = settings.AGENT_CONFIG_PATH
    ) -> None:
        """
        Loads agent configurations from a JSON file and initializes them.
        This method is designed to be idempotent.
        """
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

        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {config_path}", exc_info=True)
            self.agents = {}
            self.agent_configs = []
        except Exception:
            logger.error(
                "An unexpected error occurred while loading agents",
                exc_info=True,
            )
            self.agents = {}
            self.agent_configs = None

    xǁAgentManagerǁload_agents_from_config__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAgentManagerǁload_agents_from_config__mutmut_1": xǁAgentManagerǁload_agents_from_config__mutmut_1,
        "xǁAgentManagerǁload_agents_from_config__mutmut_2": xǁAgentManagerǁload_agents_from_config__mutmut_2,
        "xǁAgentManagerǁload_agents_from_config__mutmut_3": xǁAgentManagerǁload_agents_from_config__mutmut_3,
        "xǁAgentManagerǁload_agents_from_config__mutmut_4": xǁAgentManagerǁload_agents_from_config__mutmut_4,
        "xǁAgentManagerǁload_agents_from_config__mutmut_5": xǁAgentManagerǁload_agents_from_config__mutmut_5,
        "xǁAgentManagerǁload_agents_from_config__mutmut_6": xǁAgentManagerǁload_agents_from_config__mutmut_6,
        "xǁAgentManagerǁload_agents_from_config__mutmut_7": xǁAgentManagerǁload_agents_from_config__mutmut_7,
        "xǁAgentManagerǁload_agents_from_config__mutmut_8": xǁAgentManagerǁload_agents_from_config__mutmut_8,
        "xǁAgentManagerǁload_agents_from_config__mutmut_9": xǁAgentManagerǁload_agents_from_config__mutmut_9,
        "xǁAgentManagerǁload_agents_from_config__mutmut_10": xǁAgentManagerǁload_agents_from_config__mutmut_10,
        "xǁAgentManagerǁload_agents_from_config__mutmut_11": xǁAgentManagerǁload_agents_from_config__mutmut_11,
        "xǁAgentManagerǁload_agents_from_config__mutmut_12": xǁAgentManagerǁload_agents_from_config__mutmut_12,
        "xǁAgentManagerǁload_agents_from_config__mutmut_13": xǁAgentManagerǁload_agents_from_config__mutmut_13,
        "xǁAgentManagerǁload_agents_from_config__mutmut_14": xǁAgentManagerǁload_agents_from_config__mutmut_14,
        "xǁAgentManagerǁload_agents_from_config__mutmut_15": xǁAgentManagerǁload_agents_from_config__mutmut_15,
        "xǁAgentManagerǁload_agents_from_config__mutmut_16": xǁAgentManagerǁload_agents_from_config__mutmut_16,
        "xǁAgentManagerǁload_agents_from_config__mutmut_17": xǁAgentManagerǁload_agents_from_config__mutmut_17,
        "xǁAgentManagerǁload_agents_from_config__mutmut_18": xǁAgentManagerǁload_agents_from_config__mutmut_18,
        "xǁAgentManagerǁload_agents_from_config__mutmut_19": xǁAgentManagerǁload_agents_from_config__mutmut_19,
        "xǁAgentManagerǁload_agents_from_config__mutmut_20": xǁAgentManagerǁload_agents_from_config__mutmut_20,
        "xǁAgentManagerǁload_agents_from_config__mutmut_21": xǁAgentManagerǁload_agents_from_config__mutmut_21,
        "xǁAgentManagerǁload_agents_from_config__mutmut_22": xǁAgentManagerǁload_agents_from_config__mutmut_22,
        "xǁAgentManagerǁload_agents_from_config__mutmut_23": xǁAgentManagerǁload_agents_from_config__mutmut_23,
        "xǁAgentManagerǁload_agents_from_config__mutmut_24": xǁAgentManagerǁload_agents_from_config__mutmut_24,
        "xǁAgentManagerǁload_agents_from_config__mutmut_25": xǁAgentManagerǁload_agents_from_config__mutmut_25,
        "xǁAgentManagerǁload_agents_from_config__mutmut_26": xǁAgentManagerǁload_agents_from_config__mutmut_26,
        "xǁAgentManagerǁload_agents_from_config__mutmut_27": xǁAgentManagerǁload_agents_from_config__mutmut_27,
        "xǁAgentManagerǁload_agents_from_config__mutmut_28": xǁAgentManagerǁload_agents_from_config__mutmut_28,
        "xǁAgentManagerǁload_agents_from_config__mutmut_29": xǁAgentManagerǁload_agents_from_config__mutmut_29,
        "xǁAgentManagerǁload_agents_from_config__mutmut_30": xǁAgentManagerǁload_agents_from_config__mutmut_30,
        "xǁAgentManagerǁload_agents_from_config__mutmut_31": xǁAgentManagerǁload_agents_from_config__mutmut_31,
        "xǁAgentManagerǁload_agents_from_config__mutmut_32": xǁAgentManagerǁload_agents_from_config__mutmut_32,
        "xǁAgentManagerǁload_agents_from_config__mutmut_33": xǁAgentManagerǁload_agents_from_config__mutmut_33,
        "xǁAgentManagerǁload_agents_from_config__mutmut_34": xǁAgentManagerǁload_agents_from_config__mutmut_34,
        "xǁAgentManagerǁload_agents_from_config__mutmut_35": xǁAgentManagerǁload_agents_from_config__mutmut_35,
        "xǁAgentManagerǁload_agents_from_config__mutmut_36": xǁAgentManagerǁload_agents_from_config__mutmut_36,
        "xǁAgentManagerǁload_agents_from_config__mutmut_37": xǁAgentManagerǁload_agents_from_config__mutmut_37,
        "xǁAgentManagerǁload_agents_from_config__mutmut_38": xǁAgentManagerǁload_agents_from_config__mutmut_38,
        "xǁAgentManagerǁload_agents_from_config__mutmut_39": xǁAgentManagerǁload_agents_from_config__mutmut_39,
        "xǁAgentManagerǁload_agents_from_config__mutmut_40": xǁAgentManagerǁload_agents_from_config__mutmut_40,
    }

    def load_agents_from_config(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁAgentManagerǁload_agents_from_config__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁAgentManagerǁload_agents_from_config__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    load_agents_from_config.__signature__ = _mutmut_signature(
        xǁAgentManagerǁload_agents_from_config__mutmut_orig
    )
    xǁAgentManagerǁload_agents_from_config__mutmut_orig.__name__ = (
        "xǁAgentManagerǁload_agents_from_config"
    )

    async def xǁAgentManagerǁ_create_agents__mutmut_orig(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_1(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
        """
        Creates agent instances based on the provided configurations.
        """
        agents = None
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
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_2(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
        """
        Creates agent instances based on the provided configurations.
        """
        agents = {}
        # Ensure the TWS client is ready before creating agents that might need it
        await self._get_tws_client()

        for config in agent_configs:
            try:
                agent_tools = None

                # Using agno.Agent to create the agent instance
                agent = Agent(
                    tools=agent_tools,
                    # Note: The 'model' parameter in agno.Client refers to the LLM.
                    # We use 'model_name' from our config.
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_3(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    if tool_name not in self.tools
                ]

                # Using agno.Agent to create the agent instance
                agent = Agent(
                    tools=agent_tools,
                    # Note: The 'model' parameter in agno.Client refers to the LLM.
                    # We use 'model_name' from our config.
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_4(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                agent = None

                agents[config.id] = agent
                logger.debug(f"Successfully created agent: {config.id}")
            except KeyError as e:
                logger.warning(
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_5(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    tools=None,
                    # Note: The 'model' parameter in agno.Client refers to the LLM.
                    # We use 'model_name' from our config.
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_6(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=None,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_7(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
                    # system prompt is constructed from agent personality
                    instructions=None,
                )

                agents[config.id] = agent
                logger.debug(f"Successfully created agent: {config.id}")
            except KeyError as e:
                logger.warning(
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_8(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_9(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_10(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
                    # system prompt is constructed from agent personality
                )

                agents[config.id] = agent
                logger.debug(f"Successfully created agent: {config.id}")
            except KeyError as e:
                logger.warning(
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_11(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
                    # system prompt is constructed from agent personality
                    instructions=(
                        f"You are {config.name}, a specialized AI agent. "
                        f"Your role is: {config.role}. "
                        f"Your primary goal is: {config.goal}. "
                        f"Your backstory: {config.backstory}"
                    ),
                )

                agents[config.id] = None
                logger.debug(f"Successfully created agent: {config.id}")
            except KeyError as e:
                logger.warning(
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_12(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
                    # system prompt is constructed from agent personality
                    instructions=(
                        f"You are {config.name}, a specialized AI agent. "
                        f"Your role is: {config.role}. "
                        f"Your primary goal is: {config.goal}. "
                        f"Your backstory: {config.backstory}"
                    ),
                )

                agents[config.id] = agent
                logger.debug(None)
            except KeyError as e:
                logger.warning(
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_13(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
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
            except KeyError:
                logger.warning(None)
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_14(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
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
                    f"Tool '{e.args[1]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_15(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(None, exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_16(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=None)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_17(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(exc_info=True)
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_18(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(
                    f"Failed to create agent '{config.id}'",
                )
        return agents

    async def xǁAgentManagerǁ_create_agents__mutmut_19(
        self, agent_configs: List[AgentConfig]
    ) -> Dict[str, Any]:
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
                    model=config.model_name,
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
                    f"Tool '{e.args[0]}' not found for agent '{config.id}'. Agent will be created without it."
                )
            except Exception:
                logger.error(f"Failed to create agent '{config.id}'", exc_info=False)
        return agents

    xǁAgentManagerǁ_create_agents__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAgentManagerǁ_create_agents__mutmut_1": xǁAgentManagerǁ_create_agents__mutmut_1,
        "xǁAgentManagerǁ_create_agents__mutmut_2": xǁAgentManagerǁ_create_agents__mutmut_2,
        "xǁAgentManagerǁ_create_agents__mutmut_3": xǁAgentManagerǁ_create_agents__mutmut_3,
        "xǁAgentManagerǁ_create_agents__mutmut_4": xǁAgentManagerǁ_create_agents__mutmut_4,
        "xǁAgentManagerǁ_create_agents__mutmut_5": xǁAgentManagerǁ_create_agents__mutmut_5,
        "xǁAgentManagerǁ_create_agents__mutmut_6": xǁAgentManagerǁ_create_agents__mutmut_6,
        "xǁAgentManagerǁ_create_agents__mutmut_7": xǁAgentManagerǁ_create_agents__mutmut_7,
        "xǁAgentManagerǁ_create_agents__mutmut_8": xǁAgentManagerǁ_create_agents__mutmut_8,
        "xǁAgentManagerǁ_create_agents__mutmut_9": xǁAgentManagerǁ_create_agents__mutmut_9,
        "xǁAgentManagerǁ_create_agents__mutmut_10": xǁAgentManagerǁ_create_agents__mutmut_10,
        "xǁAgentManagerǁ_create_agents__mutmut_11": xǁAgentManagerǁ_create_agents__mutmut_11,
        "xǁAgentManagerǁ_create_agents__mutmut_12": xǁAgentManagerǁ_create_agents__mutmut_12,
        "xǁAgentManagerǁ_create_agents__mutmut_13": xǁAgentManagerǁ_create_agents__mutmut_13,
        "xǁAgentManagerǁ_create_agents__mutmut_14": xǁAgentManagerǁ_create_agents__mutmut_14,
        "xǁAgentManagerǁ_create_agents__mutmut_15": xǁAgentManagerǁ_create_agents__mutmut_15,
        "xǁAgentManagerǁ_create_agents__mutmut_16": xǁAgentManagerǁ_create_agents__mutmut_16,
        "xǁAgentManagerǁ_create_agents__mutmut_17": xǁAgentManagerǁ_create_agents__mutmut_17,
        "xǁAgentManagerǁ_create_agents__mutmut_18": xǁAgentManagerǁ_create_agents__mutmut_18,
        "xǁAgentManagerǁ_create_agents__mutmut_19": xǁAgentManagerǁ_create_agents__mutmut_19,
    }

    def _create_agents(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAgentManagerǁ_create_agents__mutmut_orig"),
            object.__getattribute__(
                self, "xǁAgentManagerǁ_create_agents__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    _create_agents.__signature__ = _mutmut_signature(
        xǁAgentManagerǁ_create_agents__mutmut_orig
    )
    xǁAgentManagerǁ_create_agents__mutmut_orig.__name__ = (
        "xǁAgentManagerǁ_create_agents"
    )

    def xǁAgentManagerǁget_agent__mutmut_orig(self, agent_id: str) -> Optional[Any]:
        """Retrieves a loaded agent by its ID."""
        return self.agents.get(agent_id)

    def xǁAgentManagerǁget_agent__mutmut_1(self, agent_id: str) -> Optional[Any]:
        """Retrieves a loaded agent by its ID."""
        return self.agents.get(None)

    xǁAgentManagerǁget_agent__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAgentManagerǁget_agent__mutmut_1": xǁAgentManagerǁget_agent__mutmut_1
    }

    def get_agent(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁAgentManagerǁget_agent__mutmut_orig"),
            object.__getattribute__(self, "xǁAgentManagerǁget_agent__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    get_agent.__signature__ = _mutmut_signature(xǁAgentManagerǁget_agent__mutmut_orig)
    xǁAgentManagerǁget_agent__mutmut_orig.__name__ = "xǁAgentManagerǁget_agent"

    def get_all_agents(self) -> List[AgentConfig]:
        """Returns the configuration of all loaded agents."""
        return self.agent_configs

    def xǁAgentManagerǁget_agent_with_tool__mutmut_orig(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
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

    def xǁAgentManagerǁget_agent_with_tool__mutmut_1(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = None
        if agent is None:
            logger.warning(f"Agent '{agent_id}' not found")
            raise ValueError(f"Agent {agent_id} not found")

        if any(t.name == tool_name for t in agent.tools):
            return agent
        else:
            logger.warning(f"Tool '{tool_name}' not found for agent '{agent_id}'")
            raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")

    def xǁAgentManagerǁget_agent_with_tool__mutmut_2(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = self.get_agent(None)
        if agent is None:
            logger.warning(f"Agent '{agent_id}' not found")
            raise ValueError(f"Agent {agent_id} not found")

        if any(t.name == tool_name for t in agent.tools):
            return agent
        else:
            logger.warning(f"Tool '{tool_name}' not found for agent '{agent_id}'")
            raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")

    def xǁAgentManagerǁget_agent_with_tool__mutmut_3(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = self.get_agent(agent_id)
        if agent is not None:
            logger.warning(f"Agent '{agent_id}' not found")
            raise ValueError(f"Agent {agent_id} not found")

        if any(t.name == tool_name for t in agent.tools):
            return agent
        else:
            logger.warning(f"Tool '{tool_name}' not found for agent '{agent_id}'")
            raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")

    def xǁAgentManagerǁget_agent_with_tool__mutmut_4(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = self.get_agent(agent_id)
        if agent is None:
            logger.warning(None)
            raise ValueError(f"Agent {agent_id} not found")

        if any(t.name == tool_name for t in agent.tools):
            return agent
        else:
            logger.warning(f"Tool '{tool_name}' not found for agent '{agent_id}'")
            raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")

    def xǁAgentManagerǁget_agent_with_tool__mutmut_5(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = self.get_agent(agent_id)
        if agent is None:
            logger.warning(f"Agent '{agent_id}' not found")
            raise ValueError(None)

        if any(t.name == tool_name for t in agent.tools):
            return agent
        else:
            logger.warning(f"Tool '{tool_name}' not found for agent '{agent_id}'")
            raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")

    def xǁAgentManagerǁget_agent_with_tool__mutmut_6(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = self.get_agent(agent_id)
        if agent is None:
            logger.warning(f"Agent '{agent_id}' not found")
            raise ValueError(f"Agent {agent_id} not found")

        if any(None):
            return agent
        else:
            logger.warning(f"Tool '{tool_name}' not found for agent '{agent_id}'")
            raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")

    def xǁAgentManagerǁget_agent_with_tool__mutmut_7(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = self.get_agent(agent_id)
        if agent is None:
            logger.warning(f"Agent '{agent_id}' not found")
            raise ValueError(f"Agent {agent_id} not found")

        if any(t.name != tool_name for t in agent.tools):
            return agent
        else:
            logger.warning(f"Tool '{tool_name}' not found for agent '{agent_id}'")
            raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")

    def xǁAgentManagerǁget_agent_with_tool__mutmut_8(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = self.get_agent(agent_id)
        if agent is None:
            logger.warning(f"Agent '{agent_id}' not found")
            raise ValueError(f"Agent {agent_id} not found")

        if any(t.name == tool_name for t in agent.tools):
            return agent
        else:
            logger.warning(None)
            raise ValueError(f"Tool {tool_name} not found for agent {agent_id}")

    def xǁAgentManagerǁget_agent_with_tool__mutmut_9(
        self, agent_id: str, tool_name: str
    ) -> Optional[Any]:
        """Retrieves an agent that has the specified tool, raising ValueError if not found."""
        agent = self.get_agent(agent_id)
        if agent is None:
            logger.warning(f"Agent '{agent_id}' not found")
            raise ValueError(f"Agent {agent_id} not found")

        if any(t.name == tool_name for t in agent.tools):
            return agent
        else:
            logger.warning(f"Tool '{tool_name}' not found for agent '{agent_id}'")
            raise ValueError(None)

    xǁAgentManagerǁget_agent_with_tool__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁAgentManagerǁget_agent_with_tool__mutmut_1": xǁAgentManagerǁget_agent_with_tool__mutmut_1,
        "xǁAgentManagerǁget_agent_with_tool__mutmut_2": xǁAgentManagerǁget_agent_with_tool__mutmut_2,
        "xǁAgentManagerǁget_agent_with_tool__mutmut_3": xǁAgentManagerǁget_agent_with_tool__mutmut_3,
        "xǁAgentManagerǁget_agent_with_tool__mutmut_4": xǁAgentManagerǁget_agent_with_tool__mutmut_4,
        "xǁAgentManagerǁget_agent_with_tool__mutmut_5": xǁAgentManagerǁget_agent_with_tool__mutmut_5,
        "xǁAgentManagerǁget_agent_with_tool__mutmut_6": xǁAgentManagerǁget_agent_with_tool__mutmut_6,
        "xǁAgentManagerǁget_agent_with_tool__mutmut_7": xǁAgentManagerǁget_agent_with_tool__mutmut_7,
        "xǁAgentManagerǁget_agent_with_tool__mutmut_8": xǁAgentManagerǁget_agent_with_tool__mutmut_8,
        "xǁAgentManagerǁget_agent_with_tool__mutmut_9": xǁAgentManagerǁget_agent_with_tool__mutmut_9,
    }

    def get_agent_with_tool(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁAgentManagerǁget_agent_with_tool__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁAgentManagerǁget_agent_with_tool__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    get_agent_with_tool.__signature__ = _mutmut_signature(
        xǁAgentManagerǁget_agent_with_tool__mutmut_orig
    )
    xǁAgentManagerǁget_agent_with_tool__mutmut_orig.__name__ = (
        "xǁAgentManagerǁget_agent_with_tool"
    )


# --- Singleton Instance ---
# Create a single, globally accessible instance of the AgentManager.
agent_manager = AgentManager()
