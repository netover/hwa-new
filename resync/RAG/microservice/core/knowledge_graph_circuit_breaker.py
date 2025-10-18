"""
Circuit Breaker for Neo4j Knowledge Graph

This module provides a circuit breaker wrapper for the AsyncKnowledgeGraph class
in the RAG microservice.
"""

import logging
from typing import Optional
from resync.core.circuit_breaker import CircuitBreaker
from resync.core.knowledge_graph import AsyncKnowledgeGraph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create circuit breaker instance for Neo4j operations
neo4j_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60
)

class CircuitBreakerAsyncKnowledgeGraph:
    """
    Circuit breaker wrapper for AsyncKnowledgeGraph.
    
    This class provides a circuit breaker protected interface to Neo4j operations.
    When the circuit is open, read operations will return empty results (graceful degradation),
    while write operations will fail fast.
    """
    
    def __init__(self):
        """Initialize the circuit breaker wrapper."""
        self._kg = AsyncKnowledgeGraph()
        logger.info("CircuitBreakerAsyncKnowledgeGraph initialized")
    
    async def add_content(self, content: str, metadata: dict) -> str:
        """Add content to knowledge graph with circuit breaker protection."""
        try:
            async with neo4j_circuit_breaker:
                return await self._kg.add_content(content, metadata)
        except Exception as e:
            logger.error(f"Neo4j add_content failed: {str(e)}", exc_info=True)
            raise
    
    async def get_relevant_context(self, query: str, top_k: int = 5) -> list:
        """Get relevant context from knowledge graph with circuit breaker protection."""
        try:
            async with neo4j_circuit_breaker:
                return await self._kg.get_relevant_context(query, top_k)
        except Exception as e:
            logger.warning(f"Neo4j get_relevant_context failed (circuit breaker active): {str(e)}")
            # Return empty list as graceful degradation for read operations
            return []
    
    async def add_conversation(self, conversation_id: str, messages: list) -> str:
        """Add conversation to knowledge graph with circuit breaker protection."""
        try:
            async with neo4j_circuit_breaker:
                return await self._kg.add_conversation(conversation_id, messages)
        except Exception as e:
            logger.error(f"Neo4j add_conversation failed: {str(e)}", exc_info=True)
            raise
    
    async def search_similar_issues(self, query: str, top_k: int = 5) -> list:
        """Search for similar issues in knowledge graph with circuit breaker protection."""
        try:
            async with neo4j_circuit_breaker:
                return await self._kg.search_similar_issues(query, top_k)
        except Exception as e:
            logger.warning(f"Neo4j search_similar_issues failed (circuit breaker active): {str(e)}")
            # Return empty list as graceful degradation for read operations
            return []
    
    async def get_all_recent_conversations(self, limit: int = 10) -> list:
        """Get all recent conversations from knowledge graph with circuit breaker protection."""
        try:
            async with neo4j_circuit_breaker:
                return await self._kg.get_all_recent_conversations(limit)
        except Exception as e:
            logger.warning(f"Neo4j get_all_recent_conversations failed (circuit breaker active): {str(e)}")
            # Return empty list as graceful degradation for read operations
            return []
    
    async def get_memories(self, memory_ids: list) -> list:
        """Get specific memories from knowledge graph with circuit breaker protection."""
        try:
            async with neo4j_circuit_breaker:
                return await self._kg.get_memories(memory_ids)
        except Exception as e:
            logger.warning(f"Neo4j get_memories failed (circuit breaker active): {str(e)}")
            # Return empty list as graceful degradation for read operations
            return []
    
    async def get_all_memories(self) -> list:
        """Get all memories from knowledge graph with circuit breaker protection."""
        try:
            async with neo4j_circuit_breaker:
                return await self._kg.get_all_memories()
        except Exception as e:
            logger.warning(f"Neo4j get_all_memories failed (circuit breaker active): {str(e)}")
            # Return empty list as graceful degradation for read operations
            return []
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return neo4j_circuit_breaker.get_stats()
    
    def reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        neo4j_circuit_breaker.reset()


def create_circuit_breaker_knowledge_graph() -> CircuitBreakerAsyncKnowledgeGraph:
    """Factory function to create a circuit breaker protected knowledge graph."""
    return CircuitBreakerAsyncKnowledgeGraph()


def get_neo4j_circuit_breaker_stats() -> dict:
    """Get statistics for the Neo4j circuit breaker."""
    return neo4j_circuit_breaker.get_stats()