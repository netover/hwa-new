"""Dependências compartilhadas para endpoints FastAPI.

Este módulo fornece funções de dependência para injeção em endpoints,
incluindo gerenciamento de idempotência, autenticação, e obtenção de IDs de contexto.
"""

from typing import Optional
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from resync.core.container import app_container
from resync.core.idempotency import (
    IdempotencyManager,
    RedisIdempotencyStorage,
    InMemoryIdempotencyStorage,
)
from resync.core.exceptions import ValidationError
from resync.core.structured_logger import get_logger
from resync.core.exceptions import (
    AuthenticationError,
    ServiceUnavailableError,
)

logger = get_logger(__name__)

# ============================================================================
# IDEMPOTENCY DEPENDENCIES
# ============================================================================


async def get_idempotency_manager() -> IdempotencyManager:
    """Obtém a instância do IdempotencyManager a partir do container de DI.
    
    Returns:
        IdempotencyManager configurado
        
    Raises:
        ServiceUnavailableError: Se o serviço de idempotência não estiver disponível.
    """
    try:
        manager = await app_container.get(IdempotencyManager)
        return manager
    except Exception as e:
        logger.error("idempotency_manager_unavailable", error=str(e), exc_info=True)
        raise ServiceUnavailableError("Idempotency service is not available.")


async def get_idempotency_key(
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key")
) -> Optional[str]:
    """Extrai idempotency key do header.
    
    Args:
        x_idempotency_key: Header X-Idempotency-Key
        
    Returns:
        Idempotency key ou None
    """
    return x_idempotency_key


async def require_idempotency_key(
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key")
) -> str:
    """Extrai e valida idempotency key obrigatória.
    
    Args:
        x_idempotency_key: Header X-Idempotency-Key
        
    Returns:
        Idempotency key
        
    Raises:
        ValidationError: Se key não foi fornecida
    """
    if not x_idempotency_key:
        raise ValidationError(
            message="Idempotency key is required for this operation",
            details={
                "header": "X-Idempotency-Key",
                "hint": "Include X-Idempotency-Key header with a unique UUID"
            }
        )
    
    # Validar formato (deve ser UUID v4)
    import re
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    if not uuid_pattern.match(x_idempotency_key):
        raise ValidationError(
            message="Invalid idempotency key format",
            details={
                "header": "X-Idempotency-Key",
                "expected": "UUID v4 format",
                "received": x_idempotency_key
            }
        )
    
    return x_idempotency_key


# ============================================================================
# CORRELATION ID DEPENDENCIES
# ============================================================================

async def get_correlation_id(
    x_correlation_id: Optional[str] = Header(None, alias="X-Correlation-ID"),
    request: Request = None
) -> str:
    """Obtém ou gera correlation ID.
    
    Args:
        x_correlation_id: Header X-Correlation-ID
        request: Request object
        
    Returns:
        Correlation ID
    """
    if x_correlation_id:
        return x_correlation_id
    
    # Tentar obter do contexto
    from resync.core.context import get_correlation_id as get_ctx_correlation_id
    ctx_id = get_ctx_correlation_id()
    if ctx_id:
        return ctx_id
    
    # Gerar novo
    import uuid
    return str(uuid.uuid4())


# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """Obtém usuário atual (placeholder).
    
    Args:
        credentials: Credenciais de autenticação injetadas pelo FastAPI.
        
    Returns:
        Um dicionário representando o usuário ou None se não autenticado.
    """
    # TODO: Implementar autenticação real
    if credentials:
        # Validar token e retornar usuário
        pass
    
    return None


async def require_authentication(
    user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """Garante que um usuário esteja autenticado.
    
    Args:
        user: O usuário obtido da dependência `get_current_user`.
        
    Returns:
        Dados do usuário
        
    Raises:
        AuthenticationError: Se o usuário não estiver autenticado.
    """
    if not user:
        raise AuthenticationError(
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


# ============================================================================
# RATE LIMITING DEPENDENCIES
# ============================================================================

async def check_rate_limit(request: Request) -> None:
    """Verifica rate limit (placeholder).
    
    Args:
        request: Request object
        
    Raises:
        RateLimitError: Se o limite de taxa for excedido.
    """
    # TODO: Implementar verificação de rate limit
    pass
