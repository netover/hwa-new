"""Dependências compartilhadas para endpoints FastAPI.

Este módulo fornece funções de dependência para injeção em endpoints,
incluindo gerenciamento de idempotência, autenticação, rate limiting, etc.
"""

from typing import Optional
from fastapi import Header, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from resync.core.idempotency import (
    IdempotencyManager,
    RedisIdempotencyStorage,
    InMemoryIdempotencyStorage,
)
from resync.core.exceptions import ValidationError
from resync.core.structured_logger import get_logger
from resync.settings import settings

logger = get_logger(__name__)

# ============================================================================
# IDEMPOTENCY DEPENDENCIES
# ============================================================================

# Instância global do manager (será inicializada no startup)
_idempotency_manager: Optional[IdempotencyManager] = None


async def get_idempotency_manager() -> IdempotencyManager:
    """Obtém instância do IdempotencyManager.
    
    Returns:
        IdempotencyManager configurado
        
    Raises:
        HTTPException: Se manager não foi inicializado
    """
    global _idempotency_manager
    
    if _idempotency_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Idempotency service not initialized"
        )
    
    return _idempotency_manager


async def initialize_idempotency_manager(redis_client=None) -> None:
    """Inicializa o IdempotencyManager global.
    
    Deve ser chamado no startup da aplicação.
    
    Args:
        redis_client: Cliente Redis (opcional, usa in-memory se não fornecido)
    """
    global _idempotency_manager
    
    if redis_client:
        storage = RedisIdempotencyStorage(redis_client)
        logger.info("Idempotency manager initialized with Redis storage")
    else:
        storage = InMemoryIdempotencyStorage()
        logger.warning(
            "Idempotency manager initialized with in-memory storage. "
            "Not recommended for production!"
        )
    
    _idempotency_manager = IdempotencyManager(
        storage=storage,
        default_ttl_seconds=getattr(settings, 'IDEMPOTENCY_TTL_SECONDS', 86400)
    )


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
    credentials: Optional[HTTPAuthorizationCredentials] = None
) -> Optional[dict]:
    """Obtém usuário atual (placeholder).
    
    Args:
        credentials: Credenciais de autenticação
        
    Returns:
        Dados do usuário ou None
    """
    # TODO: Implementar autenticação real
    if credentials:
        # Validar token e retornar usuário
        pass
    
    return None


async def require_authentication(
    credentials: HTTPAuthorizationCredentials = None
) -> dict:
    """Requer autenticação (placeholder).
    
    Args:
        credentials: Credenciais de autenticação
        
    Returns:
        Dados do usuário
        
    Raises:
        HTTPException: Se não autenticado
    """
    user = await get_current_user(credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
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
        HTTPException: Se rate limit excedido
    """
    # TODO: Implementar verificação de rate limit
    pass
