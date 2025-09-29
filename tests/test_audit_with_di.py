"""
Tests for audit endpoints using dependency injection.
"""

from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_get_flagged_memories_with_di(
    test_client: TestClient,
    mock_audit_queue: MagicMock,
    app_with_di_container: FastAPI,
):
    """Test the get_flagged_memories endpoint with dependency injection."""
    # Setup mock audit queue response
    mock_audit_queue.get_audits_by_status_sync.return_value = [
        {
            "memory_id": "test-id-1",
            "user_query": "What is the status?",
            "agent_response": "The status is good.",
            "status": "pending",
            "timestamp": "2023-01-01T00:00:00Z",
        },
        {
            "memory_id": "test-id-2",
            "user_query": "Another question",
            "agent_response": "Another response",
            "status": "pending",
            "timestamp": "2023-01-02T00:00:00Z",
        },
    ]

    # Call the endpoint
    response = test_client.get("/api/audit/flags")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["memory_id"] == "test-id-1"
    assert data[1]["memory_id"] == "test-id-2"

    # Verify the mock was called correctly
    mock_audit_queue.get_audits_by_status_sync.assert_called_once_with("pending")


def test_get_flagged_memories_with_query_filter(
    test_client: TestClient,
    mock_audit_queue: MagicMock,
    app_with_di_container: FastAPI,
):
    """Test the get_flagged_memories endpoint with query filter."""
    # Setup mock audit queue response
    mock_audit_queue.get_audits_by_status_sync.return_value = [
        {
            "memory_id": "test-id-1",
            "user_query": "What is the status?",
            "agent_response": "The status is good.",
            "status": "pending",
            "timestamp": "2023-01-01T00:00:00Z",
        },
        {
            "memory_id": "test-id-2",
            "user_query": "Another question",
            "agent_response": "Another response",
            "status": "pending",
            "timestamp": "2023-01-02T00:00:00Z",
        },
    ]

    # Call the endpoint with query filter
    response = test_client.get("/api/audit/flags?query=status")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["memory_id"] == "test-id-1"

    # Verify the mock was called correctly
    mock_audit_queue.get_audits_by_status_sync.assert_called_once_with("pending")


def test_review_memory_approve(
    test_client: TestClient,
    mock_audit_queue: MagicMock,
    mock_knowledge_graph: MagicMock,
    app_with_di_container: FastAPI,
):
    """Test the review_memory endpoint for approving a memory."""
    # Setup mocks
    mock_audit_queue.update_audit_status_sync.return_value = True
    mock_knowledge_graph.client = MagicMock()
    mock_knowledge_graph.client.add_observations = AsyncMock()

    # Call the endpoint
    response = test_client.post(
        "/api/audit/review",
        json={"memory_id": "test-id", "action": "approve"},
    )

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"
    assert data["memory_id"] == "test-id"

    # Verify the mocks were called correctly
    mock_audit_queue.update_audit_status_sync.assert_called_once_with(
        "test-id", "approved"
    )
    mock_knowledge_graph.client.add_observations.assert_called_once_with(
        "test-id", ["MANUALLY_APPROVED_BY_ADMIN"]
    )


def test_review_memory_reject(
    test_client: TestClient,
    mock_audit_queue: MagicMock,
    mock_knowledge_graph: MagicMock,
    app_with_di_container: FastAPI,
):
    """Test the review_memory endpoint for rejecting a memory."""
    # Setup mocks
    mock_audit_queue.update_audit_status_sync.return_value = True
    mock_knowledge_graph.client = MagicMock()
    mock_knowledge_graph.client.delete = AsyncMock()

    # Call the endpoint
    response = test_client.post(
        "/api/audit/review",
        json={"memory_id": "test-id", "action": "reject"},
    )

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"
    assert data["memory_id"] == "test-id"

    # Verify the mocks were called correctly
    mock_audit_queue.update_audit_status_sync.assert_called_once_with(
        "test-id", "rejected"
    )
    mock_knowledge_graph.client.delete.assert_called_once_with("test-id")


def test_get_audit_metrics(
    test_client: TestClient,
    mock_audit_queue: MagicMock,
    app_with_di_container: FastAPI,
):
    """Test the get_audit_metrics endpoint."""
    # Setup mock response
    mock_audit_queue.get_audit_metrics_sync.return_value = {
        "pending": 5,
        "approved": 10,
        "rejected": 2,
        "total": 17,
    }

    # Call the endpoint
    response = test_client.get("/api/audit/metrics")

    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["pending"] == 5
    assert data["approved"] == 10
    assert data["rejected"] == 2
    assert data["total"] == 17

    # Verify the mock was called correctly
    mock_audit_queue.get_audit_metrics_sync.assert_called_once()
