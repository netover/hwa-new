from __future__ import annotations

import asyncio
import time
import logging

from agno.agent import Agent
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer

from resync.core.exceptions import (
    AgentError,
    AgentExecutionError,
    AuditError,
    ConfigurationError,
    DatabaseError,
    KnowledgeGraphError,
    LLMError,
    ToolExecutionError,
    WebSocketError,
)
from resync.core.fastapi_di import (
    get_agent_manager,
    get_connection_manager,
    get_knowledge_graph,
)
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.security import sanitize_input, SafeAgentID
from resync.core.interfaces import IAgentManager, IConnectionManager, IKnowledgeGraph
from resync.security.oauth2 import verify_oauth2_token

# --- Logging Setup ---
logger = logging.getLogger(__name__)

from resync.core.rate_limiter import websocket_rate_limit

# --- APIRouter Initialization ---
chat_router = APIRouter()


async def send_error_message(websocket: WebSocket, message: str) -> None:
    """
    Helper function to send error messages to the client.
    Handles exceptions if the WebSocket connection is already closed.
    """
    try:
        await websocket.send_json(
            {
                "type": "error",
                "sender": "system",
                "message": message,
            }
        )
    except WebSocketDisconnect:
        logger.debug("Failed to send error message, WebSocket disconnected.")
    except RuntimeError as e:
        # This typically happens when the WebSocket is already closed
        logger.debug("Failed to send error message, WebSocket runtime error: %s", e)
    except ConnectionError as e:
        logger.debug("Failed to send error message, connection error: %s", e)
    except Exception:
        # Last resort to prevent the application from crashing if sending fails.
        logger.warning(
            "Failed to send error message due to an unexpected error.", exc_info=True
        )


async def run_auditor_safely():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except asyncio.TimeoutError:
        logger.error("IA Auditor timed out during execution.", exc_info=True)
    except KnowledgeGraphError:
        logger.error("IA Auditor encountered a knowledge graph error.", exc_info=True)
    except DatabaseError:
        logger.error("IA Auditor encountered a database error.", exc_info=True)
    except AuditError:
        logger.error("IA Auditor encountered an audit-specific error.", exc_info=True)
    except Exception:
        logger.critical(
            "IA Auditor background task failed with an unhandled exception.",
            exc_info=True,
        )


async def _get_enhanced_query(
    knowledge_graph: IKnowledgeGraph, sanitized_data: str, original_data: str
) -> str:
    """Retrieves RAG context and constructs the enhanced query for the agent."""
    context = await knowledge_graph.get_relevant_context(sanitized_data)
    logger.debug(f"Retrieved knowledge graph context: {context[:200]}...")
    return f"""
Contexto de soluções anteriores:
{context}

Pergunta do usuário:
{original_data}
"""


async def _stream_agent_response(
    websocket: WebSocket, agent: Agent, query: str
) -> str:
    """Streams the agent's response to the WebSocket and returns the full message."""
    response_message = ""
    async for chunk in agent.stream(query):
        response_message += chunk
        await websocket.send_json(
            {"type": "stream", "sender": "agent", "message": chunk}
        )
    return response_message


async def _finalize_and_store_interaction(
    websocket: WebSocket,
    knowledge_graph: IKnowledgeGraph,
    agent: Agent,
    agent_id: str,
    sanitized_query: str,
    full_response: str,
):
    """Sends the final message, stores the conversation, and schedules the auditor."""
    # Send a final message indicating the stream has ended
    await websocket.send_json(
        {
            "type": "message",
            "sender": "agent",
            "message": full_response,
            "is_final": True,
        }
    )
    logger.info(f"Agent '{agent_id}' full response: {full_response}")

    # Store the interaction in the Knowledge Graph
    await knowledge_graph.add_conversation(
        user_query=sanitized_query,
        agent_response=full_response,
        agent_id=agent_id,
        context={
            "agent_name": agent.name,
            "agent_description": agent.description,
            "model_used": agent.llm_model,
        },
    )

    # Schedule the IA Auditor to run in the background
    logger.info("Scheduling IA Auditor to run in the background.")
    asyncio.create_task(run_auditor_safely())


