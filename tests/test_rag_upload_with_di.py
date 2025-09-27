"""
Tests for RAG upload endpoints using dependency injection.
"""

import io
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from resync.core.exceptions import FileProcessingError
from resync.core.interfaces import IFileIngestor


def test_upload_document_success(
    test_client: TestClient,
    mock_file_ingestor: MagicMock,
    app_with_di_container: FastAPI,
):
    """Test successful document upload."""
    # Setup mock file ingestor
    mock_file_ingestor.save_uploaded_file = AsyncMock()
    mock_file_ingestor.save_uploaded_file.return_value = Path("/path/to/test-file.pdf")
    mock_file_ingestor.ingest_file = AsyncMock()
    
    # Create a test file
    test_file = io.BytesIO(b"test file content")
    
    # Call the endpoint
    response = test_client.post(
        "/api/rag/upload",
        files={"file": ("test-file.pdf", test_file, "application/pdf")},
    )
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test-file.pdf"
    assert data["content_type"] == "application/pdf"
    assert "uploaded successfully" in data["message"]
    
    # Verify the mocks were called correctly
    mock_file_ingestor.save_uploaded_file.assert_called_once()
    # We don't assert on ingest_file because it's called in a background task


def test_upload_document_invalid_filename(
    test_client: TestClient,
    mock_file_ingestor: MagicMock,
    app_with_di_container: FastAPI,
):
    """Test document upload with invalid filename."""
    # Setup mock file ingestor to raise an error
    mock_file_ingestor.save_uploaded_file = AsyncMock()
    mock_file_ingestor.save_uploaded_file.side_effect = FileProcessingError("Invalid filename.")
    
    # Create a test file
    test_file = io.BytesIO(b"test file content")
    
    # Call the endpoint
    response = test_client.post(
        "/api/rag/upload",
        files={"file": ("../../../etc/passwd", test_file, "text/plain")},
    )
    
    # Verify the response
    assert response.status_code == 400
    data = response.json()
    assert "Invalid filename" in data["detail"]
    
    # Verify the mock was called
    mock_file_ingestor.save_uploaded_file.assert_called_once()


def test_upload_document_server_error(
    test_client: TestClient,
    mock_file_ingestor: MagicMock,
    app_with_di_container: FastAPI,
):
    """Test document upload with server error."""
    # Setup mock file ingestor to raise an unexpected error
    mock_file_ingestor.save_uploaded_file = AsyncMock()
    mock_file_ingestor.save_uploaded_file.side_effect = Exception("Disk full")
    
    # Create a test file
    test_file = io.BytesIO(b"test file content")
    
    # Call the endpoint
    response = test_client.post(
        "/api/rag/upload",
        files={"file": ("test-file.pdf", test_file, "application/pdf")},
    )
    
    # Verify the response
    assert response.status_code == 500
    data = response.json()
    assert "Could not process file" in data["detail"]
    
    # Verify the mock was called
    mock_file_ingestor.save_uploaded_file.assert_called_once()
