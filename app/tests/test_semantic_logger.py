from unittest.mock import MagicMock, mock_open, patch

import pytest

from app.services.semantic_logger import SemanticLogger


@pytest.fixture
def mock_embedding_model(monkeypatch: pytest.MonkeyPatch):
    """Mocks the SentenceTransformer model."""
    mock_model = MagicMock()
    mock_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
    monkeypatch.setattr(
        "app.services.semantic_logger.SentenceTransformer",
        lambda *args, **kwargs: mock_model
    )
    return mock_model

@pytest.fixture
def mock_kg_manager(monkeypatch: pytest.MonkeyPatch):
    """Mocks the KnowledgeGraphManager."""
    mock_instance = MagicMock()
    monkeypatch.setattr(
        "app.services.semantic_logger.KnowledgeGraphManager",
        lambda *args, **kwargs: mock_instance
    )
    return mock_instance

@pytest.mark.asyncio
async def test_log_interaction_flow(mock_embedding_model, mock_kg_manager):
    """
    Tests the main log_interaction flow, ensuring all sub-methods are called.
    """
    interaction_data = {
        "user_query": "status do job JOB_TEST",
        "agent_response": "O job JOB_TEST concluiu com sucesso.",
        "session_id": "session123",
        "entities": [{"type": "job_name", "value": "JOB_TEST"}],
        "intent": "get_job_status"
    }

    # Use mock_open to prevent actual file writes
    with patch("builtins.open", mock_open()) as mock_file:
        with patch("pathlib.Path.mkdir", MagicMock()):
            logger = SemanticLogger()
            await logger.log_interaction(interaction_data)

            # Assert that the KG manager was updated
            mock_kg_manager.update_from_interaction.assert_called_once()

            # Assert that the fine-tuning data was prepared and saved
            mock_file.assert_called()
            # The log should be written twice: once for conversation, once for fine-tuning
            assert mock_file.call_count == 2


def test_build_semantic_entry(mock_embedding_model):
    """
    Tests the construction of the rich semantic log entry.
    """
    interaction_data = {
        "user_query": "test query",
        "agent_response": "test response",
        "classified_intent": "test_intent",
        "entities": ["test_entity"],
    }

    logger = SemanticLogger()
    # Manually set the KG manager to avoid file system operations in this unit test
    logger.kg_manager = MagicMock()

    entry = logger._build_semantic_entry(interaction_data)

    assert entry["user_input"]["raw_query"] == "test query"
    assert entry["user_input"]["intent"] == "test_intent"
    assert entry["user_input"]["embedding"] == [0.1, 0.2, 0.3]
    assert entry["response"]["generated_text"] == "test response"
