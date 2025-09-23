"""
End-to-end integration tests for the Resync system.

This module provides comprehensive integration tests that verify the complete
user flow from TWS data ingestion through knowledge graph storage and audit processing.
"""

import asyncio
import pytest
import pytest_asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from datetime import datetime

from resync.core.knowledge_graph import AsyncKnowledgeGraph, AsyncMem0Client
from resync.core.audit_queue import AsyncAuditQueue
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.utils.llm import call_llm
from resync.core.utils.json_parser import parse_llm_json_response


class TestAsyncKnowledgeGraph:
    """Test that knowledge graph methods are truly async and non-blocking."""

    @pytest_asyncio.fixture
    async def async_knowledge_graph(self):
        """Create an AsyncKnowledgeGraph instance for testing."""
        # Create a real instance but mock the HTTP client to avoid actual API calls
        kg = AsyncKnowledgeGraph()

        # Mock the async client to return predictable responses
        async def mock_add(memory_content):
            return "mock_memory_id_123"

        async def mock_search(query, limit=5):
            return [
                {
                    "id": "mock_memory_1",
                    "content": {"type": "conversation", "user_query": "test query"},
                    "observations": []
                }
            ]

        async def mock_update(memory_id, updates):
            return {"id": memory_id, "updates": updates}

        async def mock_delete(memory_id):
            pass

        async def mock_add_observations(memory_id, observations):
            pass

        # Replace client methods with mocks
        kg.client.add = mock_add
        kg.client.search = mock_search
        kg.client.update = mock_update
        kg.client.delete = mock_delete
        kg.client.add_observations = mock_add_observations

        return kg

    async def test_async_knowledge_graph_non_blocking(self, async_knowledge_graph):
        """Test that knowledge graph operations don't block the event loop."""

        async def concurrent_operations():
            """Run multiple async operations concurrently."""
            tasks = []

            # Add multiple conversations concurrently
            for i in range(5):
                task = async_knowledge_graph.add_conversation(
                    user_query=f"Test query {i}",
                    agent_response=f"Test response {i}",
                    agent_id=f"agent_{i}"
                )
                tasks.append(task)

            # Add search operations
            for i in range(3):
                task = async_knowledge_graph.search_similar_issues(f"search query {i}")
                tasks.append(task)

            # Execute all operations concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()

            # All operations should complete quickly (less than 1 second for mocks)
            assert end_time - start_time < 1.0

            # Should have 8 results (5 add + 3 search)
            assert len(results) == 8

            # Add operations should return memory IDs
            for i in range(5):
                assert results[i] == "mock_memory_id_123"

            # Search operations should return lists
            for i in range(5, 8):
                assert isinstance(results[i], list)

        await concurrent_operations()

    async def test_knowledge_graph_method_signatures(self, async_knowledge_graph):
        """Test that all knowledge graph methods are properly async."""
        import inspect

        # Check that all public methods are async
        async_methods = [
            'add_conversation',
            'search_similar_issues',
            'search_conversations',
            'add_solution_feedback',
            'get_all_recent_conversations',
            'get_relevant_context',
            'is_memory_flagged',
            'is_memory_approved',
            'delete_memory',
            'add_observations',
            'is_memory_already_processed',
            'atomic_check_and_flag',
            'atomic_check_and_delete'
        ]

        for method_name in async_methods:
            method = getattr(async_knowledge_graph, method_name)
            assert inspect.iscoroutinefunction(method), f"{method_name} should be async"

    async def test_memory_operations_are_isolated(self, async_knowledge_graph):
        """Test that memory operations don't interfere with each other."""

        # Run multiple operations concurrently
        tasks = []

        # Add operations
        for i in range(3):
            task = async_knowledge_graph.add_conversation(
                user_query=f"Query {i}",
                agent_response=f"Response {i}",
                agent_id=f"agent_{i}"
            )
            tasks.append(task)

        # Search operations
        for i in range(2):
            task = async_knowledge_graph.search_similar_issues(f"Query {i}")
            tasks.append(task)

        # Execute concurrently
        results = await asyncio.gather(*tasks)

        # Verify each operation completed independently
        assert len(results) == 5
        for i in range(3):
            assert results[i] == "mock_memory_id_123"

        for i in range(3, 5):
            assert isinstance(results[i], list)