async def _handle_agent_interaction(
    websocket: WebSocket,
    agent: Agent,
    agent_id: str,
    knowledge_graph: IKnowledgeGraph,
    data: str,
) -> None:
    """Handles the core logic of agent interaction, RAG, and auditing."""
    sanitized_data = sanitize_input(data)
    # Send the user's message back to the UI for display
    await websocket.send_json({"type": "message", "sender": "user", "message": sanitized_data})

    # 1. Get context and create the enhanced query for the agent
    enhanced_query = await _get_enhanced_query(knowledge_graph, sanitized_data, data)

    # 2. Stream the agent's response to the client and get the full response
    full_response = await _stream_agent_response(websocket, agent, enhanced_query)

    # 3. Finalize the interaction: send final message, store, and audit
    await _finalize_and_store_interaction(
        websocket=websocket,
        knowledge_graph=knowledge_graph,
        agent=agent,
        agent_id=agent_id,
        sanitized_query=sanitized_data,
        full_response=full_response,
    )


@chat_router.websocket("/ws/{agent_id}")
@websocket_rate_limit
async def websocket_endpoint(
    websocket: WebSocket,
    agent_id: SafeAgentID,
    agent_manager: IAgentManager = Depends(get_agent_manager),
    connection_manager: IConnectionManager = Depends(get_connection_manager),
    knowledge_graph: IKnowledgeGraph = Depends(get_knowledge_graph),
):
    # First, accept the WebSocket connection to establish it
    await websocket.accept()
    
    # For now, we'll allow access without authentication since we're using email-based session
    # In a real implementation, we would validate session/cookie information
    # For this implementation, we'll just log the access for auditing
    
    logger.info(f"WebSocket connection established for agent {agent_id}")
    """
    Handles the WebSocket connection for real-time chat with a specific agent.
    Enhances responses with RAG (Retrieval-Augmented Generation) using the Knowledge Graph.
    """
    await connection_manager.connect(websocket)
    agent: Agent | None = await agent_manager.get_agent(agent_id)

    if not agent:
        logger.warning(f"Agent '{agent_id}' not found for WebSocket connection.")
        await send_error_message(websocket, f"Agente '{agent_id}' não encontrado.")
        await websocket.close(code=1008)
        await connection_manager.disconnect(websocket)
        return

    try:
        await websocket.send_json(
            {
                "type": "info",
                "sender": "system",
                "message": f"Conectado ao agente: {agent_id}",
            }
        )

        while True:
            raw_data = await websocket.receive_text()
            logger.info(f"Received message for agent '{agent_id}': {raw_data}")
            # A sanitização ocorre dentro de _handle_agent_interaction
            await _handle_agent_interaction(
                websocket, agent, agent_id, knowledge_graph, raw_data
            )

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from agent '{agent_id}'.")
    except ConfigurationError as e:
        logger.error(f"Configuration error for agent '{agent_id}': {e}", exc_info=True)
        await send_error_message(
            websocket, f"Erro de configuração do servidor: {e}"
        )
    except KnowledgeGraphError as e:
        logger.error(
            f"Knowledge graph error for agent '{agent_id}': {e}", exc_info=True
        )
        await send_error_message(websocket, f"Erro no grafo de conhecimento: {e}")
    except ToolExecutionError as e:
        logger.error(f"Tool execution error for agent '{agent_id}': {e}", exc_info=True)
        await send_error_message(websocket, f"Erro ao executar uma ferramenta interna: {e}")
    except AgentExecutionError as e:
        logger.error(
            f"Agent execution error for agent '{agent_id}': {e}", exc_info=True
        )
        await send_error_message(websocket, f"Erro na execução do agente: {e}")
    except LLMError as e:
        logger.error(f"LLM communication error for agent '{agent_id}': {e}", exc_info=True)
        await send_error_message(websocket, f"Erro de comunicação com o modelo de IA: {e}")
    except AgentError as e:
        logger.error(f"Agent error for '{agent_id}': {e}", exc_info=True)
        await send_error_message(websocket, f"Erro no agente: {e}")
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout in WebSocket for agent '{agent_id}': {e}", exc_info=True)
        await send_error_message(websocket, "A operação excedeu o tempo limite.")
    except Exception:
        # A critical, unhandled error occurred. Log it for immediate investigation.
        logger.critical(
            "Unexpected critical error in WebSocket for agent '%s'",
            agent_id,
            exc_info=True,
        )
        await send_error_message(websocket, "Ocorreu um erro inesperado no servidor.")
    finally:
        # Ensure the connection is cleaned up
        await connection_manager.disconnect(websocket)
