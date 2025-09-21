from typing import Dict

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", summary="Verificar a saúde da aplicação")  # type: ignore[misc]
async def health_check() -> Dict[str, str]:
    """
    Endpoint simples que retorna 'ok' para indicar que a aplicação está rodando.
    Pode ser usado por sistemas de monitoramento (como Kubernetes liveness probes).
    """
    return {"status": "ok"}