class TestResyncIntegration:
    """Integration tests for the complete Resync system flow."""

    @pytest_asyncio.fixture
    async def mock_knowledge_graph(self):
        """Create a mock knowledge graph for testing."""
        kg = AsyncMock(spec=AsyncKnowledgeGraph)

        # Mock conversation memories
        kg.get_all_recent_conversations.return_value = [
            {
                "id": "mem_1",
                "user_query": "How do I restart a job in TWS?",
                "agent_response": "You can restart a job using the 'rerun' command in TWS console.",
                "rating": 2,
                "observations": []
            },
            {
                "id": "mem_2",
                "user_query": "What's the status of job ABC123?",
                "agent_response": "The job ABC123 is currently running and should complete in 5 minutes.",
                "rating": 4,
                "observations": []
            },
            {
                "id": "mem_3",
                "user_query": "How to fix permission denied error?",
                "agent_response": "Try running 'chmod 755' on the script file.",
                "rating": 1,
                "observations": []
            }
        ]

        # Mock atomic check methods
        kg.is_memory_flagged.side_effect = [False, False, False]
        kg.is_memory_approved.side_effect = [False, False, False]

        # Mock action methods
        kg.delete_memory = AsyncMock()
        kg.add_observations = AsyncMock()

        return kg

    @pytest_asyncio.fixture
    async def mock_audit_queue(self):
        """Create a mock audit queue for testing."""
        aq = AsyncMock(spec=AsyncAuditQueue)

        # Mock check methods
        aq.is_memory_approved.side_effect = [False, False, False]

        # Mock action methods
        aq.add_audit_record = AsyncMock()

        return aq

    @pytest_asyncio.fixture
    async def mock_llm_responses(self):
        """Mock LLM responses for different scenarios."""
        return {
            "correct_response": '{"is_incorrect": false, "confidence": 0.95, "reason": "Response is accurate"}',
            "incorrect_response": '{"is_incorrect": true, "confidence": 0.90, "reason": "Technical error in response"}',
            "flag_response": '{"is_incorrect": true, "confidence": 0.70, "reason": "Suggests wrong command"}',
            "malformed_json": 'This is not JSON at all, just plain text response.',
            "json_with_markdown": '```json\n{"is_incorrect": true, "confidence": 0.85, "reason": "Bad advice"}\n```',
            "json_with_prefix": 'Here is the analysis:\n{"is_incorrect": false, "confidence": 0.80, "reason": "Good response"}'
        }

    async def test_complete_user_flow_correct_responses(
        self,
        mock_knowledge_graph,
        mock_audit_queue,
        mock_llm_responses
    ):
        """Test the complete flow with mostly correct agent responses."""
        with patch('resync.core.ia_auditor.knowledge_graph', mock_knowledge_graph), \
             patch('resync.core.ia_auditor.audit_queue', mock_audit_queue), \
             patch('resync.core.ia_auditor.call_llm') as mock_call_llm:

            # Configure LLM to return correct responses
            mock_call_llm.side_effect = [
                mock_llm_responses["correct_response"],  # First memory - correct
                mock_call_llm_responses["correct_response"],  # Second memory - correct
                mock_call_llm_responses["incorrect_response"]  # Third memory - incorrect
            ]

            # Run the analysis
            result = await analyze_and_flag_memories()

            # Verify results
            assert result["deleted"] == 1  # One memory should be deleted
            assert result["flagged"] == 1  # One memory should be flagged

            # Verify knowledge graph interactions
            mock_knowledge_graph.get_all_recent_conversations.assert_called_once_with(100)
            mock_knowledge_graph.delete_memory.assert_called_once_with("mem_3")
            mock_knowledge_graph.add_observations.assert_called_once()

            # Verify audit queue interactions
            mock_audit_queue.add_audit_record.assert_called_once()

    async def test_complete_user_flow_malformed_json(
        self,
        mock_knowledge_graph,
        mock_audit_queue
    ):
        """Test handling of malformed JSON responses from LLM."""
        with patch('resync.core.ia_auditor.knowledge_graph', mock_knowledge_graph), \
             patch('resync.core.ia_auditor.audit_queue', mock_audit_queue), \
             patch('resync.core.ia_auditor.call_llm') as mock_call_llm:

            # Configure LLM to return malformed JSON
            mock_call_llm.return_value = "This is not JSON at all, just plain text response."

            # Run the analysis
            result = await analyze_and_flag_memories()

            # Verify no actions were taken due to parsing failure
            assert result["deleted"] == 0
            assert result["flagged"] == 0

            # Verify no memory modifications occurred
            mock_knowledge_graph.delete_memory.assert_not_called()
            mock_knowledge_graph.add_observations.assert_not_called()
            mock_audit_queue.add_audit_record.assert_not_called()

    async def test_json_parser_robustness(self, mock_llm_responses):
        """Test the robust JSON parser with various malformed inputs."""
        # Test clean JSON
        result = parse_llm_json_response(mock_llm_responses["correct_response"])
        assert result["is_incorrect"] is False
        assert result["confidence"] == 0.95

        # Test JSON with markdown formatting
        result = parse_llm_json_response(mock_llm_responses["json_with_markdown"])
        assert result["is_incorrect"] is True
        assert result["confidence"] == 0.85

        # Test JSON with prefix
        result = parse_llm_json_response(mock_llm_responses["json_with_prefix"])
        assert result["is_incorrect"] is False
        assert result["confidence"] == 0.80

        # Test malformed JSON (should raise exception)
        with pytest.raises(Exception):
            parse_llm_json_response(mock_llm_responses["malformed_json"])

        # Test with required keys validation
        result = parse_llm_json_response(
            mock_llm_responses["correct_response"],
            required_keys=["is_incorrect", "confidence", "reason"]
        )
        assert all(key in result for key in ["is_incorrect", "confidence", "reason"])

    async def test_memory_already_processed(
        self,
        mock_knowledge_graph,
        mock_audit_queue,
        mock_llm_responses
    ):
        """Test that already flagged/approved memories are skipped."""
        # Configure one memory to be already flagged
        mock_knowledge_graph.is_memory_flagged.side_effect = [True, False, False]

        with patch('resync.core.ia_auditor.knowledge_graph', mock_knowledge_graph), \
             patch('resync.core.ia_auditor.audit_queue', mock_audit_queue), \
             patch('resync.core.ia_auditor.call_llm') as mock_call_llm:

            mock_call_llm.return_value = mock_llm_responses["incorrect_response"]

            # Run the analysis
            result = await analyze_and_flag_memories()

            # Verify the flagged memory was skipped
            assert result["deleted"] == 0
            assert result["flagged"] == 0

    async def test_audit_queue_integration(
        self,
        mock_knowledge_graph,
        mock_audit_queue
    ):
        """Test the integration between knowledge graph and audit queue."""
        with patch('resync.core.ia_auditor.knowledge_graph', mock_knowledge_graph), \
             patch('resync.core.ia_auditor.audit_queue', mock_audit_queue), \
             patch('resync.core.ia_auditor.call_llm') as mock_call_llm:

            # Configure LLM to flag a memory
            mock_call_llm.return_value = '{"is_incorrect": true, "confidence": 0.70, "reason": "Wrong command"}'

            # Run the analysis
            await analyze_and_flag_memories()

            # Verify the memory was added to audit queue
            mock_audit_queue.add_audit_record.assert_called_once()
            call_args = mock_audit_queue.add_audit_record.call_args[0][0]

            assert call_args["id"] == "mem_3"
            assert call_args["ia_audit_reason"] == "Wrong command"
            assert call_args["ia_audit_confidence"] == 0.70

    async def test_conversation_rating_filter(self, mock_knowledge_graph, mock_audit_queue):
        """Test that high-rated conversations are skipped."""
        # Add a high-rated memory
        mock_knowledge_graph.get_all_recent_conversations.return_value = [
            {
                "id": "mem_high_rated",
                "user_query": "How to check job status?",
                "agent_response": "Use 'conman showjobs' to check status.",
                "rating": 5,  # High rating - should be skipped
                "observations": []
            }
        ]

        with patch('resync.core.ia_auditor.knowledge_graph', mock_knowledge_graph), \
             patch('resync.core.ia_auditor.audit_queue', mock_audit_queue), \
             patch('resync.core.ia_auditor.call_llm') as mock_call_llm:

            mock_call_llm.return_value = '{"is_incorrect": true, "confidence": 0.90, "reason": "Bad response"}'

            # Run the analysis
            result = await analyze_and_flag_memories()

            # Verify high-rated memory was skipped
            assert result["deleted"] == 0
            assert result["flagged"] == 0

    async def test_empty_and_invalid_memories(self, mock_knowledge_graph, mock_audit_queue):
        """Test handling of empty or invalid memory data."""
        mock_knowledge_graph.get_all_recent_conversations.return_value = [
            {"id": "mem_empty", "user_query": "", "agent_response": "Response"},  # Empty query
            {"id": "mem_no_response", "user_query": "Query", "agent_response": ""},  # Empty response
            {"id": "mem_null_rating", "user_query": "Query", "agent_response": "Response", "rating": None}
        ]

        with patch('resync.core.ia_auditor.knowledge_graph', mock_knowledge_graph), \
             patch('resync.core.ia_auditor.audit_queue', mock_audit_queue), \
             patch('resync.core.ia_auditor.call_llm') as mock_call_llm:

            mock_call_llm.return_value = '{"is_incorrect": true, "confidence": 0.90, "reason": "Bad"}'

            # Run the analysis
            result = await analyze_and_flag_memories()

            # Verify invalid memories were skipped
            assert result["deleted"] == 0
            assert result["flagged"] == 0


