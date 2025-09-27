"""Tests for resync.core.ia_auditor module."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, call
import asyncio
from datetime import datetime, timedelta

from resync.core.ia_auditor import (
    _validate_memory_for_analysis,
    _get_llm_analysis,
    _perform_action_on_memory,
    analyze_memory,
    analyze_and_flag_memories
)


class TestValidateMemoryForAnalysis:
    """Test the _validate_memory_for_analysis function."""

    @pytest.mark.asyncio
    async def test_validate_memory_basic_valid(self):
        """Test validation of a basic valid memory."""
        memory = {
            "id": "mem123",
            "user_query": "How to restart a service?",
            "agent_response": "Use systemctl restart service-name"
        }
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.is_memory_already_processed.return_value = False
            mock_kg.is_memory_approved.return_value = False
            
            result = await _validate_memory_for_analysis(memory)
            
            assert result is True

    @pytest.mark.asyncio
    async def test_validate_memory_already_processed(self):
        """Test validation when memory is already processed."""
        memory = {
            "id": "mem123",
            "user_query": "Test query",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.is_memory_already_processed.return_value = True
            
            result = await _validate_memory_for_analysis(memory)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_validate_memory_high_rating(self):
        """Test validation when memory has high rating."""
        memory = {
            "id": "mem123",
            "user_query": "Test query",
            "agent_response": "Test response",
            "rating": 5
        }
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.is_memory_already_processed.return_value = False
            
            result = await _validate_memory_for_analysis(memory)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_validate_memory_missing_user_query(self):
        """Test validation when user_query is missing."""
        memory = {
            "id": "mem123",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.is_memory_already_processed.return_value = False
            
            result = await _validate_memory_for_analysis(memory)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_validate_memory_missing_agent_response(self):
        """Test validation when agent_response is missing."""
        memory = {
            "id": "mem123",
            "user_query": "Test query"
        }
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.is_memory_already_processed.return_value = False
            
            result = await _validate_memory_for_analysis(memory)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_validate_memory_already_approved(self):
        """Test validation when memory is already approved by human."""
        memory = {
            "id": "mem123",
            "user_query": "Test query",
            "agent_response": "Test response"
        }
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.is_memory_already_processed.return_value = False
            mock_kg.is_memory_approved.return_value = True
            
            result = await _validate_memory_for_analysis(memory)
            
            assert result is False

    @pytest.mark.asyncio
    async def test_validate_memory_rating_threshold(self):
        """Test validation with rating at threshold (3)."""
        memory = {
            "id": "mem123",
            "user_query": "Test query", 
            "agent_response": "Test response",
            "rating": 3
        }
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.is_memory_already_processed.return_value = False
            
            result = await _validate_memory_for_analysis(memory)
            
            assert result is False  # Rating 3 should be skipped (>= 3)


class TestGetLLMAnalysis:
    """Test the _get_llm_analysis function."""

    @pytest.mark.asyncio
    async def test_get_llm_analysis_success(self):
        """Test successful LLM analysis."""
        user_query = "How to restart a service?"
        agent_response = "Use systemctl restart service-name"
        
        mock_llm_response = '{"is_incorrect": false, "confidence": 0.9, "reason": "Correct command"}'
        mock_parsed_response = {
            "is_incorrect": False,
            "confidence": 0.9,
            "reason": "Correct command"
        }
        
        with patch('resync.core.ia_auditor.call_llm', return_value=mock_llm_response), \
             patch('resync.core.ia_auditor.parse_llm_json_response', return_value=mock_parsed_response):
            
            result = await _get_llm_analysis(user_query, agent_response)
            
            assert result == mock_parsed_response

    @pytest.mark.asyncio
    async def test_get_llm_analysis_llm_failure(self):
        """Test LLM analysis when LLM call fails."""
        user_query = "Test query"
        agent_response = "Test response"
        
        with patch('resync.core.ia_auditor.call_llm', return_value=None):
            result = await _get_llm_analysis(user_query, agent_response)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_llm_analysis_parsing_error(self):
        """Test LLM analysis when JSON parsing fails."""
        user_query = "Test query"
        agent_response = "Test response"
        
        with patch('resync.core.ia_auditor.call_llm', return_value="invalid json"), \
             patch('resync.core.ia_auditor.parse_llm_json_response', side_effect=Exception("Parse error")):
            
            with patch('resync.core.ia_auditor.logger') as mock_logger:
                result = await _get_llm_analysis(user_query, agent_response)
                
                assert result is None
                mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_get_llm_analysis_with_settings(self):
        """Test that LLM analysis uses settings for model name."""
        user_query = "Test query"
        agent_response = "Test response"
        
        with patch('resync.core.ia_auditor.call_llm') as mock_call_llm, \
             patch('resync.core.ia_auditor.settings') as mock_settings:
            
            mock_settings.AUDITOR_MODEL_NAME = "test-model"
            mock_call_llm.return_value = '{"is_incorrect": false, "confidence": 0.8, "reason": "OK"}'
            
            await _get_llm_analysis(user_query, agent_response)
            
            # Verify call_llm was called with correct model
            call_args = mock_call_llm.call_args
            assert call_args[1]['model'] == "test-model"
            assert call_args[1]['max_tokens'] == 500


class TestPerformActionOnMemory:
    """Test the _perform_action_on_memory function."""

    @pytest.mark.asyncio
    async def test_perform_action_delete_high_confidence(self):
        """Test deletion action for high confidence incorrect memory."""
        memory = {
            "id": "mem123",
            "user_query": "Test query",
            "agent_response": "Wrong response"
        }
        
        analysis = {
            "is_incorrect": True,
            "confidence": 0.9,
            "reason": "Completely wrong advice"
        }
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.atomic_check_and_delete.return_value = True
            
            result = await _perform_action_on_memory(memory, analysis)
            
            assert result == ("delete", "mem123")
            mock_kg.atomic_check_and_delete.assert_called_once_with("mem123")

    @pytest.mark.asyncio
    async def test_perform_action_flag_medium_confidence(self):
        """Test flagging action for medium confidence incorrect memory."""
        memory = {
            "id": "mem456",
            "user_query": "Test query",
            "agent_response": "Questionable response"
        }
        
        analysis = {
            "is_incorrect": True,
            "confidence": 0.7,
            "reason": "Potentially misleading"
        }
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.atomic_check_and_flag.return_value = True
            
            result = await _perform_action_on_memory(memory, analysis)
            
            assert result[0] == "flag"
            flagged_memory = result[1]
            assert flagged_memory["id"] == "mem456"
            assert flagged_memory["ia_audit_reason"] == "Potentially misleading"
            assert flagged_memory["ia_audit_confidence"] == 0.7
            
            mock_kg.atomic_check_and_flag.assert_called_once_with("mem456", "Potentially misleading", 0.7)

    @pytest.mark.asyncio
    async def test_perform_action_no_action_low_confidence(self):
        """Test no action for low confidence incorrect memory."""
        memory = {
            "id": "mem789",
            "user_query": "Test query",
            "agent_response": "Uncertain response"
        }
        
        analysis = {
            "is_incorrect": True,
            "confidence": 0.5,  # Below threshold
            "reason": "Uncertain assessment"
        }
        
        result = await _perform_action_on_memory(memory, analysis)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_perform_action_no_action_correct_memory(self):
        """Test no action for correct memory."""
        memory = {
            "id": "mem101",
            "user_query": "Test query",
            "agent_response": "Correct response"
        }
        
        analysis = {
            "is_incorrect": False,
            "confidence": 0.9,
            "reason": "Correct advice"
        }
        
        result = await _perform_action_on_memory(memory, analysis)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_perform_action_delete_failed(self):
        """Test when delete operation fails."""
        memory = {"id": "mem123"}
        analysis = {"is_incorrect": True, "confidence": 0.9, "reason": "Wrong"}
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.atomic_check_and_delete.return_value = False
            
            result = await _perform_action_on_memory(memory, analysis)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_perform_action_flag_failed(self):
        """Test when flag operation fails."""
        memory = {"id": "mem456"}
        analysis = {"is_incorrect": True, "confidence": 0.7, "reason": "Wrong"}
        
        with patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            mock_kg.atomic_check_and_flag.return_value = False
            
            result = await _perform_action_on_memory(memory, analysis)
            
            assert result is None


class TestAnalyzeMemory:
    """Test the analyze_memory function."""

    @pytest.mark.asyncio
    async def test_analyze_memory_success(self):
        """Test successful memory analysis."""
        memory = {
            "id": "mem123",
            "user_query": "How to delete files?",
            "agent_response": "Use rm -rf /"
        }
        
        analysis = {
            "is_incorrect": True,
            "confidence": 0.95,
            "reason": "Dangerous command"
        }
        
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor._validate_memory_for_analysis', return_value=True), \
             patch('resync.core.ia_auditor.knowledge_graph') as mock_kg, \
             patch('resync.core.ia_auditor._get_llm_analysis', return_value=analysis), \
             patch('resync.core.ia_auditor._perform_action_on_memory', return_value=("delete", "mem123")):
            
            # Mock lock acquisition
            mock_lock_context = AsyncMock()
            mock_lock.acquire.return_value.__aenter__.return_value = mock_lock_context
            
            mock_kg.is_memory_flagged.return_value = False
            mock_kg.is_memory_approved.return_value = False
            
            result = await analyze_memory(memory)
            
            assert result == ("delete", "mem123")

    @pytest.mark.asyncio
    async def test_analyze_memory_invalid_for_analysis(self):
        """Test analysis when memory is invalid for analysis."""
        memory = {"id": "mem123"}
        
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor._validate_memory_for_analysis', return_value=False):
            
            mock_lock_context = AsyncMock()
            mock_lock.acquire.return_value.__aenter__.return_value = mock_lock_context
            
            result = await analyze_memory(memory)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_analyze_memory_already_flagged(self):
        """Test analysis when memory is already flagged."""
        memory = {"id": "mem123", "user_query": "test", "agent_response": "test"}
        
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor._validate_memory_for_analysis', return_value=True), \
             patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            
            mock_lock_context = AsyncMock()
            mock_lock.acquire.return_value.__aenter__.return_value = mock_lock_context
            
            mock_kg.is_memory_flagged.return_value = True
            
            result = await analyze_memory(memory)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_analyze_memory_llm_analysis_failed(self):
        """Test analysis when LLM analysis fails."""
        memory = {"id": "mem123", "user_query": "test", "agent_response": "test"}
        
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor._validate_memory_for_analysis', return_value=True), \
             patch('resync.core.ia_auditor.knowledge_graph') as mock_kg, \
             patch('resync.core.ia_auditor._get_llm_analysis', return_value=None):
            
            mock_lock_context = AsyncMock()
            mock_lock.acquire.return_value.__aenter__.return_value = mock_lock_context
            
            mock_kg.is_memory_flagged.return_value = False
            mock_kg.is_memory_approved.return_value = False
            
            result = await analyze_memory(memory)
            
            assert result is None

    @pytest.mark.asyncio
    async def test_analyze_memory_exception_handling(self):
        """Test exception handling in memory analysis."""
        memory = {"id": "mem123"}
        
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor.logger') as mock_logger:
            
            # Mock lock to raise exception
            mock_lock.acquire.side_effect = Exception("Lock error")
            
            result = await analyze_memory(memory)
            
            assert result is None
            mock_logger.error.assert_called()


class TestAnalyzeAndFlagMemories:
    """Test the analyze_and_flag_memories function."""

    @pytest.mark.asyncio
    async def test_analyze_and_flag_memories_success(self):
        """Test successful analysis and flagging of memories."""
        test_memories = [
            {"id": "mem1", "user_query": "query1", "agent_response": "response1"},
            {"id": "mem2", "user_query": "query2", "agent_response": "response2"}
        ]
        
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor.knowledge_graph') as mock_kg, \
             patch('resync.core.ia_auditor.analyze_memory') as mock_analyze, \
             patch('resync.core.ia_auditor.audit_queue') as mock_audit_queue:
            
            mock_lock.cleanup_expired_locks = AsyncMock()
            mock_kg.get_all_recent_conversations.return_value = test_memories
            mock_kg.delete_memory = AsyncMock()
            
            # Mock analyze_memory to return different results
            mock_analyze.side_effect = [
                ("delete", "mem1"),
                ("flag", {"id": "mem2", "ia_audit_reason": "flagged"})
            ]
            
            result = await analyze_and_flag_memories()
            
            assert result["deleted"] == 1
            assert result["flagged"] == 1
            
            # Verify delete was called
            mock_kg.delete_memory.assert_called_once_with("mem1")
            
            # Verify audit record was added
            mock_audit_queue.add_audit_record.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_and_flag_no_memories(self):
        """Test analysis when no memories are found."""
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor.knowledge_graph') as mock_kg:
            
            mock_lock.cleanup_expired_locks = AsyncMock()
            mock_kg.get_all_recent_conversations.return_value = []
            
            result = await analyze_and_flag_memories()
            
            assert result["deleted"] == 0
            assert result["flagged"] == 0

    @pytest.mark.asyncio
    async def test_analyze_and_flag_knowledge_graph_error(self):
        """Test handling of knowledge graph errors."""
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor.knowledge_graph') as mock_kg, \
             patch('resync.core.ia_auditor.logger') as mock_logger:
            
            mock_lock.cleanup_expired_locks = AsyncMock()
            mock_kg.get_all_recent_conversations.side_effect = Exception("KG Error")
            
            result = await analyze_and_flag_memories()
            
            assert result["deleted"] == 0
            assert result["flagged"] == 0
            mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_analyze_and_flag_lock_cleanup_error(self):
        """Test handling of lock cleanup errors."""
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor.knowledge_graph') as mock_kg, \
             patch('resync.core.ia_auditor.logger') as mock_logger:
            
            mock_lock.cleanup_expired_locks.side_effect = Exception("Cleanup error")
            mock_kg.get_all_recent_conversations.return_value = []
            
            # Should continue despite cleanup error
            result = await analyze_and_flag_memories()
            
            assert result["deleted"] == 0
            assert result["flagged"] == 0
            mock_logger.warning.assert_called()

    @pytest.mark.asyncio
    async def test_analyze_and_flag_concurrent_processing(self):
        """Test concurrent processing of multiple memories."""
        # Create multiple memories
        test_memories = [
            {"id": f"mem{i}", "user_query": f"query{i}", "agent_response": f"response{i}"}
            for i in range(10)
        ]
        
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor.knowledge_graph') as mock_kg, \
             patch('resync.core.ia_auditor.analyze_memory') as mock_analyze:
            
            mock_lock.cleanup_expired_locks = AsyncMock()
            mock_kg.get_all_recent_conversations.return_value = test_memories
            mock_kg.delete_memory = AsyncMock()
            
            # Mock analyze_memory to return None (no action needed)
            mock_analyze.return_value = None
            
            result = await analyze_and_flag_memories()
            
            # Verify analyze_memory was called for each memory
            assert mock_analyze.call_count == 10
            assert result["deleted"] == 0
            assert result["flagged"] == 0

    @pytest.mark.asyncio
    async def test_analyze_and_flag_mixed_results(self):
        """Test analysis with mixed results (delete, flag, no action)."""
        test_memories = [
            {"id": "mem1", "user_query": "query1", "agent_response": "response1"},
            {"id": "mem2", "user_query": "query2", "agent_response": "response2"},
            {"id": "mem3", "user_query": "query3", "agent_response": "response3"}
        ]
        
        with patch('resync.core.ia_auditor.audit_lock') as mock_lock, \
             patch('resync.core.ia_auditor.knowledge_graph') as mock_kg, \
             patch('resync.core.ia_auditor.analyze_memory') as mock_analyze, \
             patch('resync.core.ia_auditor.audit_queue') as mock_audit_queue:
            
            mock_lock.cleanup_expired_locks = AsyncMock()
            mock_kg.get_all_recent_conversations.return_value = test_memories
            mock_kg.delete_memory = AsyncMock()
            
            # Mock different results for each memory
            mock_analyze.side_effect = [
                ("delete", "mem1"),
                ("flag", {"id": "mem2", "ia_audit_reason": "flagged"}),
                None  # No action for mem3
            ]
            
            result = await analyze_and_flag_memories()
            
            assert result["deleted"] == 1
            assert result["flagged"] == 1
            
            # Verify appropriate actions were taken
            mock_kg.delete_memory.assert_called_once_with("mem1")
            mock_audit_queue.add_audit_record.assert_called_once()