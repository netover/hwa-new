import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Importa a instância real do gerenciador de agentes, 'reg', e a renomeia para clareza.
from app.agents.manager import reg as agent_manager


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


@router.post("/chat", response_model=ChatResponse)  # type: ignore[misc]
async def chat_endpoint(chat_request: ChatRequest) -> ChatResponse:
    """
    Endpoint principal para interação com o chat.
    Recebe uma mensagem, a roteia através do dispatcher de agentes e retorna a resposta.
    """
    request_id = str(uuid.uuid4())

    # A lógica de como o dispatcher é acessado será corrigida no app/agents/manager.py.
    # Assumimos que o agent_manager terá uma propriedade 'dispatcher'.
    if not hasattr(agent_manager, "dispatcher") or not agent_manager.dispatcher:
        raise HTTPException(
            status_code=503,
            detail="O agente Dispatcher não está inicializado ou disponível no momento.",
        )

    try:
        # Roteia a mensagem através do agente dispatcher do AGNO
        result = await agent_manager.dispatcher.run(
            chat_request.message,
            session_id=chat_request.session_id,
            context=chat_request.context,
        )
    except Exception as e:
        # Captura exceções durante a execução do agente para fornecer um erro claro.
        raise HTTPException(
            status_code=500, detail=f"Ocorreu um erro interno no agente: {e}"
        ) from e

    return ChatResponse(
        reply=result.get("reply", ""),
        sources=result.get("sources", []),
        agent_route=result.get("agent_route", ""),
        request_id=request_id,
    )
