from unittest.mock import AsyncMock, MagicMock

import pytest

from resync.api.chat import _handle_agent_interaction
from resync.core.fastapi_di import (
    get_agent_manager,
    get_connection_manager,
    get_knowledge_graph,
)
from resync.main import app

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_chat_dependencies():
    """Overrides the main dependencies for chat endpoints for isolated testing."""
    mock_agent_mgr = AsyncMock()
    mock_conn_mgr = AsyncMock()
    mock_kg = AsyncMock()

    with app.dependency_overrides.items() as overrides:
        overrides[get_agent_manager] = lambda: mock_agent_mgr
        overrides[get_connection_manager] = lambda: mock_conn_mgr
        overrides[get_knowledge_graph] = lambda: mock_kg
        yield {
            "agent_manager": mock_agent_mgr,
            "connection_manager": mock_conn_mgr,
            "knowledge_graph": mock_kg,
        }


async def test_handle_agent_interaction_mocks_async_iterator(mock_chat_dependencies):
    """
    Verifies that _handle_agent_interaction correctly processes chunks
    from a mocked async iterator (agent.stream).
    """
    # 1. Arrange
    mock_websocket = AsyncMock()
    mock_agent = MagicMock()
    mock_kg = mock_chat_dependencies["knowledge_graph"]

    # This is the key part: Mocking the async iterator.
    # We create a list of chunks to be "streamed".
    stream_chunks = ["Hello", ", ", "world", "!"]
    # We configure the mock's __aiter__ method to return an async iterator
    # that yields our chunks.
    mock_agent.stream = AsyncMock()
    mock_agent.stream.return_value.__aiter__.return_value = stream_chunks

    # 2. Act
    await _handle_agent_interaction(
        websocket=mock_websocket,
        agent=mock_agent,
        agent_id="test-agent",
        knowledge_graph=mock_kg,
        data="user message",
    )

    # 3. Assert
    # Check that the stream method was called.
    mock_agent.stream.assert_called_once()

    # Check that send_json was called for each chunk in the stream.
    stream_calls = [
        call for call in mock_websocket.send_json.call_args_list if call.args[0]["type"] == "stream"
    ]
    assert len(stream_calls) == len(stream_chunks)
    assert stream_calls[0].args[0]["message"] == "Hello"
    assert stream_calls[3].args[0]["message"] == "!"

    # Verify the final message was sent correctly.
    final_call = mock_websocket.send_json.call_args_list[-1]
    assert final_call.args[0]["type"] == "message"
    assert final_call.args[0]["is_final"] is True
    assert final_call.args[0]["message"] == "Hello, world!"
