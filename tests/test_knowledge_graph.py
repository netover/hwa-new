"""Tests for resync.core.knowledge_graph module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, mock_open
from pathlib import Path
import json
import tempfile

from resync.core.knowledge_graph import (
    AsyncKnowledgeGraph,
    create_knowledge_graph
)


class TestAsyncKnowledgeGraph:
    """Test AsyncKnowledgeGraph class."""

    @pytest.fixture
    def kg(self):
        """Create a fresh AsyncKnowledgeGraph instance."""
        return AsyncKnowledgeGraph()

    def test_initialization(self, kg):
        """Test AsyncKnowledgeGraph initialization."""
        assert kg.documents == {}
        assert kg.embeddings == {}
        assert hasattr(kg, 'embedding_model')

    @pytest.mark.asyncio
    async def test_add_document(self, kg):
        """Test adding a document to the knowledge graph."""
        doc_id = "test_doc_1"
        content = "This is a test document about artificial intelligence."
        metadata = {"source": "test", "type": "text"}
        
        await kg.add_document(doc_id, content, metadata)
        
        assert doc_id in kg.documents
        assert kg.documents[doc_id]["content"] == content
        assert kg.documents[doc_id]["metadata"] == metadata

    @pytest.mark.asyncio
    async def test_add_document_with_default_metadata(self, kg):
        """Test adding a document with default metadata."""
        doc_id = "test_doc_2"
        content = "Another test document."
        
        await kg.add_document(doc_id, content)
        
        assert doc_id in kg.documents
        assert kg.documents[doc_id]["metadata"] == {}

    @pytest.mark.asyncio
    async def test_add_document_overwrites_existing(self, kg):
        """Test that adding a document overwrites existing one."""
        doc_id = "test_doc_3"
        original_content = "Original content"
        new_content = "New content"
        
        await kg.add_document(doc_id, original_content)
        await kg.add_document(doc_id, new_content)
        
        assert kg.documents[doc_id]["content"] == new_content

    @pytest.mark.asyncio
    async def test_remove_document(self, kg):
        """Test removing a document from the knowledge graph."""
        doc_id = "test_doc_4"
        content = "Document to be removed"
        
        # Add document first
        await kg.add_document(doc_id, content)
        assert doc_id in kg.documents
        
        # Remove document
        await kg.remove_document(doc_id)
        assert doc_id not in kg.documents

    @pytest.mark.asyncio
    async def test_remove_document_also_removes_embeddings(self, kg):
        """Test that removing a document also removes its embeddings."""
        doc_id = "test_doc_5"
        content = "Document with embeddings"
        
        # Add document and simulate embeddings
        await kg.add_document(doc_id, content)
        kg.embeddings[doc_id] = [0.1, 0.2, 0.3]  # Mock embedding
        
        # Remove document
        await kg.remove_document(doc_id)
        
        assert doc_id not in kg.documents
        assert doc_id not in kg.embeddings

    @pytest.mark.asyncio
    async def test_remove_nonexistent_document(self, kg):
        """Test removing a document that doesn't exist."""
        # Should not raise an error
        await kg.remove_document("nonexistent_doc")

    @pytest.mark.asyncio
    async def test_get_document(self, kg):
        """Test retrieving a document from the knowledge graph."""
        doc_id = "test_doc_6"
        content = "Document to retrieve"
        metadata = {"author": "test"}
        
        await kg.add_document(doc_id, content, metadata)
        
        retrieved = await kg.get_document(doc_id)
        assert retrieved["content"] == content
        assert retrieved["metadata"] == metadata

    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self, kg):
        """Test retrieving a document that doesn't exist."""
        result = await kg.get_document("nonexistent_doc")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_documents(self, kg):
        """Test listing all documents in the knowledge graph."""
        # Add multiple documents
        docs = [
            ("doc1", "Content 1", {"type": "text"}),
            ("doc2", "Content 2", {"type": "pdf"}),
            ("doc3", "Content 3", {}),
        ]
        
        for doc_id, content, metadata in docs:
            await kg.add_document(doc_id, content, metadata)
        
        document_list = await kg.list_documents()
        
        assert len(document_list) == 3
        doc_ids = [doc["id"] for doc in document_list]
        assert "doc1" in doc_ids
        assert "doc2" in doc_ids
        assert "doc3" in doc_ids

    @pytest.mark.asyncio
    async def test_list_documents_empty(self, kg):
        """Test listing documents when knowledge graph is empty."""
        document_list = await kg.list_documents()
        assert document_list == []

    @pytest.mark.asyncio
    async def test_search_documents_by_metadata(self, kg):
        """Test searching documents by metadata."""
        # Add documents with different metadata
        await kg.add_document("doc1", "Content 1", {"type": "pdf", "author": "alice"})
        await kg.add_document("doc2", "Content 2", {"type": "text", "author": "bob"})
        await kg.add_document("doc3", "Content 3", {"type": "pdf", "author": "charlie"})
        
        # Search by type
        pdf_docs = await kg.search_documents(metadata_filter={"type": "pdf"})
        assert len(pdf_docs) == 2
        
        # Search by author
        alice_docs = await kg.search_documents(metadata_filter={"author": "alice"})
        assert len(alice_docs) == 1
        assert alice_docs[0]["id"] == "doc1"

    @pytest.mark.asyncio
    async def test_search_documents_no_filter(self, kg):
        """Test searching documents without any filter."""
        await kg.add_document("doc1", "Content 1")
        await kg.add_document("doc2", "Content 2")
        
        all_docs = await kg.search_documents()
        assert len(all_docs) == 2

    @pytest.mark.asyncio
    async def test_search_documents_empty_result(self, kg):
        """Test searching documents with no matches."""
        await kg.add_document("doc1", "Content 1", {"type": "pdf"})
        
        result = await kg.search_documents(metadata_filter={"type": "video"})
        assert result == []

    @pytest.mark.asyncio
    async def test_update_document_metadata(self, kg):
        """Test updating document metadata."""
        doc_id = "test_doc_7"
        content = "Document with updatable metadata"
        original_metadata = {"version": "1.0", "author": "original"}
        
        await kg.add_document(doc_id, content, original_metadata)
        
        # Update metadata
        new_metadata = {"version": "2.0", "author": "updated", "status": "reviewed"}
        await kg.update_document_metadata(doc_id, new_metadata)
        
        retrieved = await kg.get_document(doc_id)
        assert retrieved["metadata"] == new_metadata
        assert retrieved["content"] == content  # Content should remain unchanged

    @pytest.mark.asyncio
    async def test_update_metadata_nonexistent_document(self, kg):
        """Test updating metadata for a document that doesn't exist."""
        # Should not raise an error
        await kg.update_document_metadata("nonexistent", {"test": "data"})

    @pytest.mark.asyncio
    async def test_clear_all_documents(self, kg):
        """Test clearing all documents from the knowledge graph."""
        # Add several documents
        for i in range(5):
            await kg.add_document(f"doc{i}", f"Content {i}")
            kg.embeddings[f"doc{i}"] = [float(i)] * 10  # Mock embeddings
        
        assert len(kg.documents) == 5
        assert len(kg.embeddings) == 5
        
        # Clear all
        await kg.clear()
        
        assert len(kg.documents) == 0
        assert len(kg.embeddings) == 0

    @pytest.mark.asyncio
    async def test_get_document_count(self, kg):
        """Test getting the count of documents."""
        assert await kg.get_document_count() == 0
        
        # Add documents
        for i in range(3):
            await kg.add_document(f"doc{i}", f"Content {i}")
        
        assert await kg.get_document_count() == 3

    @pytest.mark.asyncio
    async def test_export_data(self, kg):
        """Test exporting knowledge graph data."""
        # Add test documents
        await kg.add_document("doc1", "Content 1", {"type": "text"})
        await kg.add_document("doc2", "Content 2", {"type": "pdf"})
        
        exported_data = await kg.export_data()
        
        assert "documents" in exported_data
        assert len(exported_data["documents"]) == 2
        assert "doc1" in exported_data["documents"]
        assert "doc2" in exported_data["documents"]

    @pytest.mark.asyncio
    async def test_import_data(self, kg):
        """Test importing knowledge graph data."""
        # Prepare test data
        test_data = {
            "documents": {
                "imported_doc1": {
                    "content": "Imported content 1",
                    "metadata": {"source": "import"}
                },
                "imported_doc2": {
                    "content": "Imported content 2", 
                    "metadata": {"source": "import"}
                }
            }
        }
        
        await kg.import_data(test_data)
        
        assert len(kg.documents) == 2
        assert "imported_doc1" in kg.documents
        assert "imported_doc2" in kg.documents
        assert kg.documents["imported_doc1"]["content"] == "Imported content 1"

    @pytest.mark.asyncio
    async def test_import_invalid_data(self, kg):
        """Test importing invalid data structure."""
        invalid_data = {"not_documents": "invalid"}
        
        # Should handle gracefully
        await kg.import_data(invalid_data)
        assert len(kg.documents) == 0

    @pytest.mark.asyncio
    async def test_save_to_file(self, kg):
        """Test saving knowledge graph to file."""
        # Add test data
        await kg.add_document("doc1", "Test content", {"type": "test"})
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            await kg.save_to_file(tmp_path)
            
            # Verify file was created and contains data
            assert tmp_path.exists()
            
            with open(tmp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert "documents" in saved_data
            assert "doc1" in saved_data["documents"]
            
        finally:
            # Clean up
            tmp_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_load_from_file(self, kg):
        """Test loading knowledge graph from file."""
        # Create test data file
        test_data = {
            "documents": {
                "loaded_doc": {
                    "content": "Loaded content",
                    "metadata": {"source": "file"}
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(test_data, tmp_file)
            tmp_path = Path(tmp_file.name)
        
        try:
            await kg.load_from_file(tmp_path)
            
            assert len(kg.documents) == 1
            assert "loaded_doc" in kg.documents
            assert kg.documents["loaded_doc"]["content"] == "Loaded content"
            
        finally:
            # Clean up
            tmp_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_load_from_nonexistent_file(self, kg):
        """Test loading from a file that doesn't exist."""
        nonexistent_path = Path("/nonexistent/file.json")
        
        # Should handle gracefully
        await kg.load_from_file(nonexistent_path)
        assert len(kg.documents) == 0

    @pytest.mark.asyncio
    async def test_bulk_add_documents(self, kg):
        """Test adding multiple documents at once."""
        docs_to_add = [
            ("bulk1", "Bulk content 1", {"type": "bulk"}),
            ("bulk2", "Bulk content 2", {"type": "bulk"}),
            ("bulk3", "Bulk content 3", {"type": "bulk"})
        ]
        
        await kg.bulk_add_documents(docs_to_add)
        
        assert len(kg.documents) == 3
        for doc_id, content, metadata in docs_to_add:
            assert doc_id in kg.documents
            assert kg.documents[doc_id]["content"] == content
            assert kg.documents[doc_id]["metadata"] == metadata

    @pytest.mark.asyncio
    async def test_bulk_add_empty_list(self, kg):
        """Test bulk adding an empty list of documents."""
        await kg.bulk_add_documents([])
        assert len(kg.documents) == 0

    @pytest.mark.asyncio
    async def test_document_exists(self, kg):
        """Test checking if a document exists."""
        doc_id = "existence_test"
        
        assert not await kg.document_exists(doc_id)
        
        await kg.add_document(doc_id, "Test content")
        
        assert await kg.document_exists(doc_id)

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, kg):
        """Test concurrent operations on the knowledge graph."""
        import asyncio
        
        # Define concurrent operations
        async def add_docs():
            for i in range(10):
                await kg.add_document(f"concurrent_{i}", f"Content {i}")
        
        async def search_docs():
            for _ in range(5):
                await kg.search_documents()
                await asyncio.sleep(0.01)
        
        async def list_docs():
            for _ in range(5):
                await kg.list_documents()
                await asyncio.sleep(0.01)
        
        # Run operations concurrently
        await asyncio.gather(add_docs(), search_docs(), list_docs())
        
        # Verify final state
        assert len(kg.documents) == 10
        final_list = await kg.list_documents()
        assert len(final_list) == 10


class TestKnowledgeGraphFactory:
    """Test knowledge graph factory functions."""

    def test_create_knowledge_graph(self):
        """Test creating a knowledge graph instance."""
        kg = create_knowledge_graph()
        assert isinstance(kg, AsyncKnowledgeGraph)
        assert kg.documents == {}
        assert kg.embeddings == {}

    def test_create_multiple_instances(self):
        """Test that factory creates independent instances."""
        kg1 = create_knowledge_graph()
        kg2 = create_knowledge_graph()
        
        assert kg1 is not kg2
        assert kg1.documents is not kg2.documents

    def test_global_knowledge_graph_exists(self):
        """Test that global knowledge graph instance exists."""
        assert knowledge_graph is not None
        assert isinstance(knowledge_graph, AsyncKnowledgeGraph)

    @pytest.mark.asyncio
    async def test_global_knowledge_graph_functionality(self):
        """Test basic functionality of global knowledge graph."""
        # Clean up any existing data
        await knowledge_graph.clear()
        
        # Test basic operations
        await knowledge_graph.add_document("global_test", "Global test content")
        
        assert await knowledge_graph.get_document_count() == 1
        
        doc = await knowledge_graph.get_document("global_test")
        assert doc["content"] == "Global test content"
        
        # Clean up
        await knowledge_graph.clear()

    def test_global_knowledge_graph_persistence(self):
        """Test that global knowledge graph persists across imports."""
        # Import again and check it's the same instance
        from resync.core.knowledge_graph import knowledge_graph as imported_kg
        
        assert imported_kg is knowledge_graph
