#!/usr/bin/env python3
"""
Tests for the refactored AgentManager to ensure it correctly handles
dependency injection. The original test for the async lock is now obsolete
as the lazy-loading mechanism has been removed in favor of DI.
"""

from unittest.mock import MagicMock

from resync.core.agent_manager import AgentManager
from resync.core.interfaces import ITWSClient
from resync.tool_definitions.tws_tools import TWSToolReadOnly


def test_agent_manager_dependency_injection():
    """
    Test that AgentManager correctly accepts and configures its dependencies
    via its constructor, following the new dependency injection pattern.
    """
    # Arrange: Create a mock dependency for the TWS client.
    # Using a spec ensures the mock behaves like the actual interface.
    mock_tws_client = MagicMock(spec=ITWSClient)

    # Act: Instantiate AgentManager with the mock dependency.
    agent_manager = AgentManager(tws_client=mock_tws_client)

    # Assert:
    # 1. The dependency is stored correctly on the instance.
    assert agent_manager.tws_client is mock_tws_client, \
        "AgentManager should store the provided tws_client instance."

    # 2. The tools managed by AgentManager are configured with the dependency.
    # We check one of the tools that we know requires the TWS client.
    status_tool = agent_manager.tools.get("tws_status_tool")
    assert isinstance(status_tool, TWSToolReadOnly), \
        "The TWS status tool should be a TWSToolReadOnly instance."
    assert status_tool.tws_client is mock_tws_client, \
        "The TWS client should be injected into the TWS tools."

    print("\n✅ AgentManager dependency injection test passed!")
    print("✅ AgentManager correctly accepts and configures dependencies.")