import pytest

from app.services.semantic_extractor import SemanticExtractor


@pytest.fixture
def extractor() -> SemanticExtractor:
    """Provides a SemanticExtractor instance."""
    return SemanticExtractor()

def test_extract_intent_job_status(extractor: SemanticExtractor):
    query = "qual a situação do job XPTO_123?"
    intent = extractor.extract_intent(query)
    assert intent == "get_job_status"

def test_extract_intent_unknown(extractor: SemanticExtractor):
    query = "fale sobre o tempo hoje"
    intent = extractor.extract_intent(query)
    assert intent == "unknown"

def test_extract_entities_job_name(extractor: SemanticExtractor):
    query = "me mostra o job JOB_FINAL_BATCH"
    entities = extractor.extract_entities(query)
    assert len(entities) == 1
    assert entities[0]["type"] == "job_name"
    assert entities[0]["value"] == "JOB_FINAL_BATCH"

def test_extract_entities_multiple(extractor: SemanticExtractor):
    query = "ver o log do JOB_A em 10/10/2025 e também do BATCH_PROCESS"
    entities = extractor.extract_entities(query)
    assert len(entities) == 3
    assert {"type": "job_name", "value": "JOB_A"} in entities
    assert {"type": "job_name", "value": "BATCH_PROCESS"} in entities
    assert {"type": "date", "value": "10/10/2025"} in entities

def test_extract_entities_none(extractor: SemanticExtractor):
    query = "olá, como vai você?"
    entities = extractor.extract_entities(query)
    assert len(entities) == 0
