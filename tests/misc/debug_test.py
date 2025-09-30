#!/usr/bin/env python3
"""Debug script to test the integration test."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import WebSocket

from resync.api.chat import websocket_endpoint
from resync.core.agent_manager import AgentManager


async def debug_integration_test():
    """Debug the integration test step by step."""
    print("Starting debug integration test...")

    # Create mock agent manager
    AgentManager._instance = None
    AgentManager._initialized = False

    agent_manager = AgentManager()

    # Mock the agent
    mock_agent = MagicMock()

    async def mock_stream(enhanced_query):
        print(f"Agent stream called with: {enhanced_query[:100]}...")
        response_text = "Test response from agent"
        for chunk in response_text.split():
            yield chunk + " "

    mock_agent.stream = mock_stream

    # Add mock agent to manager
    agent_manager.agents["test-agent"] = mock_agent
    agent_manager.agent_configs = [MagicMock(id="test-agent", name="Test Agent")]

    # Mock TWS client
    mock_tws_client = AsyncMock()
    mock_tws_client.check_connection.return_value = True
    mock_tws_client.get_system_status.return_value = MagicMock(
        workstations=[
            MagicMock(name="CPU_WS", status="LINKED", type="CPU"),
            MagicMock(name="FT_WS", status="LINKED", type="FT"),
        ],
        jobs=[
            MagicMock(name="JOB_A", workstation="CPU_WS", status="SUCC"),
            MagicMock(name="JOB_B", workstation="FT_WS", status="ABEND"),
        ],
        critical_jobs=[
            MagicMock(name="CRITICAL_JOB_1", workstation="CPU_WS", status="SUCC")
        ],
    )

    # Mock LLM call
    async def mock_call_llm(
        prompt,
        model,
        max_tokens=200,
        temperature=0.1,
        max_retries=3,
        initial_backoff=1.0,
    ):
        print(f"LLM called with prompt: {prompt[:100]}...")
        if "permission denied" in prompt.lower():
            return '{"is_incorrect": true, "confidence": 0.90, "reason": "Incorrect chmod command suggestion"}'
        elif "restart" in prompt.lower():
            return '{"is_incorrect": false, "confidence": 0.95, "reason": "Correct restart procedure"}'
        else:
            return '{"is_incorrect": false, "confidence": 0.85, "reason": "General response acceptable"}'

    # Mock knowledge graph
    mock_knowledge_graph = AsyncMock()
    mock_knowledge_graph.get_relevant_context.return_value = (
        "Previous context about job troubleshooting"
    )
    mock_knowledge_graph.add_conversation.return_value = "mock_memory_id_123"

    # Mock audit queue
    mock_audit_queue = AsyncMock()
    mock_audit_queue.is_memory_approved.return_value = False
    mock_audit_queue.add_audit_record = AsyncMock()

    # Mock connection manager
    mock_connection_manager = AsyncMock()
    mock_connection_manager.connect = AsyncMock()
    mock_connection_manager.disconnect = AsyncMock()
    mock_connection_manager.broadcast_json = AsyncMock()

    # Create mock WebSocket
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.accept = AsyncMock()

    # Make receive_text return one message then raise disconnect
    call_count = 0

    async def mock_receive_text():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return "How do I restart a job in TWS?"
        else:
            # Simulate WebSocket disconnect after first message
            from fastapi import WebSocketDisconnect

            raise WebSocketDisconnect(code=1000, reason="Client disconnected")

    mock_websocket.receive_text = mock_receive_text
    mock_websocket.send_json = AsyncMock()
    mock_websocket.send_text = AsyncMock()
    mock_websocket.close = AsyncMock()
    mock_websocket.client = "test_client"

    print("All mocks created successfully!")

    # Test the websocket endpoint with patches
    with (
        patch("resync.api.chat.agent_manager", agent_manager),
        patch(
            "resync.core.agent_manager.OptimizedTWSClient",
            return_value=mock_tws_client,
        ),
        patch("resync.core.ia_auditor.call_llm", mock_call_llm),
        patch("resync.core.ia_auditor.knowledge_graph", mock_knowledge_graph),
        patch("resync.core.ia_auditor.audit_queue", mock_audit_queue),
        patch("resync.api.chat.knowledge_graph", mock_knowledge_graph),
        patch("resync.api.chat.connection_manager", mock_connection_manager),
    ):
        print("Running websocket endpoint...")
        try:
            await websocket_endpoint(mock_websocket, "test-agent")
            print("WebSocket endpoint completed successfully!")
        except Exception as e:
            print(f"WebSocket endpoint failed: {e}")
            import traceback

            traceback.print_exc()

    print("Debug test completed!")


if __name__ == "__main__":
    asyncio.run(debug_integration_test())
