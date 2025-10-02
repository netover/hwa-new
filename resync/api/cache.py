from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

from resync.core.fastapi_di import get_tws_client
from resync.core.interfaces import ITWSClient
from resync.settings import settings

cache_router = APIRouter()

# Define o esquema de segurança: espera credenciais Basic Auth.
security = HTTPBasic()


async def verify_admin_credentials(creds: HTTPBasicCredentials = Depends(security)):
    """
    Dependência para verificar as credenciais de administrador usando Basic Auth.

    Esta função é usada como uma dependência de segurança para endpoints
    administrativos. Ela valida o nome de usuário e a senha fornecidos
    contra as credenciais definidas no sistema.

    Utiliza `secrets.compare_digest` para uma comparação segura que previne
    ataques de timing.

    Args:
        creds: Credenciais HTTPBasic injetadas pelo FastAPI.

    Raises:
        HTTPException: Lança um erro 401 Unauthorized se as credenciais
                       forem inválidas.
    """
    # Busca as credenciais de administrador a partir das configurações da aplicação.
    admin_user = settings.ADMIN_USERNAME
    admin_pass = settings.ADMIN_PASSWORD

    # Garante que as credenciais de administrador estão configuradas no servidor.
    if not admin_user or not admin_pass:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="As credenciais de administrador não estão configuradas no servidor.",
        )

    correct_username = secrets.compare_digest(creds.username, admin_user)
    correct_password = secrets.compare_digest(creds.password, admin_pass)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais de administrador inválidas ou ausentes.",
            headers={"WWW-Authenticate": "Basic"},
        )


@cache_router.post(
    "/invalidate",
    summary="Invalidate TWS Cache",
    dependencies=[Depends(verify_admin_credentials)],
)
async def invalidate_tws_cache(
    scope: str = "system",  # 'system', 'jobs', 'workstations'
    tws_client: ITWSClient = Depends(get_tws_client),
):
    """
    Invalidates the TWS data cache based on the specified scope.
    Requires administrator credentials via HTTP Basic Auth for authorization.

    - **scope='system'**: Invalidates all TWS-related caches.
    - **scope='jobs'**: Invalidates only the main job list cache.
    - **scope='workstations'**: Invalidates only the workstation list cache.
    """
    if scope == "system":
        await tws_client.invalidate_system_cache()
        return {"status": "success", "detail": "Full TWS system cache invalidated."}
    elif scope == "jobs":
        await tws_client.invalidate_all_jobs()
        return {"status": "success", "detail": "All jobs list cache invalidated."}
    elif scope == "workstations":
        await tws_client.invalidate_all_workstations()
        return {"status": "success", "detail": "All workstations list cache invalidated."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scope '{scope}'. Must be 'system', 'jobs', or 'workstations'.",
        )