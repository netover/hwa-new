"""
Knowledge Graph Integration for Resync using Neo4j.

This module implements a persistent knowledge graph using Neo4j to model and
query the complex relationships within the TWS environment and user interactions.
"""

import logging
import httpx
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from neo4j import AsyncGraphDatabase, AsyncDriver

from resync.core.exceptions import (
    DatabaseError,
    KnowledgeGraphError,
    LLMError,
    NetworkError,
)

# Import settings
from ..settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)


class AsyncKnowledgeGraph:
    """
    A wrapper around a Neo4j database to manage a persistent knowledge graph for the Resync system.

    The knowledge graph stores:
    - Conversations between users and AI agents
    - TWS entities like Jobs, Jobstreams, and Workstations
    - Relationships between all these entities

    This enables RAG (Retrieval-Augmented Generation) to become more intelligent over time.
    """

    _driver: Optional[AsyncDriver] = None

    def __init__(self, settings_module: Any = settings):
        """
        Initialize the AsyncKnowledgeGraph with Neo4j connection settings.

        Args:
            settings_module: The settings module to use (default: global settings).
        """
        self.settings = settings_module
        self.uri = self.settings.NEO4J_URI
        self.auth = (self.settings.NEO4J_USER, self.settings.NEO4J_PASSWORD)
        logger.info(
            f"AsyncKnowledgeGraph configured for Neo4j instance at {self.uri}"
        )

    def _get_driver(self) -> AsyncDriver:
        """Get or create the Neo4j async driver instance."""
        if self._driver is None or self._driver._closed:
            logger.info("Initializing new Neo4j driver.")
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=self.auth)
        return self._driver

    async def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self._driver and not self._driver._closed:
            await self.driver.close()
            logger.info("Neo4j driver closed.")

    @property
    def driver(self) -> AsyncDriver:
        """Property to access the driver, ensuring it's initialized."""
        return self._get_driver()

    async def add_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Adds a piece of content (e.g., a document chunk) to the knowledge graph.

        Args:
            content: The text content to store.
            metadata: Additional metadata about the content (e.g., source file, chunk index).

        Returns:
            The unique ID of the stored memory.
        """
        query = """
        CREATE (c:DocumentChunk {
            content: $content,
            source_file: $metadata.source_file,
            chunk_index: $metadata.chunk_index,
            total_chunks: $metadata.total_chunks,
            uuid: randomUUID()
        })
        RETURN c.uuid AS uuid
        """
        async with self.driver.session() as session:
            result = await session.run(query, content=content, metadata=metadata)
            record = await result.single()
            return str(record["uuid"]) if record else ""

    async def add_conversation(
        self,
        user_query: str,
        agent_response: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
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
        query = """
        CREATE (c:Conversation {
            user_query: $user_query,
            agent_response: $agent_response,
            agent_id: $agent_id,
            context: $context,
            uuid: randomUUID()
        })
        RETURN c.uuid AS uuid
        """
        async with self.driver.session() as session:
            result = await session.run(
                query, user_query=user_query, agent_response=agent_response, agent_id=agent_id, context=context or {}
            )
            record = await result.single()
            return str(record["uuid"]) if record else ""

    async def search_similar_issues(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Searches the knowledge graph for similar past issues and solutions.

        Args:
            query: The current problem or question to match against.
            limit: Maximum number of similar memories to return.

        Returns:
            A list of relevant past memories with their metadata.
        """
        # This would use the Neo4j Vector Index
        # Placeholder implementation
        logger.warning("search_similar_issues with vector index is not yet implemented.")
        return []

    async def search_conversations(
        self,
        query: str = "type:conversation",
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
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
        # This is a placeholder. A real implementation would parse the query.
        cypher_query = f"""
        MATCH (c:Conversation)
        RETURN c
        ORDER BY c.{sort_by} {sort_order.upper()}
        LIMIT {limit}
        """
        async with self.driver.session() as session:
            result = await session.run(cypher_query)
            records = await result.data()
            return [record['c'] for record in records]

    async def add_solution_feedback(
        self, memory_id: str, feedback: str, rating: int
    ) -> None:
        """
        Adds user feedback to a specific memory in the knowledge graph.

        Args:
            memory_id: The ID of the memory to add feedback to.
            feedback: The user's textual feedback (e.g., 'This helped!', 'Not useful').
            rating: A numerical rating from 1 to 5.
        """
        query = """
        MATCH (c:Conversation {uuid: $memory_id})
        SET c.feedback = $feedback, c.rating = $rating
        """
        async with self.driver.session() as session:
            await session.run(query, memory_id=memory_id, feedback=feedback, rating=rating)
        logger.info(
            f"Added feedback to conversation {memory_id}: {rating}/5 - {feedback}"
        )

    async def get_all_recent_conversations(
        self, limit: int = 100
    ) -> List[Dict[str, Any]]:
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
            sort_order="desc",
        )

    async def get_relevant_context(self, user_query: str) -> str:
        """
        Retrieves a structured text summary of relevant knowledge from the graph to use in RAG.

        Args:
            user_query: The current user query.

        Returns:
            A formatted string of relevant past solutions and context.
        """
        graph_schema = """
        Node labels are: `Job`, `Jobstream`, `Workstation`, `User`, `Execution`, `Conversation`, `Message`, `DocumentChunk`.
        Relationship types are: `CONTAINS`, `DEPENDS_ON`, `EXECUTED_ON`, `INSTANCE_OF`, `INTERACTED_IN`, `HAS_MESSAGE`, `MENTIONS`, `REFERENCES`.
        `Job` properties: `name`, `type`.
        `Execution` properties: `status`, `startTime`.
        `Workstation` properties: `name`, `type`.
        `Conversation` properties: `user_query`, `agent_response`.
        """

        prompt = f"""
        You are an expert Neo4j Cypher query translator. Given the following graph schema and a user question,
        generate a Cypher query to answer the question. Return ONLY the Cypher query, with no explanations.

        Schema:
        {graph_schema}

        Question: "{user_query}"

        Cypher Query:
        """

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.settings.LLM_ENDPOINT,
                    json={
                        "model": self.settings.AGENT_MODEL_NAME,
                        "prompt": prompt,
                        "stream": False,
                    },
                    headers={"Authorization": f"Bearer {self.settings.LLM_API_KEY}"},
                    timeout=30.0,
                )
                response.raise_for_status()
                
                # Handle different API response structures (OpenAI vs Ollama)
                response_data = response.json()
                if "response" in response_data:  # Ollama
                    cypher_query = str(response_data["response"])
                elif "choices" in response_data and response_data["choices"] and "text" in response_data["choices"][0]:  # OpenAI (legacy completion)
                    cypher_query = str(response_data["choices"][0]["text"])
                elif "choices" in response_data and response_data["choices"]:  # OpenAI
                    cypher_query = response_data["choices"][0]["message"]["content"]
                else:
                    raise ValueError("Unsupported LLM API response format")

            logger.info(f"Generated Cypher query: {cypher_query}")

            # --- Sanitize and validate the generated Cypher ---
            # Extract from markdown code block if present
            if "```" in cypher_query:
                cypher_query = cypher_query.split("```")[1].replace("cypher", "").strip()

            # Basic validation to prevent execution of garbage
            if not cypher_query.strip().upper().startswith(("MATCH", "CREATE", "MERGE", "CALL")):
                raise ValueError(f"Generated query is not a valid Cypher query: {cypher_query}")

            # Execute the generated query
            async with self.driver.session() as session:
                result = await session.run(cypher_query)
                records = await result.data()

            # Format results for RAG context
            return str(records) if records else "No relevant information found in the knowledge graph."

        except httpx.RequestError as e:
            logger.error("Network error during Text-to-Cypher request: %s", e, exc_info=True)
            raise NetworkError("Failed to connect to the LLM service for Cypher generation") from e
        except httpx.HTTPStatusError as e:
            logger.error("LLM API returned an error status during Text-to-Cypher: %s", e.response.text, exc_info=True)
            raise LLMError(f"LLM API failed with status {e.response.status_code}") from e
        except ValueError as e:
            # This can be raised by our custom validation or JSON parsing
            logger.error("Validation or data error during Text-to-Cypher: %s", e, exc_info=True)
            raise KnowledgeGraphError("Failed to process or validate the generated Cypher query") from e
        except (DatabaseError, KnowledgeGraphError) as e:
            # Re-raise known database or graph errors
            logger.error("Database error executing generated Cypher query: %s", e, exc_info=True)
            raise
        except Exception as e:
            # Catch any other unexpected errors
            logger.critical(
                "An unexpected critical error occurred during Text-to-Cypher or execution.",
                exc_info=True
            )
            raise KnowledgeGraphError("An unexpected error occurred while retrieving context") from e

    # --- Additional methods for race condition fixes ---

    async def is_memory_flagged(self, memory_id: str) -> bool:
        """
        Checks if a memory has been flagged by the IA Auditor.

        Args:
            memory_id: The ID of the memory to check.

        Returns:
            True if the memory is flagged, False otherwise.
        """
        # Placeholder implementation
        logger.warning("is_memory_flagged is not yet implemented.")
        return False

    async def is_memory_approved(self, memory_id: str) -> bool:
        """
        Checks if a memory has been approved by an admin.

        Args:
            memory_id: The ID of the memory to check.

        Returns:
            True if the memory is approved, False otherwise.
        """
        # Placeholder implementation
        logger.warning("is_memory_approved is not yet implemented.")
        return False

    async def delete_memory(self, memory_id: str) -> None:
        """
        Deletes a memory from the knowledge graph.

        Args:
            memory_id: The ID of the memory to delete.
        """
        query = "MATCH (n {uuid: $memory_id}) DETACH DELETE n"
        async with self.driver.session() as session:
            await session.run(query, memory_id=memory_id)
        logger.info(
            f"Deleted node with uuid {memory_id} from knowledge graph"
        )

    async def add_observations(self, memory_id: str, observations: List[str]) -> None:
        """
        Adds observations to a memory in the knowledge graph.

        Args:
            memory_id: The ID of the memory to add observations to.
            observations: List of observation strings to add.
        """
        # This would likely involve creating new nodes or updating properties.
        # Placeholder implementation
        logger.warning("add_observations is not yet implemented.")
        logger.info(
            f"Received {len(observations)} observations for memory {memory_id}"
        )

    # --- Atomic Operations for Race Condition Prevention ---

    async def is_memory_already_processed(self, memory_id: str) -> bool:
        """
        Atomically checks if a memory has already been processed (flagged or approved).

        Args:
            memory_id: The ID of the memory to check.

        Returns:
            True if already processed (flagged or approved), False otherwise.
        """
        # Placeholder implementation
        logger.warning("is_memory_already_processed is not yet implemented.")
        return False

    async def atomic_check_and_flag(
        self, memory_id: str, reason: str, confidence: float
    ) -> bool:
        """
        Atomically checks if memory is already processed, and if not, flags it.

        Args:
            memory_id: The ID of the memory to flag.
            reason: Reason for flagging.
            confidence: Confidence score (0.0-1.0).

        Returns:
            True if successfully flagged, False if already processed.
        """
        # This would need a transactional Cypher query (using MERGE or transactions)
        # Placeholder implementation
        logger.warning("atomic_check_and_flag is not yet implemented.")
        return False

    async def atomic_check_and_delete(self, memory_id: str) -> bool:
        """
        Atomically checks if memory is already processed, and if not, deletes it.

        Args:
            memory_id: The ID of the memory to delete.

        Returns:
            True if successfully deleted, False if already processed.
        """
        # This would need a transactional Cypher query
        # Placeholder implementation
        logger.warning("atomic_check_and_delete is not yet implemented.")
        return False


# Factory function for creating AsyncKnowledgeGraph instances
def create_knowledge_graph(settings_module: Any = settings) -> AsyncKnowledgeGraph:
    """Create and return a new AsyncKnowledgeGraph instance."""
    return AsyncKnowledgeGraph(settings_module=settings_module)