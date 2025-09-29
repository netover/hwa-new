from __future__ import annotations

import asyncio
import logging

from agno.agent import Agent
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from resync.core.exceptions import (
    AgentError,
    AuditError,
    DatabaseError,
    KnowledgeGraphError,
    NetworkError,
    WebSocketError,
)
from resync.core.fastapi_di import (
    get_agent_manager,
    get_connection_manager,
    get_knowledge_graph,
)
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.interfaces import IAgentManager, IConnectionManager, IKnowledgeGraph

# --- Logging Setup ---
logger = logging.getLogger(__name__)

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
    except Exception as e:
        # Keep a generic handler as a last resort to prevent any issues
        logger.debug("Failed to send error message, unexpected error: %s", e)


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
    except Exception as e:
        logger.error(
            "IA Auditor background task failed unexpectedly: %s", str(e), exc_info=True
        )
        # Still catch general exceptions as a last resort to prevent task from dying


@chat_router.websocket("/ws/{agent_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    agent_id: str,
    agent_manager: IAgentManager = Depends(get_agent_manager),
    connection_manager: IConnectionManager = Depends(get_connection_manager),
    knowledge_graph: IKnowledgeGraph = Depends(get_knowledge_graph),
):
    """
    Handles the WebSocket connection for real-time chat with a specific agent.
    Enhances responses with RAG (Retrieval-Augmented Generation) using the Knowledge Graph.
    """
    await connection_manager.connect(websocket)
    agent: Agent | None = agent_manager.get_agent(agent_id)

    if not agent:
        # If the agent doesn't exist, inform the client and close the connection.
        logger.warning(f"Agent '{agent_id}' not found for WebSocket connection.")
        await websocket.send_json(
            {
                "type": "error",
                "sender": "system",
                "message": f"Agente '{agent_id}' não encontrado.",
            }
        )
        await websocket.close(code=1008)
        await connection_manager.disconnect(websocket)
        return

    try:
        # Initial greeting to confirm connection
        await websocket.send_json(
            {
                "type": "info",
                "sender": "system",
                "message": f"Conectado ao agente: {agent_id}",
            }
        )

        while True:
            # Wait for a message from the client
            data = await websocket.receive_text()
            logger.info(f"Received message for agent '{agent_id}': {data}")

            # Send the user's message back to the UI for display
            await websocket.send_json(
                {"type": "message", "sender": "user", "message": data}
            )

            # --- RAG Enhancement ---
            # Fetch relevant past solutions from the Knowledge Graph
            context = await knowledge_graph.get_relevant_context(data)
            logger.debug(f"Retrieved knowledge graph context: {context[:200]}...")

            # --- Agent Interaction ---
            # Stream the agent's response back to the client chunk by chunk
            # Inject the context into the agent's system prompt via the input
            enhanced_query = f"""
Contexto de soluções anteriores:
{context}

Pergunta do usuário:
{data}
"""
            response_message = ""
            async for chunk in agent.stream(enhanced_query):
                response_message += chunk
                await websocket.send_json(
                    {"type": "stream", "sender": "agent", "message": chunk}
                )

            # Send a final message indicating the stream has ended
            await websocket.send_json(
                {
                    "type": "message",
                    "sender": "agent",
                    "message": response_message,
                    "is_final": True,
                }
            )
            logger.info(f"Agent '{agent_id}' full response: {response_message}")

            # --- Store Interaction in Knowledge Graph ---
            # Log the interaction for continuous learning
            await knowledge_graph.add_conversation(
                user_query=data,
                agent_response=response_message,
                agent_id=agent_id,
                context={  # Refine context to include only relevant, non-sensitive info
                    "agent_name": agent.name,
                    "agent_description": agent.description,
                    "model_used": agent.llm_model,
                }
            ),

            # --- IA Auditor ---
            # Recommendation 3: Run the auditor in a safe background task
            logger.info("Scheduling IA Auditor to run in the background.")
            asyncio.create_task(run_auditor_safely())

    except WebSocketDisconnect:
        # Handle client disconnection gracefully
        logger.info(f"Client disconnected from agent '{agent_id}'.")
    except KnowledgeGraphError as e:
        logger.error(
            f"Knowledge graph error for agent '{agent_id}': {e}", exc_info=True
        )
        await send_error_message(websocket, f"Erro no grafo de conhecimento: {e}")
    except AgentError as e:
        logger.error(f"Agent error for '{agent_id}': {e}", exc_info=True)
        await send_error_message(websocket, f"Erro no agente: {e}")
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout in WebSocket for agent '{agent_id}': {e}", exc_info=True)
        await send_error_message(websocket, "A operação excedeu o tempo limite.")
    except WebSocketError as e:
        logger.error(f"WebSocket error for agent '{agent_id}': {e}", exc_info=True)
        # No need to send message as the WebSocket is likely broken
    except NetworkError as e:
        logger.error(f"Network error for agent '{agent_id}': {e}", exc_info=True)
        await send_error_message(websocket, f"Erro de conexão: {e}")
    except Exception as e:
        # Handle truly unexpected errors during the chat as a last resort
        logger.error(
            f"Unexpected error in WebSocket for agent '{agent_id}': {e}", exc_info=True
        )
        await send_error_message(websocket, f"Ocorreu um erro inesperado: {e}")
    finally:
        # Ensure the connection is cleaned up
        await connection_manager.disconnect(websocket)
