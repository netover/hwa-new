from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from resync.models.tws import SystemStatus
from resync.services.tws_service import OptimizedTWSClient
from resync.tool_definitions.tws_tools import (
    TWSStatusTool,
    TWSTroubleshootingTool,
)


@pytest.fixture
def mock_tws_client() -> MagicMock:
    """Creates a mock of the OptimizedTWSClient for testing."""
    client = MagicMock(spec=OptimizedTWSClient)
    client.get_system_status = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_tws_status_tool_success(mock_tws_client):
    """
    Tests the TWSStatusTool's success path, ensuring it correctly formats data.
    """
    # Arrange: Set up the mock client to return predefined data
    mock_status = SystemStatus(
        workstations=[
            {"name": "CPU1", "status": "LINKED", "type": "FTA"},
            {"name": "CPU2", "status": "DOWN", "type": "FTA"},
        ],
        jobs=[
            {
                "name": "JOB1",
                "workstation": "CPU1",
                "status": "SUCC",
                "job_stream": "JS1",
            },
            {
                "name": "JOB2",
                "workstation": "CPU2",
                "status": "ABEND",
                "job_stream": "JS2",
            },
        ],
        critical_jobs=[],
    )
    mock_tws_client.get_system_status.return_value = mock_status

    tool = TWSStatusTool(tws_client=mock_tws_client)

    # Act: Execute the tool's method
    result = await tool.get_tws_status()

    # Assert: Verify the output is correctly formatted
    assert "Situação atual do TWS:" in result
    assert "CPU1 (LINKED)" in result
    assert "CPU2 (DOWN)" in result
    assert "JOB1 on CPU1 (SUCC)" in result
    assert "JOB2 on CPU2 (ABEND)" in result
    mock_tws_client.get_system_status.assert_awaited_once()


@pytest.mark.asyncio
async def test_tws_troubleshooting_tool_finds_failures(mock_tws_client):
    """
    Tests the TWSTroubleshootingTool's ability to identify and report failures.
    """
    # Arrange
    mock_status = SystemStatus(
        workstations=[
            {"name": "CPU1", "status": "LINKED", "type": "FTA"},
            {"name": "CPU2", "status": "DOWN", "type": "FTA"},
        ],
        jobs=[
            {
                "name": "JOB1",
                "workstation": "CPU1",
                "status": "SUCC",
                "job_stream": "JS1",
            },
            {
                "name": "JOB2",
                "workstation": "CPU2",
                "status": "ABEND",
                "job_stream": "JS2",
            },
        ],
        critical_jobs=[],
    )
    mock_tws_client.get_system_status.return_value = mock_status

    tool = TWSTroubleshootingTool(tws_client=mock_tws_client)

    # Act
    result = await tool.analyze_failures()

    # Assert
    assert "Análise de Problemas no TWS:" in result
    assert "Jobs com Falha (1): JOB2 (workstation: CPU2)" in result
    assert "Workstations com Problemas (1): CPU2 (status: DOWN)" in result
    mock_tws_client.get_system_status.assert_awaited_once()


@pytest.mark.asyncio
async def test_tws_troubleshooting_tool_no_failures(mock_tws_client):
    """
    Tests the TWSTroubleshootingTool's behavior when no failures are present.
    """
    # Arrange
    mock_status = SystemStatus(
        workstations=[{"name": "CPU1", "status": "LINKED", "type": "FTA"}],
        jobs=[
            {
                "name": "JOB1",
                "workstation": "CPU1",
                "status": "SUCC",
                "job_stream": "JS1",
            }
        ],
        critical_jobs=[],
    )
    mock_tws_client.get_system_status.return_value = mock_status

    tool = TWSTroubleshootingTool(tws_client=mock_tws_client)

    # Act
    result = await tool.analyze_failures()

    # Assert
    assert "Nenhuma falha crítica encontrada. O ambiente TWS parece estável." in result
    mock_tws_client.get_system_status.assert_awaited_once()


@pytest.mark.asyncio
async def test_tool_handles_client_exception(mock_tws_client):
    """
    Tests that tools gracefully handle exceptions from the TWS client.
    """
    # Arrange
    mock_tws_client.get_system_status.side_effect = Exception("Connection Refused")

    status_tool = TWSStatusTool(tws_client=mock_tws_client)
    trouble_tool = TWSTroubleshootingTool(tws_client=mock_tws_client)

    # Act
    status_result = await status_tool.get_tws_status()
    trouble_result = await trouble_tool.analyze_failures()

    # Assert
    assert "Erro ao obter o status do TWS: Connection Refused" in status_result
    assert "Erro ao analisar as falhas do TWS: Connection Refused" in trouble_result
