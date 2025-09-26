from __future__ import annotations

import asyncio
import logging

from agno.agent import Agent
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from resync.core.agent_manager import agent_manager
from resync.core.connection_manager import connection_manager
from resync.core.ia_auditor import analyze_and_flag_memories
from resync.core.knowledge_graph import (  # noqa: N813
    AsyncKnowledgeGraph as knowledge_graph,
)

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- APIRouter Initialization ---
chat_router = APIRouter()
from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


async def x_run_auditor_safely__mutmut_orig():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except Exception:
        logger.error("IA Auditor background task failed unexpectedly.", exc_info=True)


async def x_run_auditor_safely__mutmut_1():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except Exception:
        logger.error(None, exc_info=True)


async def x_run_auditor_safely__mutmut_2():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except Exception:
        logger.error("IA Auditor background task failed unexpectedly.", exc_info=None)


async def x_run_auditor_safely__mutmut_3():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except Exception:
        logger.error(exc_info=True)


async def x_run_auditor_safely__mutmut_4():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except Exception:
        logger.error(
            "IA Auditor background task failed unexpectedly.",
        )


async def x_run_auditor_safely__mutmut_5():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except Exception:
        logger.error(
            "XXIA Auditor background task failed unexpectedly.XX", exc_info=True
        )


async def x_run_auditor_safely__mutmut_6():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except Exception:
        logger.error("ia auditor background task failed unexpectedly.", exc_info=True)


async def x_run_auditor_safely__mutmut_7():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except Exception:
        logger.error("IA AUDITOR BACKGROUND TASK FAILED UNEXPECTEDLY.", exc_info=True)


async def x_run_auditor_safely__mutmut_8():
    """
    Executes the IA auditor in a safe context, catching and logging any exceptions
    to prevent the background task from dying silently.
    """
    try:
        await analyze_and_flag_memories()
    except Exception:
        logger.error("IA Auditor background task failed unexpectedly.", exc_info=False)


x_run_auditor_safely__mutmut_mutants: ClassVar[MutantDict] = {
    "x_run_auditor_safely__mutmut_1": x_run_auditor_safely__mutmut_1,
    "x_run_auditor_safely__mutmut_2": x_run_auditor_safely__mutmut_2,
    "x_run_auditor_safely__mutmut_3": x_run_auditor_safely__mutmut_3,
    "x_run_auditor_safely__mutmut_4": x_run_auditor_safely__mutmut_4,
    "x_run_auditor_safely__mutmut_5": x_run_auditor_safely__mutmut_5,
    "x_run_auditor_safely__mutmut_6": x_run_auditor_safely__mutmut_6,
    "x_run_auditor_safely__mutmut_7": x_run_auditor_safely__mutmut_7,
    "x_run_auditor_safely__mutmut_8": x_run_auditor_safely__mutmut_8,
}


def run_auditor_safely(*args, **kwargs):
    result = _mutmut_trampoline(
        x_run_auditor_safely__mutmut_orig,
        x_run_auditor_safely__mutmut_mutants,
        args,
        kwargs,
    )
    return result


run_auditor_safely.__signature__ = _mutmut_signature(x_run_auditor_safely__mutmut_orig)
x_run_auditor_safely__mutmut_orig.__name__ = "x_run_auditor_safely"


@chat_router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
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
                context={
                    "agent_config": (
                        agent_manager.get_agent(agent_id).__dict__
                        if agent_manager.get_agent(agent_id)
                        else "N/A"
                    )
                },
            )

            # --- IA Auditor ---
            # Recommendation 3: Run the auditor in a safe background task
            logger.info("Scheduling IA Auditor to run in the background.")
            asyncio.create_task(run_auditor_safely())

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
        await connection_manager.disconnect(websocket)
