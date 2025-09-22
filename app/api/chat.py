import asyncio
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Importa a instância real do gerenciador de agentes, 'reg', e a renomeia para clareza.
from app.agents.manager import reg as agent_manager
from app.services.semantic_extractor import semantic_extractor
from app.services.semantic_logger import SemanticLogger


class ChatRequest(BaseModel):  # type: ignore[misc]
    """Modelo para validação da requisição do chat."""

    message: str = Field(..., min_length=1, description="A mensagem do usuário.")
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):  # type: ignore[misc]
    """Modelo para a resposta do chat."""

    reply: str
    sources: List[Dict[str, Any]]
    agent_route: str
    request_id: str


router = APIRouter(prefix="/api")
semantic_logger = SemanticLogger()


@router.post("/chat", response_model=ChatResponse)  # type: ignore[misc]
async def chat_endpoint(chat_request: ChatRequest) -> ChatResponse:
    """
    Endpoint principal para interação com o chat.
    Recebe uma mensagem, a roteia através do dispatcher de agentes e retorna a resposta.
    """
    request_id = str(uuid.uuid4())
    session_id = chat_request.session_id or str(uuid.uuid4())

    if not agent_manager.dispatcher:
        raise HTTPException(
            status_code=503,
            detail="O agente Dispatcher não está inicializado ou disponível no momento.",
        )

    # 1. Extração Semântica
    intent = semantic_extractor.extract_intent(chat_request.message)
    entities = semantic_extractor.extract_entities(chat_request.message)

    # 2. Execução do Agente
    try:
        result = await agent_manager.dispatcher.run(
            chat_request.message,
            session_id=session_id,
            context=chat_request.context,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ocorreu um erro interno no agente: {e}"
        ) from e

    # 3. Logging Semântico em Background
    interaction_data = {
        "user_query": chat_request.message,
        "agent_response": result.get("reply", ""),
        "session_id": session_id,
        "interaction_id": request_id,
        "classified_intent": intent,
        "entities": entities,
        "agent_name": result.get("agent_route", "dispatcher"),
        "tools_used": result.get("sources", []),
    }
    asyncio.create_task(semantic_logger.log_interaction(interaction_data))

    # 4. Resposta ao Usuário
    return ChatResponse(
        reply=result.get("reply", ""),
        sources=result.get("sources", []),
        agent_route=result.get("agent_route", ""),
        request_id=request_id,
    )
