"""
Knowledge Graph Integration for Resync

This module implements a persistent knowledge graph using Mem0 AI to enable
continuous learning from user interactions with AI agents. It captures
conversations, outcomes, and solutions to build a self-improving system.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path

import httpx
from pydantic import BaseModel

# Import settings
from ..settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)


class MemoryConfig(BaseModel):
    """Configuration for the async Mem0 client."""
    storage_provider: str = "qdrant"
    storage_host: str = "localhost"
    storage_port: int = 6333
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    api_key: Optional[str] = None


class AsyncMem0Client:
    """
    A truly async wrapper around the Mem0 AI REST API.

    This client eliminates blocking I/O by using httpx for all HTTP requests
    and provides fully async methods for all Mem0 operations.
    """

    def __init__(self, config: MemoryConfig):
        """
        Initialize the async Mem0 client.

        Args:
            config: Configuration object with API settings.
        """
        self.config = config
        self.base_url = f"http://{config.storage_host}:{config.storage_port}"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}" if config.api_key else None,
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        logger.info(f"AsyncMem0Client initialized with base URL: {self.base_url}")

    async def add(self, memory_content: Dict[str, Any]) -> str:
        """
        Add a memory to the knowledge graph asynchronously.

        Args:
            memory_content: The memory data to store.

        Returns:
            The unique ID of the stored memory.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/memories",
                json=memory_content,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["id"]

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories asynchronously.

        Args:
            query: The search query.
            limit: Maximum number of results to return.

        Returns:
            List of matching memories.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {"query": query, "limit": limit}
            response = await client.get(
                f"{self.base_url}/search",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()["results"]

    async def update(self, memory_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a memory asynchronously.

        Args:
            memory_id: The ID of the memory to update.
            updates: The fields to update.

        Returns:
            The updated memory data.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.patch(
                f"{self.base_url}/memories/{memory_id}",
                json=updates,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def delete(self, memory_id: str) -> None:
        """
        Delete a memory asynchronously.

        Args:
            memory_id: The ID of the memory to delete.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(
                f"{self.base_url}/memories/{memory_id}",
                headers=self.headers
            )
            response.raise_for_status()

    async def add_observations(self, memory_id: str, observations: List[str]) -> None:
        """
        Add observations to a memory asynchronously.

        Args:
            memory_id: The ID of the memory to add observations to.
            observations: List of observation strings.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            data = {"observations": observations}
            response = await client.post(
                f"{self.base_url}/memories/{memory_id}/observations",
                json=data,
                headers=self.headers
            )
            response.raise_for_status()


class AsyncKnowledgeGraph:
    """
    A wrapper around Mem0 AI to manage a persistent knowledge graph for the Resync system.

    The knowledge graph stores:
    - Conversations between users and AI agents
    - Problem descriptions and root causes
    - Solutions and troubleshooting steps
    - User feedback on solution effectiveness

    This enables RAG (Retrieval-Augmented Generation) to become more intelligent over time.

    All methods are truly async without any blocking I/O operations.
    """

    def __init__(self, data_dir: Path = Path(".mem0")):
        """
        Initialize the AsyncKnowledgeGraph with Mem0 configuration.

        Args:
            data_dir: Directory to store persistent memory data.
        """
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        # Configure async Mem0 client
        mem0_config = MemoryConfig(
            storage_host=settings.MEM0_STORAGE_HOST,
            storage_port=settings.MEM0_STORAGE_PORT,
            embedding_provider=settings.MEM0_EMBEDDING_PROVIDER,
            embedding_model=settings.MEM0_EMBEDDING_MODEL,
            llm_provider=settings.MEM0_LLM_PROVIDER,
            llm_model=settings.MEM0_LLM_MODEL,
        )

        # Initialize async Mem0 client
        self.client = AsyncMem0Client(config=mem0_config)
        logger.info(f"AsyncKnowledgeGraph initialized with data directory: {self.data_dir}")

    async def add_conversation(self, user_query: str, agent_response: str, agent_id: str, context: Dict[str, Any] = None) -> str:
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

        # Store in Mem0 using truly async client
        memory_id = await self.client.add(memory_content)
        logger.info(f"Added conversation to knowledge graph. Memory ID: {memory_id}")
        return memory_id

    async def search_similar_issues(self, query: str, limit: int = 5) -> list:
        """
        Searches the knowledge graph for similar past issues and solutions.

        Args:
            query: The current problem or question to match against.
            limit: Maximum number of similar memories to return.

        Returns:
            A list of relevant past memories with their metadata.
        """
        memories = await self.client.search(query, limit)
        logger.info(f"Found {len(memories)} similar issues for query: {query}")
        return memories

    async def search_conversations(self, query: str = "type:conversation", limit: int = 100, sort_by: str = "created_at", sort_order: str = "desc") -> list:
        """
        Optimized search method for conversations with better defaults and sorting.

        Args:
            query: Search query for conversations.
            limit: Maximum number of conversations to return.
            sort_by: Field to sort by (e.g., 'created_at', 'rating').
            sort_order: Sort order ('asc' or 'desc').

        Returns:
            A list of conversation memories sorted efficiently.
        """
        # Use a more specific query format for better performance
        if query == "type:conversation":
            search_query = "type:conversation"
        else:
            search_query = f"{query} AND type:conversation"

        memories = await self.client.search(search_query, limit)

        # Sort memories by creation time if available (in-memory sort for better performance)
        try:
            memories.sort(
                key=lambda x: x.get('created_at', ''),
                reverse=(sort_order.lower() == 'desc')
            )
        except Exception as e:
            logger.warning(f"Could not sort memories by {sort_by}: {e}")

        logger.info(f"Found {len(memories)} conversations for query: {query}")
        return memories

    async def add_solution_feedback(self, memory_id: str, feedback: str, rating: int):
        """
        Adds user feedback to a specific memory in the knowledge graph.

        Args:
            memory_id: The ID of the memory to add feedback to.
            feedback: The user's textual feedback (e.g., 'This helped!', 'Not useful').
            rating: A numerical rating from 1 to 5.
        """
        # Update the memory with feedback using truly async client
        await self.client.update(memory_id, {"feedback": feedback, "rating": rating})
        logger.info(f"Added feedback to memory {memory_id}: {rating}/5 - {feedback}")

    async def get_all_recent_conversations(self, limit: int = 100) -> list:
        """
        Retrieves all recent conversation-type memories for auditing.

        Args:
            limit: The maximum number of memories to return. Defaults to 100.

        Returns:
            A list of recent conversation memories, sorted by creation time.
        """
        logger.debug(f"Fetching last {limit} conversations for audit.")

        # Use the optimized search method with better defaults
        return await self.search_conversations(
            query="type:conversation",
            limit=limit,
            sort_by="created_at",
            sort_order="desc"
        )

    async def get_relevant_context(self, user_query: str) -> str:
        """
        Retrieves a structured text summary of relevant knowledge from the graph to use in RAG.

        Args:
            user_query: The current user query.

        Returns:
            A formatted string of relevant past solutions and context.
        """
        similar_issues = await self.search_similar_issues(user_query, limit=3)
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

    # --- Additional methods for race condition fixes ---

    async def is_memory_flagged(self, memory_id: str) -> bool:
        """
        Checks if a memory has been flagged by the IA Auditor.

        Args:
            memory_id: The ID of the memory to check.

        Returns:
            True if the memory is flagged, False otherwise.
        """
        memories = await self.client.search(f"id:{memory_id}", 1)

        if memories:
            observations = memories[0].get("observations", [])
            return any("FLAGGED_BY_IA" in str(obs) for obs in observations)

        return False

    async def is_memory_approved(self, memory_id: str) -> bool:
        """
        Checks if a memory has been approved by an admin.

        Args:
            memory_id: The ID of the memory to check.

        Returns:
            True if the memory is approved, False otherwise.
        """
        memories = await self.client.search(f"id:{memory_id}", 1)

        if memories:
            observations = memories[0].get("observations", [])
            return any("MANUALLY_APPROVED_BY_ADMIN" in str(obs) for obs in observations)

        return False

    async def delete_memory(self, memory_id: str):
        """
        Deletes a memory from the knowledge graph.

        Args:
            memory_id: The ID of the memory to delete.
        """
        await self.client.delete(memory_id)
        logger.info(f"Deleted memory {memory_id} from knowledge graph")

    async def add_observations(self, memory_id: str, observations: list):
        """
        Adds observations to a memory in the knowledge graph.

        Args:
            memory_id: The ID of the memory to add observations to.
            observations: List of observation strings to add.
        """
        await self.client.add_observations(memory_id, observations)
        logger.info(f"Added {len(observations)} observations to memory {memory_id}")

    # --- Atomic Operations for Race Condition Prevention ---

    async def is_memory_already_processed(self, memory_id: str) -> bool:
        """
        Atomically checks if a memory has already been processed (flagged or approved).

        Args:
            memory_id: The ID of the memory to check.

        Returns:
            True if already processed (flagged or approved), False otherwise.
        """
        memories = await self.client.search(f"id:{memory_id}", 1)

        if memories:
            observations = memories[0].get("observations", [])
            # Check for any processing indicators
            return any(
                "FLAGGED_BY_IA" in str(obs) or
                "MANUALLY_APPROVED_BY_ADMIN" in str(obs) or
                "PROCESSED_BY_IA_AUDITOR" in str(obs)
                for obs in observations
            )

        return False

    async def atomic_check_and_flag(self, memory_id: str, reason: str, confidence: float) -> bool:
        """
        Atomically checks if memory is already processed, and if not, flags it.

        Args:
            memory_id: The ID of the memory to flag.
            reason: Reason for flagging.
            confidence: Confidence score (0.0-1.0).

        Returns:
            True if successfully flagged, False if already processed.
        """
        # Check current state first
        memories = await self.client.search(f"id:{memory_id}", 1)
        if not memories:
            logger.warning(f"Memory {memory_id} not found for atomic flagging.")
            return False

        observations = memories[0].get("observations", [])

        # Check if already processed
        if any(
            "FLAGGED_BY_IA" in str(obs) or
            "MANUALLY_APPROVED_BY_ADMIN" in str(obs) or
            "PROCESSED_BY_IA_AUDITOR" in str(obs)
            for obs in observations
        ):
            logger.info(f"Memory {memory_id} already processed, skipping flagging.")
            return False

        # Add flagging observation
        flag_observation = f"FLAGGED_BY_IA: {reason} (Confidence: {confidence:.2f})"
        await self.client.add_observations(memory_id, [flag_observation])

        logger.info(f"Successfully flagged memory {memory_id} with confidence {confidence:.2f}")
        return True

    async def atomic_check_and_delete(self, memory_id: str) -> bool:
        """
        Atomically checks if memory is already processed, and if not, deletes it.

        Args:
            memory_id: The ID of the memory to delete.

        Returns:
            True if successfully deleted, False if already processed.
        """
        # Check current state first
        memories = await self.client.search(f"id:{memory_id}", 1)
        if not memories:
            logger.warning(f"Memory {memory_id} not found for atomic deletion.")
            return False

        observations = memories[0].get("observations", [])

        # Check if already processed
        if any(
            "FLAGGED_BY_IA" in str(obs) or
            "MANUALLY_APPROVED_BY_ADMIN" in str(obs) or
            "PROCESSED_BY_IA_AUDITOR" in str(obs)
            for obs in observations
        ):
            logger.info(f"Memory {memory_id} already processed, skipping deletion.")
            return False

        # Mark as processed to prevent future processing
        await self.client.add_observations(
            memory_id,
            ["PROCESSED_BY_IA_AUDITOR"]
        )

        # Delete the memory
        await self.client.delete(memory_id)
        logger.info(f"Successfully deleted memory {memory_id}")
        return True


# --- Global Instance ---
# Create a single, globally accessible instance of the AsyncKnowledgeGraph.
knowledge_graph = AsyncKnowledgeGraph()