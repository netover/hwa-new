from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.services.model_discovery import ModelInfo
from app.services.model_discovery import model_discovery as discovery_service


# Modelo mais enxuto para a lista de modelos disponíveis, para não sobrecarregar o frontend
class AvailableModel(BaseModel):  # type: ignore[misc]
    id: str
    name: str
    context_length: Optional[int] = None
    pricing: Dict[str, Any]


class ValidationResponse(BaseModel):  # type: ignore[misc]
    valid: bool
    model_info: Optional[ModelInfo] = None


router = APIRouter(prefix="/api/models", tags=["LLM Models"])


@router.get(  # type: ignore[misc]
    "/available",
    response_model=List[AvailableModel],
    summary="Listar modelos de IA disponíveis",
    description="Retorna uma lista de todos os modelos de IA disponíveis, com opção de forçar a atualização do cache.",
)
async def get_available_models(
    refresh: bool = Query(
        False,
        description="Força a atualização da lista de modelos a partir da fonte (ex: OpenRouter).",
    ),
) -> List[ModelInfo]:
    models = await discovery_service.get_available_models(force_refresh=refresh)
    return models


@router.get(  # type: ignore[misc]
    "/suggest",
    response_model=List[ModelInfo],
    summary="Sugerir modelos de IA com base em uma busca",
    description="Fornece uma lista de sugestões de modelos com base em uma string de busca.",
)
async def suggest_models(
    q: str = Query(
        ..., min_length=2, description="Texto para buscar nos nomes e IDs dos modelos."
    )
) -> List[ModelInfo]:
    return await discovery_service.suggest_models(q)


@router.get(  # type: ignore[misc]
    "/validate",
    response_model=ValidationResponse,
    summary="Validar se um ID de modelo existe",
    description="Verifica se um determinado ID de modelo é válido e retorna suas informações.",
)
async def validate_model(
    model_id: str = Query(
        ..., description="O ID completo do modelo a ser validado (ex: 'openai/gpt-4o')."
    )
) -> ValidationResponse:
    model = await discovery_service.validate_model(model_id)
    if model:
        return ValidationResponse(valid=True, model_info=model)
    return ValidationResponse(valid=False, model_info=None)
