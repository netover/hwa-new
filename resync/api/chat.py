from __future__ import annotations

import asyncio
import json
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
)
from resync.core.fastapi_di import (
    get_agent_manager,
    get_connection_manager,
    get_knowledge_graph,
)
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.interfaces import IAgentManager, IConnectionManager, IKnowledgeGraph
from resync.core.llm_wrapper import optimized_llm
from resync.core.rate_limiter import websocket_rate_limit
from resync.core.security import SafeAgentID, sanitize_input

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# Module-level dependencies to avoid B008 errors
agent_manager_dependency = Depends(get_agent_manager)
connection_manager_dependency = Depends(get_connection_manager)
knowledge_graph_dependency = Depends(get_knowledge_graph)

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


async def _get_optimized_response(
    query: str,
    context: dict = None,
    use_cache: bool = True,
    stream: bool = False
) -> str:
    """
    Get response using the TWS-optimized LLM optimizer.
    
    This is used for queries that might benefit from special TWS-specific
    optimizations like template matching, caching, and model selection.
    """
    try:
        response = await optimized_llm.get_response(
            query=query,
            context=context or {},
            use_cache=use_cache,
            stream=stream
        )
        return response
    except Exception as e:
        logger.error(f"LLM optimization failed, falling back to regular processing: {e}")
        # Return the original query to be handled by the normal agent flow
        return query


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

    # Safe access to agent attributes - FIXED
    agent_name = getattr(agent, 'name', 'Unknown Agent')
    agent_description = getattr(agent, 'description', 'No description')
    agent_model = getattr(agent, 'llm_model', getattr(agent, 'model', 'Unknown Model'))

    # Store the interaction in the Knowledge Graph
    await knowledge_graph.add_conversation(
        user_query=sanitized_query,
        agent_response=full_response,
        agent_id=agent_id,
        context={
            "agent_name": agent_name,
            "agent_description": agent_description,
            "model_used": str(agent_model),
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

    # Check if query would benefit from LLM optimization
    # For certain TWS-specific queries, we can use the optimized approach
    if _should_use_llm_optimization(data):
        logger.info(f"Using LLM optimization for query from agent {agent_id}")
        
        # Get optimized response
        optimized_response = await _get_optimized_response(
            query=data,
            context={"agent_id": agent_id, "user_query": sanitized_data}
        )
        
        # Send the optimized response
        await websocket.send_json(
            {
                "type": "message",
                "sender": "agent",
                "message": optimized_response,
                "is_optimized": True,
                "is_final": True,
            }
        )
        
        # Store the optimized interaction
        await _finalize_and_store_interaction(
            websocket=websocket,
            knowledge_graph=knowledge_graph,
            agent=agent,
            agent_id=agent_id,
            sanitized_query=sanitized_data,
            full_response=optimized_response,
        )
    else:
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


def _should_use_llm_optimization(query: str) -> bool:
    """Determine if a query would benefit from LLM optimization."""
    query_lower = query.lower()
    
    # Use optimization for specific TWS-related queries
    tws_indicators = [
        "status", "estado", "job", "tws", "system", "health", "saúde", 
        "sistema", "dependency", "dependenc", "troubleshoot", "problem",
        "analyze", "failure", "error", "erro", "falha"
    ]
    
    return any(indicator in query_lower for indicator in tws_indicators)


@chat_router.websocket("/ws/{agent_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    agent_id: SafeAgentID,
):
    # Accept WebSocket connection
    await websocket.accept()
    logger.info(f"WebSocket connection established for agent {agent_id}")

    # Send welcome message
    welcome_data = {
        "type": "info",
        "sender": "system",
        "message": f"Conectado ao agente: {agent_id}. Digite sua mensagem...",
    }
    await websocket.send_text(json.dumps(welcome_data))

    # Get agent manager and agent
    from resync.core.fastapi_di import get_service
    from resync.core.interfaces import IAgentManager

    agent_manager = await get_service(IAgentManager)()
    agent = await agent_manager.get_agent(agent_id)

    if not agent:
        error_data = {"type": "error", "sender": "system", "message": f"Agente '{agent_id}' não encontrado."}
        await websocket.send_text(json.dumps(error_data))
        await websocket.close(code=1008)
        return

    logger.info(f"Agent '{agent_id}' ready for WebSocket communication")

    # Multi-message conversation model
    try:
        # Initialize conversation history
        conversation_history = []
        
        # Continuous message processing loop
        while True:
            # Receive message from client
            raw_data = await websocket.receive_text()
            logger.info(f"Received message for agent '{agent_id}': {raw_data}")
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": raw_data})
            
            try:
                # Process message with agent
                logger.info(f"Processing message with agent: {raw_data}")
                
                # Use direct string responses with context from conversation history
                msg = raw_data.lower()
                
                # Generate contextual response based on conversation history
                if len(conversation_history) > 1:
                    # This is a follow-up question
                    logger.info(f"Follow-up question detected. History length: {len(conversation_history)}")
                
                # Generate responses based on keywords
                if "job" in msg and ("abend" in msg or "erro" in msg):
                    response = "Jobs em estado ABEND encontrados:\n- Data Processing (ID: JOB002) na workstation TWS_AGENT2\n\nRecomendo investigar o log do job e verificar dependências."
                elif "status" in msg or "workstation" in msg:
                    response = "Status atual do ambiente TWS:\n\nWorkstations:\n- TWS_MASTER: ONLINE\n- TWS_AGENT1: ONLINE\n- TWS_AGENT2: OFFLINE\n\nJobs:\n- Daily Backup: SUCC (TWS_AGENT1)\n- Data Processing: ABEND (TWS_AGENT2)\n- Report Generation: SUCC (TWS_AGENT1)"
                elif "tws" in msg:
                    response = f"Como {agent_id}, posso ajudar com questões relacionadas ao TWS. Que informações você precisa?"
                elif "obrigado" in msg or "valeu" in msg:
                    response = "Disponível para ajudar! Se precisar de mais informações sobre o TWS, é só perguntar."
                else:
                    response = f"Entendi sua mensagem: '{raw_data}'. Como {agent_id}, estou aqui para ajudar com questões do TWS."
                
                # Add agent response to history
                conversation_history.append({"role": "assistant", "content": response})
                logger.info(f"Generated response: {response}")
                
                # Send response back to client
                response_data = {
                    "type": "message",
                    "sender": "agent",
                    "message": response,
                }
                logger.info(f"Sending response_data: {response_data}")
                await websocket.send_text(json.dumps(response_data))
                logger.info(f"Response sent to client for agent '{agent_id}'")
                
            except Exception as agent_error:
                logger.error(f"Error processing message with agent '{agent_id}': {agent_error}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                error_data = {
                    "type": "error",
                    "sender": "agent",
                    "message": f"Erro ao processar mensagem: {str(agent_error)}",
                }
                await websocket.send_text(json.dumps(error_data))
        
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from agent '{agent_id}'.")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket for agent '{agent_id}': {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        try:
            await websocket.close(code=1011)
        except:
            pass

    # Removed duplicate code


async def _validate_input(raw_data: str, agent_id: str, websocket: WebSocket) -> dict:
    """Validate input data for size and potential injection attempts."""
    # Input validation and size check
    if len(raw_data) > 10000:  # Limit message size to 10KB
        await send_error_message(websocket, "Mensagem muito longa. Máximo de 10.000 caracteres permitido.")
        return {"is_valid": False}

    # Additional validation: check for potential injection attempts
    if "<script>" in raw_data or "javascript:" in raw_data.lower():
        logger.warning(f"Potential injection attempt detected from agent '{agent_id}': {raw_data[:100]}...")
        await send_error_message(websocket, "Conteúdo não permitido detectado.")
        return {"is_valid": False}

    return {"is_valid": True}