class TestIntegrationErrorHandling:
    """Test error handling in integration scenarios."""

    async def test_knowledge_graph_failure(self, mock_audit_queue):
        """Test behavior when knowledge graph fails."""
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg, \
             patch('resync.core.ia_auditor.audit_queue', mock_audit_queue):

            # Make knowledge graph throw an exception
            mock_kg.get_all_recent_conversations.side_effect = Exception("Database connection failed")

            # Run the analysis
            result = await analyze_and_flag_memories()

            # Verify graceful handling
            assert result["deleted"] == 0
            assert result["flagged"] == 0

    async def test_llm_failure_handling(self, mock_knowledge_graph, mock_audit_queue):
        """Test behavior when LLM calls fail."""
        with patch('resync.core.ia_auditor.knowledge_graph', mock_knowledge_graph), \
             patch('resync.core.ia_auditor.audit_queue', mock_audit_queue), \
             patch('resync.core.ia_auditor.call_llm') as mock_call_llm:

            # Make LLM calls fail
            mock_call_llm.return_value = None  # Simulate LLM failure

            # Run the analysis
            result = await analyze_and_flag_memories()

            # Verify no actions taken on LLM failure
            assert result["deleted"] == 0
            assert result["flagged"] == 0


class TestIntegrationPerformance:
    """Performance-related integration tests."""

    async def test_large_memory_batch(self, mock_knowledge_graph, mock_audit_queue):
        """Test performance with a large batch of memories."""
        # Create a large batch of memories
        large_memory_batch = []
        for i in range(100):
            large_memory_batch.append({
                "id": f"mem_{i}",
                "user_query": f"Query {i}",
                "agent_response": f"Response {i}",
                "rating": 2,
                "observations": []
            })

        mock_knowledge_graph.get_all_recent_conversations.return_value = large_memory_batch
        mock_knowledge_graph.is_memory_flagged.side_effect = [False] * 100
        mock_knowledge_graph.is_memory_approved.side_effect = [False] * 100

        with patch('resync.core.ia_auditor.knowledge_graph', mock_knowledge_graph), \
             patch('resync.core.ia_auditor.audit_queue', mock_audit_queue), \
             patch('resync.core.ia_auditor.call_llm') as mock_call_llm:

            # Configure LLM to return mixed results
            responses = []
            for i in range(100):
                if i % 10 == 0:  # Every 10th response is incorrect
                    responses.append('{"is_incorrect": true, "confidence": 0.90, "reason": "Error"}')
                else:
                    responses.append('{"is_incorrect": false, "confidence": 0.95, "reason": "Good"}')

            mock_call_llm.side_effect = responses

            # Run the analysis
            result = await analyze_and_flag_memories()

            # Verify correct processing of large batch
            assert result["deleted"] == 10  # 10 incorrect responses
            assert result["flagged"] == 0  # No flagged (all above threshold for deletion)

            # Verify all memories were processed
            assert mock_call_llm.call_count == 100