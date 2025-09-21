from pathlib import Path

import pandas as pd
import pytest

from app.services.knowledge_service import KnowledgeBaseService


@pytest.fixture
def mock_kb_data() -> pd.DataFrame:
    """Provides a sample knowledge base DataFrame."""
    data = {
        "job_name": ["JOB_A01_FAIL", "JOB_B02_RECOVER", "JOB_C03_SUCCESS"],
        "solution": ["Check database connection", "Restart the service", "No action needed"],
        "owner": ["DB Team", "App Team", "Ops Team"],
        "error_code": ["DB-500", "SVC-101", None]
    }
    return pd.DataFrame(data)


def test_load_kb_file_not_found() -> None:
    """
    Tests that the service handles a non-existent KB file gracefully.
    """
    kb_service = KnowledgeBaseService("non_existent_file.xlsx")
    kb_service.load_kb()
    assert kb_service.kb_df is not None
    assert kb_service.kb_df.empty


def test_load_kb_success(monkeypatch: pytest.MonkeyPatch, mock_kb_data: pd.DataFrame) -> None:
    """
    Tests successful loading and column normalization of the KB file.
    """
    # Mock pandas read_excel to return our sample data
    monkeypatch.setattr(pd, "read_excel", lambda *args, **kwargs: mock_kb_data)

    kb_service = KnowledgeBaseService("dummy_path.xlsx")
    # Mock Path.is_file to return True so it attempts to load
    monkeypatch.setattr(Path, "is_file", lambda self: True)

    kb_service.load_kb()

    assert kb_service.kb_df is not None
    assert not kb_service.kb_df.empty
    # Check if a column was correctly normalized
    assert "job_name" in kb_service.kb_df.columns


def test_search_for_solution_found(monkeypatch: pytest.MonkeyPatch, mock_kb_data: pd.DataFrame) -> None:
    """
    Tests that a solution is found for a job that exists in the KB (case-insensitive).
    """
    monkeypatch.setattr(pd, "read_excel", lambda *args, **kwargs: mock_kb_data)
    kb_service = KnowledgeBaseService("dummy_path.xlsx")
    monkeypatch.setattr(Path, "is_file", lambda self: True)
    kb_service.load_kb()

    solution = kb_service.search_for_solution("job_a01_fail") # Search with lowercase
    assert solution is not None
    assert solution["owner"] == "DB Team"
    assert solution["solution"] == "Check database connection"


def test_search_for_solution_not_found(monkeypatch: pytest.MonkeyPatch, mock_kb_data: pd.DataFrame) -> None:
    """
    Tests that None is returned for a job that does not exist in the KB.
    """
    monkeypatch.setattr(pd, "read_excel", lambda *args, **kwargs: mock_kb_data)
    kb_service = KnowledgeBaseService("dummy_path.xlsx")
    monkeypatch.setattr(Path, "is_file", lambda self: True)
    kb_service.load_kb()

    solution = kb_service.search_for_solution("NON_EXISTENT_JOB")
    assert solution is None
