"""Sistema de Idempotency Keys para operações idempotentes.

Este módulo implementa o padrão de Idempotency Keys para garantir que
operações críticas possam ser executadas múltiplas vezes com segurança,
retornando sempre o mesmo resultado.

Casos de uso:
- Pagamentos e transações financeiras
- Criação de recursos
- Operações de escrita críticas
- Prevenção de duplicação em retries

Baseado nas práticas da Stripe API.
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, TypeVar
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps

from resync.core.exceptions import ResourceConflictError, ValidationError
from resync.core.structured_logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


# ============================================================================
# MODELS
# ============================================================================

class IdempotencyStatus(str, Enum):
    """Status de uma operação idempotente."""
    PROCESSING = "processing"  # Em processamento
    COMPLETED = "completed"    # Completada com sucesso
    FAILED = "failed"          # Falhou


@dataclass
class IdempotencyRecord:
    """Registro de uma operação idempotente.
    
    Attributes:
        key: Chave de idempotência
        status: Status da operação
        result: Resultado da operação (se completada)
        error: Erro da operação (se falhou)
        created_at: Timestamp de criação
        updated_at: Timestamp de última atualização
        expires_at: Timestamp de expiração
        request_hash: Hash da requisição para validação
    """
    key: str
    status: IdempotencyStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    expires_at: datetime = None
    request_hash: Optional[str] = None
    
    def __post_init__(self):
        """Inicializa timestamps se não fornecidos."""
        now = datetime.utcnow()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        data['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IdempotencyRecord':
        """Cria instância a partir de dicionário."""
        data = data.copy()
        data['status'] = IdempotencyStatus(data['status'])
        
        for field in ['created_at', 'updated_at', 'expires_at']:
            if data.get(field):
                data[field] = datetime.fromisoformat(data[field])
        
        return cls(**data)


# ============================================================================
# STORAGE INTERFACE
# ============================================================================

class IdempotencyStorage:
    """Interface abstrata para storage de idempotency keys.
    
    Implementações concretas podem usar Redis, banco de dados, etc.
    """
    
    async def get(self, key: str) -> Optional[IdempotencyRecord]:
        """Obtém registro de idempotência.
        
        Args:
            key: Chave de idempotência
            
        Returns:
            Registro se existir, None caso contrário
        """
        raise NotImplementedError
    
    async def set(
        self,
        key: str,
        record: IdempotencyRecord,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """Armazena registro de idempotência.
        
        Args:
            key: Chave de idempotência
            record: Registro a ser armazenado
            ttl_seconds: Tempo de vida em segundos
        """
        raise NotImplementedError
    
    async def delete(self, key: str) -> None:
        """Remove registro de idempotência.
        
        Args:
            key: Chave de idempotência
        """
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe.
        
        Args:
            key: Chave de idempotência
            
        Returns:
            True se existir, False caso contrário
        """
        raise NotImplementedError


