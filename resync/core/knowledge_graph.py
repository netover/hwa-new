"""
Knowledge Graph Integration for Resync

This module implements a persistent knowledge graph using Mem0 AI to enable
continuous learning from user interactions with AI agents. It captures
conversations, outcomes, and solutions to build a self-improving system.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

import mem0
from mem0.config import MemoryConfig

# --- Logging Setup ---
logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """
    A wrapper around Mem0 AI to manage a persistent knowledge graph for the Resync system.
    
    The knowledge graph stores:
    - Conversations between users and AI agents
    - Problem descriptions and root causes
    - Solutions and troubleshooting steps
    - User feedback on solution effectiveness
    
    This enables RAG (Retrieval-Augmented Generation) to become more intelligent over time.
    """

    def __init__(self, data_dir: Path = Path(".mem0")):
        """
        Initialize the KnowledgeGraph with Mem0 configuration.
        
        Args:
            data_dir: Directory to store persistent memory data.
        """
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        
        # Configure Mem0 with a vector store (Qdrant) and embedding model
        self.config = MemoryConfig(
            storage={"provider": "qdrant", "config": {"host": "localhost", "port": 6333}},
            embeddings={"provider": "openai", "model": "text-embedding-3-small"},
            llm={"provider": "openai", "model": "gpt-4o-mini"}
        )
        
        # Initialize Mem0 client
        self.client = mem0.MemoryClient(config=self.config)
        logger.info(f"KnowledgeGraph initialized with data directory: {self.data_dir}")

    def add_conversation(self, user_query: str, agent_response: str, agent_id: str, context: Dict[str, Any] = None) -> str:
        """
        Stores a conversation between a user and an agent in the knowledge graph.
        
        Args:
            user_query: The user's question or command.
            agent_response: The agent's response.
            agent_id: The ID of the agent that responded.
            context: Additional context (e.g., system status, error codes) to enrich the memory.
            
        Returns:
            The unique ID of the stored memory.
        """
        # Create a structured memory record
        memory_content = {
            "type": "conversation",
            "user_query": user_query,
            "agent_response": agent_response,
            "agent_id": agent_id,
            "context": context or {}
        }
        
        # Store in Mem0
        memory_id = self.client.add(memory_content)
        logger.info(f"Added conversation to knowledge graph. Memory ID: {memory_id}")
        return memory_id

    def search_similar_issues(self, query: str, limit: int = 5) -> list:
        """
        Searches the knowledge graph for similar past issues and solutions.
        
        Args:
            query: The current problem or question to match against.
            limit: Maximum number of similar memories to return.
            
        Returns:
            A list of relevant past memories with their metadata.
        """
        memories = self.client.search(query, limit=limit)
        logger.info(f"Found {len(memories)} similar issues for query: {query}")
        return memories

    def add_solution_feedback(self, memory_id: str, feedback: str, rating: int):
        """
        Adds user feedback to a specific memory in the knowledge graph.
        
        Args:
            memory_id: The ID of the memory to add feedback to.
            feedback: The user's textual feedback (e.g., 'This helped!', 'Not useful').
            rating: A numerical rating from 1 to 5.
        """
        # Update the memory with feedback
        self.client.update(memory_id, metadata={"feedback": feedback, "rating": rating})
        logger.info(f"Added feedback to memory {memory_id}: {rating}/5 - {feedback}")

    def get_relevant_context(self, user_query: str) -> str:
        """
        Retrieves a structured text summary of relevant knowledge from the graph to use in RAG.
        
        Args:
            user_query: The current user query.
            
        Returns:
            A formatted string of relevant past solutions and context.
        """
        similar_issues = self.search_similar_issues(user_query, limit=3)
        if not similar_issues:
            return "Nenhuma solução similar encontrada na base de conhecimento."
        
        context_parts = []
        for mem in similar_issues:
            if mem.get('content', {}).get('type') == 'conversation':
                content = mem['content']
                context_parts.append(f"""
--- Problema Similar ---
Usuário: {content.get('user_query')}
Solução: {content.get('agent_response')}
Avaliação: {content.get('metadata', {}).get('rating', 'N/A')}/5
""")
        
        return "\n".join(context_parts)

# --- Global Instance ---
# Create a single, globally accessible instance of the KnowledgeGraph.
knowledge_graph = KnowledgeGraph()
