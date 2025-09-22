from typing import Dict

from fastapi import APIRouter, Response, status

from app.services.tws_client import OptimizedTWSClient

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("/app", summary="Verificar a saúde da aplicação")
async def app_health_check() -> Dict[str, str]:
    """
    Endpoint simples que retorna 'ok' para indicar que a aplicação está rodando.
    Pode ser usado por sistemas de monitoramento (como Kubernetes liveness probes).
    """
    return {"status": "ok"}


@router.get("/tws", summary="Verificar a conectividade com a API do TWS")
async def tws_health_check(response: Response) -> Dict[str, str]:
    """
    Verifica a saúde da conexão com a API do TWS fazendo uma chamada simples.
    """
    try:
        async with OptimizedTWSClient() as client:
            # Usa um método cacheado para não sobrecarregar a API
            await client.get_system_status()
        return {"status": "healthy", "dependency": "TWS API", "connection": "ok"}
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "unhealthy",
            "dependency": "TWS API",
            "connection": "failed",
            "error": str(e),
        }