class InMemoryIdempotencyStorage(IdempotencyStorage):
    """Implementação em memória para desenvolvimento/testes.
    
    ATENÇÃO: Não usar em produção! Dados são perdidos ao reiniciar.
    """
    
    def __init__(self):
        """Inicializa storage em memória."""
        self._storage: Dict[str, IdempotencyRecord] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[IdempotencyRecord]:
        """Obtém registro."""
        async with self._lock:
            record = self._storage.get(key)
            
            # Verificar expiração
            if record and record.expires_at:
                if datetime.utcnow() > record.expires_at:
                    del self._storage[key]
                    return None
            
            return record
    
    async def set(
        self,
        key: str,
        record: IdempotencyRecord,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """Armazena registro."""
        async with self._lock:
            if ttl_seconds:
                record.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            
            self._storage[key] = record
    
    async def delete(self, key: str) -> None:
        """Remove registro."""
        async with self._lock:
            self._storage.pop(key, None)
    
    async def exists(self, key: str) -> bool:
        """Verifica existência."""
        record = await self.get(key)
        return record is not None


# ============================================================================
# IDEMPOTENCY MANAGER
# ============================================================================

class IdempotencyManager:
    """Gerenciador de operações idempotentes.
    
    Coordena o armazenamento e recuperação de resultados de operações
    idempotentes, garantindo que a mesma operação não seja executada
    múltiplas vezes.
    
    Example:
        ```python
        manager = IdempotencyManager(storage)
        
        @manager.idempotent(ttl_seconds=3600)
        async def create_payment(amount: float, idempotency_key: str):
            # Operação crítica
            return await payment_service.create(amount)
        ```
    """
    
    def __init__(
        self,
        storage: IdempotencyStorage,
        default_ttl_seconds: int = 86400  # 24 horas
    ):
        """Inicializa o manager.
        
        Args:
            storage: Storage para idempotency keys
            default_ttl_seconds: TTL padrão em segundos
        """
        self.storage = storage
        self.default_ttl_seconds = default_ttl_seconds
    
    def _compute_request_hash(self, *args, **kwargs) -> str:
        """Computa hash da requisição para validação.
        
        Args:
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Hash SHA256 da requisição
        """
        # Serializar argumentos
        data = {
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
    
    async def execute_idempotent(
        self,
        key: str,
        func: Callable[..., T],
        *args,
        ttl_seconds: Optional[int] = None,
        validate_request: bool = True,
        **kwargs
    ) -> T:
        """Executa função de forma idempotente.
        
        Args:
            key: Chave de idempotência
            func: Função a ser executada
            *args: Argumentos posicionais
            ttl_seconds: TTL customizado
            validate_request: Se deve validar hash da requisição
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função
            
        Raises:
            ResourceConflictError: Se operação já está em processamento
            ValidationError: Se requisição não corresponde ao hash armazenado
        """
        if not key:
            raise ValidationError(
                message="Idempotency key is required",
                details={"field": "idempotency_key"}
            )
        
        ttl = ttl_seconds or self.default_ttl_seconds
        request_hash = self._compute_request_hash(*args, **kwargs) if validate_request else None
        
        # Verificar se já existe
        existing = await self.storage.get(key)
        
        if existing:
            # Validar hash da requisição
            if validate_request and existing.request_hash != request_hash:
                logger.warning(
                    "Idempotency key reused with different request",
                    idempotency_key=key
                )
                raise ValidationError(
                    message="Idempotency key already used with different request",
                    details={
                        "idempotency_key": key,
                        "reason": "request_mismatch"
                    }
                )
            
            # Verificar status
            if existing.status == IdempotencyStatus.PROCESSING:
                logger.info(
                    "Operation already in progress",
                    idempotency_key=key
                )
                raise ResourceConflictError(
                    message="Operation already in progress",
                    details={"idempotency_key": key}
                )
            
            elif existing.status == IdempotencyStatus.COMPLETED:
                logger.info(
                    "Returning cached result",
                    idempotency_key=key
                )
                return existing.result
            
            elif existing.status == IdempotencyStatus.FAILED:
                logger.info(
                    "Previous attempt failed, retrying",
                    idempotency_key=key
                )
                # Permitir retry em caso de falha
        
        # Criar registro de processamento
        record = IdempotencyRecord(
            key=key,
            status=IdempotencyStatus.PROCESSING,
            request_hash=request_hash
        )
        
        await self.storage.set(key, record, ttl)
        
        logger.info(
            "Starting idempotent operation",
            idempotency_key=key
        )
        
        # Executar função
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Armazenar resultado
            record.status = IdempotencyStatus.COMPLETED
            record.result = result
            record.updated_at = datetime.utcnow()
            
            await self.storage.set(key, record, ttl)
            
            logger.info(
                "Idempotent operation completed",
                idempotency_key=key
            )
            
            return result
        
        except Exception as e:
            # Armazenar erro
            record.status = IdempotencyStatus.FAILED
            record.error = str(e)
            record.updated_at = datetime.utcnow()
            
            await self.storage.set(key, record, ttl)
            
            logger.error(
                "Idempotent operation failed",
                idempotency_key=key,
                error=str(e)
            )
            
            raise
    
    def idempotent(
        self,
        ttl_seconds: Optional[int] = None,
        validate_request: bool = True,
        key_param: str = "idempotency_key"
    ):
        """Decorator para tornar função idempotente.
        
        Args:
            ttl_seconds: TTL customizado
            validate_request: Se deve validar hash da requisição
            key_param: Nome do parâmetro que contém a chave
            
        Example:
            ```python
            @manager.idempotent(ttl_seconds=3600)
            async def create_order(order_data: dict, idempotency_key: str):
                return await db.create_order(order_data)
            ```
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extrair idempotency key
                key = kwargs.get(key_param)
                
                if not key:
                    raise ValidationError(
                        message=f"Missing required parameter: {key_param}",
                        details={"field": key_param}
                    )
                
                # Remover key dos kwargs para não passar para a função
                func_kwargs = {k: v for k, v in kwargs.items() if k != key_param}
                
                return await self.execute_idempotent(
                    key=key,
                    func=func,
                    *args,
                    ttl_seconds=ttl_seconds,
                    validate_request=validate_request,
                    **func_kwargs
                )
            
            return wrapper
        
        return decorator


# ============================================================================
# MIDDLEWARE
# ============================================================================

class IdempotencyMiddleware:
    """Middleware para extrair e validar idempotency keys de requisições HTTP.
    
    Extrai a chave do header X-Idempotency-Key e a disponibiliza
    no contexto da requisição.
    """
    
    HEADER_NAME = "X-Idempotency-Key"
    
    def __init__(
        self,
        app,
        manager: IdempotencyManager,
        required_methods: tuple = ("POST", "PUT", "PATCH")
    ):
        """Inicializa o middleware.
        
        Args:
            app: Aplicação ASGI
            manager: Gerenciador de idempotência
            required_methods: Métodos HTTP que requerem idempotency key
        """
        self.app = app
        self.manager = manager
        self.required_methods = required_methods
    
    async def __call__(self, scope, receive, send):
        """Processa requisição."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extrair idempotency key do header
        headers = dict(scope.get("headers", []))
        idempotency_key = headers.get(
            self.HEADER_NAME.lower().encode(),
            b""
        ).decode()
        
        # Armazenar no scope
        if idempotency_key:
            scope["idempotency_key"] = idempotency_key
        
        await self.app(scope, receive, send)


# ============================================================================
# HELPERS
# ============================================================================

def generate_idempotency_key() -> str:
    """Gera uma nova idempotency key.
    
    Returns:
        UUID v4 como string
    """
    import uuid
    return str(uuid.uuid4())


# Instância global para facilitar uso
_default_storage = InMemoryIdempotencyStorage()
_default_manager = IdempotencyManager(_default_storage)


def get_default_manager() -> IdempotencyManager:
    """Obtém o manager padrão.
    
    Returns:
        Manager de idempotência padrão
    """
    return _default_manager


def set_default_storage(storage: IdempotencyStorage) -> None:
    """Define o storage padrão.
    
    Args:
        storage: Storage a ser usado
    """
    global _default_manager
    _default_manager = IdempotencyManager(storage)


__all__ = [
    # Models
    'IdempotencyStatus',
    'IdempotencyRecord',
    # Storage
    'IdempotencyStorage',
    'InMemoryIdempotencyStorage',
    # Manager
    'IdempotencyManager',
    # Middleware
    'IdempotencyMiddleware',
    # Helpers
    'generate_idempotency_key',
    'get_default_manager',
    'set_default_storage',
]



class RedisIdempotencyStorage(IdempotencyStorage):
    """Implementação Redis para produção.
    
    Usa Redis para armazenar idempotency keys com TTL automático.
    Recomendado para ambientes de produção.
    """
    
    def __init__(self, redis_client):
        """Inicializa storage Redis.
        
        Args:
            redis_client: Cliente Redis (redis.asyncio.Redis)
        """
        self.redis = redis_client
        self._key_prefix = "idempotency:"
    
    def _make_key(self, key: str) -> str:
        """Cria chave Redis com prefixo.
        
        Args:
            key: Chave de idempotência
            
        Returns:
            Chave com prefixo
        """
        return f"{self._key_prefix}{key}"
    
    async def get(self, key: str) -> Optional[IdempotencyRecord]:
        """Obtém registro do Redis."""
        redis_key = self._make_key(key)
        data = await self.redis.get(redis_key)
        
        if not data:
            return None
        
        try:
            record_dict = json.loads(data)
            return IdempotencyRecord.from_dict(record_dict)
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.error(
                "Failed to deserialize idempotency record",
                key=key,
                error=str(e)
            )
            return None
    
    async def set(
        self,
        key: str,
        record: IdempotencyRecord,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """Armazena registro no Redis."""
        redis_key = self._make_key(key)
        data = json.dumps(record.to_dict())
        
        if ttl_seconds:
            await self.redis.setex(redis_key, ttl_seconds, data)
        else:
            await self.redis.set(redis_key, data)
    
    async def delete(self, key: str) -> None:
        """Remove registro do Redis."""
        redis_key = self._make_key(key)
        await self.redis.delete(redis_key)
    
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe no Redis."""
        redis_key = self._make_key(key)
        return await self.redis.exists(redis_key) > 0


# ============================================================================
# IDEMPOTENCY MANAGER
# ============================================================================

class IdempotencyManager:
    """Gerenciador de operações idempotentes.
    
    Coordena o armazenamento e recuperação de resultados de operações
    idempotentes, garantindo que a mesma operação não seja executada
    múltiplas vezes.
    
    Example:
        ```python
        manager = IdempotencyManager(storage)
        
        @manager.idempotent(ttl_seconds=3600)
        async def create_payment(amount: float, idempotency_key: str):
            # Operação crítica
            return await payment_service.create(amount)
        ```
    """
    
    def __init__(
        self,
        storage: IdempotencyStorage,
        default_ttl_seconds: int = 86400  # 24 horas
    ):
        """Inicializa o manager.
        
        Args:
            storage: Storage para idempotency keys
            default_ttl_seconds: TTL padrão em segundos
        """
        self.storage = storage
        self.default_ttl_seconds = default_ttl_seconds
    
    def _compute_request_hash(self, *args, **kwargs) -> str:
        """Computa hash da requisição para validação.
        
        Args:
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Hash SHA256 da requisição
        """
        # Serializar argumentos
        data = {
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
