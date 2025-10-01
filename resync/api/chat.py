from __future__ import annotations

import asyncio
import logging

from agno.agent import Agent
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

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


async def _handle_agent_interaction(
    websocket: WebSocket,
    agent: Agent,
    agent_id: str,
    knowledge_graph: IKnowledgeGraph,
    data: str,
) -> None:
    """Handles the core logic of agent interaction, RAG, and auditing."""
    # Send the user's message back to the UI for display
    await websocket.send_json({"type": "message", "sender": "user", "message": data})

    # --- RAG Enhancement ---
    context = await knowledge_graph.get_relevant_context(data)
    logger.debug(f"Retrieved knowledge graph context: {context[:200]}...")

    # --- Agent Interaction ---
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
    await knowledge_graph.add_conversation(
        user_query=data,
        agent_response=response_message,
        agent_id=agent_id,
        context={
            "agent_name": agent.name,
            "agent_description": agent.description,
            "model_used": agent.llm_model,
        },
    )

    # --- IA Auditor ---
    logger.info("Scheduling IA Auditor to run in the background.")
    asyncio.create_task(run_auditor_safely())


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
            data = await websocket.receive_text()
            logger.info(f"Received message for agent '{agent_id}': {data}")
            await _handle_agent_interaction(
                websocket, agent, agent_id, knowledge_graph, data
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
