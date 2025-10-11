# resync/core/knowledge_graph.py
from typing import Any, Dict, List, Optional

from neo4j import AsyncGraphDatabase
from neo4j import exceptions as neo4j_exceptions

from resync.core.exceptions import KnowledgeGraphError
from resync.settings import settings
from resync.core.structured_logger import get_logger

logger = get_logger(__name__)


class AsyncKnowledgeGraph:
    """
    Interface assíncrona para interagir com o Knowledge Graph (Neo4j).
    Utiliza parâmetros de query para prevenir injeção de Cypher.
    """

    def __init__(self):
        try:
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
            )
            logger.info("neo4j_driver_initialized")
        except (neo4j_exceptions.ServiceUnavailable, neo4j_exceptions.AuthError) as e:
            logger.critical(
                "failed_to_initialize_neo4j_driver", error=str(e), exc_info=True
            )
            raise KnowledgeGraphError("Could not connect to Neo4j database.") from e

    @property
    def client(self) -> Any:
        """Gets the underlying Neo4j driver client."""
        return self.driver

    async def close(self):
        """Fecha a conexão com o driver do Neo4j."""
        if self.driver:
            await self.driver.close()
            logger.info("neo4j_driver_closed")

    async def add_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """Adds a piece of content (e.g., a document chunk) to the knowledge graph."""
        query = """
        CREATE (n:Content {
            content: $content,
            metadata: $metadata,
            created_at: datetime()
        })
        RETURN id(n) as node_id
        """
        params = {"content": content, "metadata": metadata}

        try:
            async with self.driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                return str(record["node_id"])
        except neo4j_exceptions.Neo4jError as e:
            logger.error("error_adding_content_to_kg", error=str(e), exc_info=True)
            raise KnowledgeGraphError(
                "Failed to store content in knowledge graph."
            ) from e

    async def get_relevant_context(self, user_query: str, top_k: int = 10) -> str:
        """
        Busca contexto relevante no grafo usando busca vetorial de forma segura.

        Args:
            user_query: A query do usuário (sanitizada).
            top_k: O número de resultados a serem retornados.

        Returns:
            Uma string contendo o contexto relevante.
        """
        # SEGURO: A query Cypher usa um placeholder ($query_text) para o parâmetro.
        # O input do usuário é passado separadamente no dicionário de parâmetros.
        query = """
        CALL db.index.vector.queryNodes('embedding_index', $top_k, $query_text)
        YIELD node, score
        RETURN node.text AS text, score
        ORDER BY score DESC
        """
        params = {"query_text": user_query, "top_k": top_k}

        try:
            async with self.driver.session() as session:
                result = await session.run(query, params)
                records = await result.data()
                return "\n".join(
                    [
                        f"- {record['text']} (Score: {record['score']:.2f})"
                        for record in records
                    ]
                )
        except neo4j_exceptions.Neo4jError as e:
            logger.error(
                "error_fetching_relevant_context_from_kg", error=str(e), exc_info=True
            )
            raise KnowledgeGraphError(
                "Failed to query knowledge graph for context."
            ) from e

    async def add_conversation(
        self,
        user_query: str,
        agent_response: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Stores a conversation between a user and an agent."""
        query = """
        CREATE (c:Conversation {
            user_query: $user_query,
            agent_response: $agent_response,
            agent_id: $agent_id,
            model_used: $model_used,
            timestamp: datetime()
        })
        RETURN id(c) as conversation_id
        """
        params = {
            "user_query": user_query,
            "agent_response": agent_response,
            "agent_id": agent_id,
            "model_used": (
                context.get("model_used", "unknown") if context else "unknown"
            ),
        }

        try:
            async with self.driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                logger.debug("added_conversation_for_agent_to_kg", agent_id=agent_id)
                return str(record["conversation_id"])
        except neo4j_exceptions.Neo4jError as e:
            logger.error("error_adding_conversation_to_kg", error=str(e), exc_info=True)
            raise KnowledgeGraphError(
                "Failed to store conversation in knowledge graph."
            ) from e

    async def search_similar_issues(
        self, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Searches the knowledge graph for similar past issues and solutions."""
        # Simple implementation - could be enhanced with vector search
        cypher_query = """
        MATCH (c:Conversation)
        WHERE c.user_query CONTAINS $query OR c.agent_response CONTAINS $query
        RETURN c.user_query as user_query, c.agent_response as agent_response,
               c.agent_id as agent_id, c.timestamp as timestamp
        ORDER BY c.timestamp DESC
        LIMIT $limit
        """
        params = {"query": query, "limit": limit}

        try:
            async with self.driver.session() as session:
                result = await session.run(cypher_query, params)
                records = await result.data()
                return records
        except neo4j_exceptions.Neo4jError as e:
            logger.error("error_searching_similar_issues", error=str(e), exc_info=True)
            raise KnowledgeGraphError("Failed to search similar issues.") from e

    async def search_conversations(
        self,
        query: str = "type:conversation",
        limit: int = 100,
        _sort_by: str = "created_at",
        _sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """Optimized search method for conversations."""
        cypher_query = """
        MATCH (c:Conversation)
        RETURN c.user_query as user_query, c.agent_response as agent_response,
               c.agent_id as agent_id, c.model_used as model_used,
               c.timestamp as timestamp
        ORDER BY c.timestamp DESC
        LIMIT $limit
        """
        params = {"limit": limit}

        try:
            async with self.driver.session() as session:
                result = await session.run(cypher_query, params)
                records = await result.data()
                return records
        except neo4j_exceptions.Neo4jError as e:
            logger.error("error_searching_conversations", error=str(e), exc_info=True)
            raise KnowledgeGraphError("Failed to search conversations.") from e

    async def add_solution_feedback(
        self, memory_id: str, feedback: str, rating: int
    ) -> None:
        """Adds user feedback to a specific memory."""
        query = """
        MATCH (c:Conversation) WHERE id(c) = $memory_id
        SET c.feedback = $feedback, c.rating = $rating
        """
        params = {"memory_id": int(memory_id), "feedback": feedback, "rating": rating}

        try:
            async with self.driver.session() as session:
                await session.run(query, params)
        except neo4j_exceptions.Neo4jError as e:
            logger.error("error_adding_solution_feedback", error=str(e), exc_info=True)
            raise KnowledgeGraphError("Failed to add solution feedback.") from e

    async def get_all_recent_conversations(
        self, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieves all recent conversation-type memories for auditing."""
        return await self.search_conversations(limit=limit)

    async def is_memory_flagged(self, memory_id: str) -> bool:
        """Checks if a memory has been flagged by the IA Auditor."""
        query = "MATCH (c:Conversation) WHERE id(c) = $memory_id RETURN c.is_flagged AS flagged"
        params = {"memory_id": int(memory_id)}
        try:
            async with self.driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                return record["flagged"] if record else False
        except neo4j_exceptions.Neo4jError as e:
            logger.error(
                "error_checking_if_memory_is_flagged", error=str(e), exc_info=True
            )
            raise KnowledgeGraphError("Failed to check memory flag status.") from e

    async def is_memory_approved(self, memory_id: str) -> bool:
        """Checks if a memory has been approved by an admin."""
        query = "MATCH (c:Conversation) WHERE id(c) = $memory_id RETURN c.is_approved AS approved"
        params = {"memory_id": int(memory_id)}
        try:
            async with self.driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                return record["approved"] if record else False
        except neo4j_exceptions.Neo4jError as e:
            logger.error(
                "error_checking_if_memory_is_approved", error=str(e), exc_info=True
            )
            raise KnowledgeGraphError("Failed to check memory approval status.") from e

    async def delete_memory(self, memory_id: str) -> None:
        """Deletes a memory from the knowledge graph."""
        query = "MATCH (c:Conversation) WHERE id(c) = $memory_id DELETE c"
        params = {"memory_id": int(memory_id)}

        try:
            async with self.driver.session() as session:
                await session.run(query, params)
        except neo4j_exceptions.Neo4jError as e:
            logger.error("error_deleting_memory", error=str(e), exc_info=True)
            raise KnowledgeGraphError("Failed to delete memory.") from e

    async def add_observations(self, memory_id: str, observations: List[str]) -> None:
        """Adds observations to a memory in the knowledge graph."""
        query = """
        MATCH (c:Conversation) WHERE id(c) = $memory_id
        SET c.observations = $observations
        """
        params = {"memory_id": int(memory_id), "observations": observations}

        try:
            async with self.driver.session() as session:
                await session.run(query, params)
        except neo4j_exceptions.Neo4jError as e:
            logger.error("error_adding_observations", error=str(e), exc_info=True)
            raise KnowledgeGraphError("Failed to add observations.") from e

    async def is_memory_already_processed(self, memory_id: str) -> bool:
        """Atomically checks if a memory has already been processed."""
        query = """
        MATCH (c:Conversation) WHERE id(c) = $memory_id
        RETURN c.processed AS processed
        """
        params = {"memory_id": int(memory_id)}

        try:
            async with self.driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                return record["processed"] if record else False
        except neo4j_exceptions.Neo4jError as e:
            logger.error(
                "error_checking_if_memory_is_processed", error=str(e), exc_info=True
            )
            raise KnowledgeGraphError("Failed to check memory processed status.") from e

    async def atomic_check_and_flag(
        self, memory_id: str, reason: str, confidence: float
    ) -> bool:
        """Atomically checks if memory is already processed, and if not, flags it."""
        query = """
        MATCH (c:Conversation) WHERE id(c) = $memory_id
        SET c.is_flagged = true, c.flag_reason = $reason,
            c.flag_confidence = $confidence, c.processed = true
        RETURN c.processed AS was_already_processed
        """
        params = {
            "memory_id": int(memory_id),
            "reason": reason,
            "confidence": confidence,
        }

        try:
            async with self.driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                # Return True if it was NOT already processed (i.e., we just processed it)
                return not record["was_already_processed"]
        except neo4j_exceptions.Neo4jError as e:
            logger.error("error_in_atomic_check_and_flag", error=str(e), exc_info=True)
            raise KnowledgeGraphError(
                "Failed to atomically check and flag memory."
            ) from e

    async def atomic_check_and_delete(self, memory_id: str) -> bool:
        """Atomically checks if memory is already processed, and if not, deletes it."""
        query = """
        MATCH (c:Conversation) WHERE id(c) = $memory_id
        SET c.processed = true
        WITH c, c.processed AS was_already_processed
        DELETE c
        RETURN was_already_processed
        """
        params = {"memory_id": int(memory_id)}

        try:
            async with self.driver.session() as session:
                result = await session.run(query, params)
                record = await result.single()
                # Return True if it was NOT already processed (i.e., we just processed it)
                return not record["was_already_processed"]
        except neo4j_exceptions.Neo4jError as e:
            logger.error(
                "error_in_atomic_check_and_delete", error=str(e), exc_info=True
            )
            raise KnowledgeGraphError(
                "Failed to atomically check and delete memory."
            ) from e
