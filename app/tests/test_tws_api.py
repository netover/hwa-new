import pytest
from unittest.mock import MagicMock
from app.tools.tws_tool_readonly import TWSToolReadOnly


@pytest.fixture
def tws_tool(monkeypatch: pytest.MonkeyPatch) -> TWSToolReadOnly:
    """Fixture to provide a TWSToolReadOnly instance in mock mode."""
    # Garante que o modo mock esteja ativado para os testes
    monkeypatch.setattr("app.tools.tws_tool_readonly.settings.TWS_MOCK_MODE", True)
    return TWSToolReadOnly()


@pytest.mark.asyncio
async def test_tws_tool_blocks_write_operations(tws_tool: TWSToolReadOnly) -> None:
    """
    Verifica se a ferramenta bloqueia corretamente operações de escrita perigosas.
    """
    blocked_ops = ["submit_job", "cancel_job", "delete_jobstream", "run_command"]
    for op in blocked_ops:
        result = await tws_tool.run(op)
        assert "error" in result
        assert result["error"] == "OPERAÇÃO BLOQUEADA"


@pytest.mark.asyncio
async def test_tws_tool_get_job_status(tws_tool: TWSToolReadOnly) -> None:
    """Testa a operação mock 'get_job_status'."""
    result = await tws_tool.run("get_job_status")
    assert "jobs_found" in result
    assert result["jobs_found"] == 2
    assert len(result["jobs"]) == 2
    assert result["jobs"][0]["status"] == "SUCC"


@pytest.mark.asyncio
async def test_tws_tool_get_system_status(tws_tool: TWSToolReadOnly) -> None:
    """Testa a operação mock 'get_system_status'."""
    result = await tws_tool.run("get_system_status")
    assert "status" in result
    assert result["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_tws_tool_get_engine_status(tws_tool: TWSToolReadOnly) -> None:
    """Testa a operação mock 'get_engine_status'."""
    result = await tws_tool.run("get_engine_status")
    assert "engines" in result
    assert len(result["engines"]) == 2
    assert result["engines"][0]["type"] == "master"


@pytest.mark.asyncio
async def test_tws_tool_unhandled_mock_operation(tws_tool: TWSToolReadOnly) -> None:
    """
    Testa como a ferramenta lida com uma operação de leitura válida mas
    que não tem uma resposta mock específica.
    """
    result = await tws_tool.run("get_job_history", job_id=123)
    assert result["mock"] is True
    assert result["operation"] == "get_job_history"
    assert result["args"]["job_id"] == 123
