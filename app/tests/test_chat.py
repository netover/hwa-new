from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Importa a instância 'app' do __main__ para o TestClient
from app.__main__ import app


# Fixture para gerenciar o ciclo de vida da aplicação nos testes
@pytest.fixture(scope="module", autouse=True)
def app_lifespan_manager():
    """
    Gerencia os eventos de startup e shutdown da aplicação FastAPI para os testes.
    """
    with TestClient(app):
        yield

client = TestClient(app)

# Patching the method on the class where it's defined is more robust
@patch("app.services.semantic_logger.SemanticLogger.log_interaction", new_callable=AsyncMock)
def test_chat_endpoint_triggers_semantic_logging(mock_log_interaction):
    """
    Verifica se uma chamada ao endpoint /api/chat aciona o SemanticLogger.
    """
    # Mock para o dispatcher do agente para não depender de uma chamada real à IA
    # Patching the Agent class's run method is the most robust way
    with patch("agno.agent.Agent.run", new_callable=AsyncMock) as mock_agent_run:
        mock_agent_run.return_value = {
            "reply": "Esta é uma resposta mock.",
            "sources": [],
            "agent_route": "dispatcher",
        }

        # Faz a requisição para a API
        response = client.post(
            "/api/chat",
            json={"message": "Olá, mundo!", "session_id": "test_session_123"},
        )

        # 1. Verifica se a resposta da API foi bem-sucedida
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["reply"] == "Esta é uma resposta mock."

        # 2. Verifica se o logger semântico foi chamado.
        # A chamada é feita em uma task de background. Em um teste real,
        # pode ser necessário um pequeno `await asyncio.sleep(0)` para
        # dar ao event loop a chance de executar a task.
        # No entanto, o mock deve registrar a chamada imediatamente após
        # a criação da task.
        mock_log_interaction.assert_called_once()

        # 3. Verifica se os dados corretos foram passados para o logger
        call_args, _ = mock_log_interaction.call_args
        interaction_data = call_args[0]

        assert interaction_data["user_query"] == "Olá, mundo!"
        assert interaction_data["session_id"] == "test_session_123"
        assert interaction_data["agent_response"] == "Esta é uma resposta mock."
        assert interaction_data["classified_intent"] == "unknown"
        assert interaction_data["entities"] == []
