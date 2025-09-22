from __future__ import annotations

import logging

from agno.client import Client
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from resync.core.agent_manager import agent_manager
from resync.core.connection_manager import connection_manager
from resync.core.knowledge_graph import knowledge_graph

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- APIRouter Initialization ---
chat_router = APIRouter()


@chat_router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """
    Handles the WebSocket connection for real-time chat with a specific agent.
    Enhances responses with RAG (Retrieval-Augmented Generation) using the Knowledge Graph.
    """
    await connection_manager.connect(websocket)
    agent: Client | None = agent_manager.get_agent(agent_id)

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
        connection_manager.disconnect(websocket)
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
            context = knowledge_graph.get_relevant_context(data)
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
            knowledge_graph.add_conversation(
                user_query=data,
                agent_response=response_message,
                agent_id=agent_id,
                context={"agent_config": agent_manager.get_agent(agent_id).__dict__ if agent_manager.get_agent(agent_id) else "N/A"}
            )

    except WebSocketDisconnect:
        # Handle client disconnection gracefully
        logger.info(f"Client disconnected from agent '{agent_id}'.")
    except Exception as e:
        # Handle unexpected errors during the chat
        logger.error(f"Error in WebSocket for agent '{agent_id}': {e}", exc_info=True)
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "sender": "system",
                    "message": f"Ocorreu um erro inesperado: {e}",
                }
            )
        except Exception:
            # If sending fails, the connection is likely already dead.
            pass
    finally:
        # Ensure the connection is cleaned up
        connection_manager.disconnect(websocket)
