"""
Sistema de Idempotency Keys para o Resync

Este módulo implementa um sistema completo de idempotency keys para garantir
que operações críticas não sejam executadas múltiplas vezes, mesmo em caso
de falhas de rede ou retry automático.

Características:
- Storage Redis para alta performance
- TTL configurável para limpeza automática
- Proteção contra processamento concorrente
- Serialização/deserialização automática
- Métricas de monitoramento

Author: Resync Team
Date: October 2025
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from redis.asyncio import Redis

from resync.core.structured_logger import get_logger

logger = get_logger(__name__)


@dataclass
class IdempotencyConfig:
    """Configuração do sistema de idempotency"""
    ttl_hours: int = 24
    redis_db: int = 1
    key_prefix: str = "idempotency"
    processing_prefix: str = "processing"
    max_response_size_kb: int = 64  # 64KB máximo por resposta


@dataclass
class IdempotencyRecord:
    """Registro de idempotency armazenado"""
    idempotency_key: str
    request_hash: str
    response_data: Dict[str, Any]
    status_code: int
    created_at: datetime
    expires_at: datetime
    request_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização"""
        return {
            "idempotency_key": self.idempotency_key,
            "request_hash": self.request_hash,
            "response_data": self.response_data,
            "status_code": self.status_code,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "request_metadata": self.request_metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IdempotencyRecord':
        """Cria instância a partir de dicionário"""
        return cls(
            idempotency_key=data["idempotency_key"],
            request_hash=data["request_hash"],
            response_data=data["response_data"],
            status_code=data["status_code"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            request_metadata=data.get("request_metadata", {})
        )


@dataclass
class IdempotencyMetrics:
    """Métricas do sistema de idempotency"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    concurrent_blocks: int = 0
    storage_errors: int = 0
    expired_cleanups: int = 0

    @property
    def hit_rate(self) -> float:
        """Taxa de acertos do cache"""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests


class IdempotencyManager:
    """
    Gerenciador de chaves de idempotência

    Responsável por armazenar e recuperar respostas de operações
    idempotentes, garantindo que operações críticas não sejam
    executadas múltiplas vezes.
    """

    def __init__(
        self,
        redis_client: Redis,
        config: Optional[IdempotencyConfig] = None
    ):
        self.redis = redis_client
        self.config = config or IdempotencyConfig()
        self.metrics = IdempotencyMetrics()

        logger.info(
            "Idempotency manager initialized",
            ttl_hours=self.config.ttl_hours,
            redis_db=self.config.redis_db,
            max_response_size_kb=self.config.max_response_size_kb
        )

    async def get_cached_response(
        self,
        idempotency_key: str,
        request_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Recupera resposta em cache para chave de idempotência

        Args:
            idempotency_key: Chave de idempotência
            request_data: Dados da requisição para validação (opcional)

        Returns:
            Resposta em cache ou None se não encontrada
        """
        self.metrics.total_requests += 1

        try:
            key = self._make_key(idempotency_key)
            cached_data = await self.redis.get(key)

            if not cached_data:
                self.metrics.cache_misses += 1
                return None

            # Desserializar dados
            record_data = json.loads(cached_data)
            record = IdempotencyRecord.from_dict(record_data)

            # Verificar se expirou (defesa extra)
            if datetime.utcnow() > record.expires_at:
                await self.redis.delete(key)
                self.metrics.expired_cleanups += 1
                logger.warning(
                    "Expired idempotency record cleaned up",
                    idempotency_key=idempotency_key
                )
                return None

            # Validar hash da requisição se fornecido
            if request_data is not None:
                current_hash = self._hash_request_data(request_data)
                if current_hash != record.request_hash:
                    logger.warning(
                        "Idempotency key collision detected",
                        idempotency_key=idempotency_key,
                        stored_hash=record.request_hash,
                        current_hash=current_hash
                    )
                    # Em caso de colisão, não usar cache
                    return None

            self.metrics.cache_hits += 1

            logger.debug(
                "Idempotency cache hit",
                idempotency_key=idempotency_key,
                age_seconds=(datetime.utcnow() - record.created_at).total_seconds()
            )

            return {
                "status_code": record.status_code,
                "data": record.response_data,
                "cached_at": record.created_at.isoformat(),
                "expires_at": record.expires_at.isoformat()
            }

        except Exception as e:
            self.metrics.storage_errors += 1
            logger.error(
                "Failed to get cached response",
                idempotency_key=idempotency_key,
                error=str(e)
            )
            return None

    async def cache_response(
        self,
        idempotency_key: str,
        response_data: Dict[str, Any],
        status_code: int = 200,
        request_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Armazena resposta para chave de idempotência

        Args:
            idempotency_key: Chave de idempotência
            response_data: Dados da resposta
            status_code: Código de status HTTP
            request_data: Dados da requisição para hash
            metadata: Metadados adicionais

        Returns:
            True se armazenado com sucesso, False caso contrário
        """
        try:
            # Verificar tamanho da resposta
            response_size = len(json.dumps(response_data).encode('utf-8'))
            max_size_bytes = self.config.max_response_size_kb * 1024

            if response_size > max_size_bytes:
                logger.warning(
                    "Response too large for idempotency cache",
                    idempotency_key=idempotency_key,
                    size_kb=response_size / 1024,
                    max_size_kb=self.config.max_response_size_kb
                )
                return False

            # Criar registro
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=self.config.ttl_hours)

            record = IdempotencyRecord(
                idempotency_key=idempotency_key,
                request_hash=self._hash_request_data(request_data) if request_data else "",
                response_data=response_data,
                status_code=status_code,
                created_at=now,
                expires_at=expires_at,
                request_metadata=metadata or {}
            )

            # Serializar e armazenar
            key = self._make_key(idempotency_key)
            data = json.dumps(record.to_dict())

            ttl_seconds = int((expires_at - now).total_seconds())
            success = await self.redis.setex(key, ttl_seconds, data)

            if success:
                logger.debug(
                    "Response cached for idempotency",
                    idempotency_key=idempotency_key,
                    ttl_seconds=ttl_seconds,
                    size_kb=response_size / 1024
                )
                return True
            else:
                logger.error(
                    "Failed to cache response",
                    idempotency_key=idempotency_key
                )
                return False

        except Exception as e:
            self.metrics.storage_errors += 1
            logger.error(
                "Failed to cache response",
                idempotency_key=idempotency_key,
                error=str(e)
            )
            return False

    async def is_processing(self, idempotency_key: str) -> bool:
        """
        Verifica se operação já está em processamento

        Args:
            idempotency_key: Chave de idempotência

        Returns:
            True se já está em processamento
        """
        try:
            processing_key = self._make_processing_key(idempotency_key)
            return await self.redis.exists(processing_key)
        except Exception as e:
            logger.error(
                "Failed to check processing status",
                idempotency_key=idempotency_key,
                error=str(e)
            )
            return False

    async def mark_processing(
        self,
        idempotency_key: str,
        ttl_seconds: int = 300
    ) -> bool:
        """
        Marca operação como em processamento

        Args:
            idempotency_key: Chave de idempotência
            ttl_seconds: TTL para a marca de processamento

        Returns:
            True se marcado com sucesso
        """
        try:
            processing_key = self._make_processing_key(idempotency_key)
            success = await self.redis.setex(
                processing_key,
                ttl_seconds,
                json.dumps({
                    "started_at": datetime.utcnow().isoformat(),
                    "ttl_seconds": ttl_seconds
                })
            )

            if success:
                logger.debug(
                    "Operation marked as processing",
                    idempotency_key=idempotency_key,
                    ttl_seconds=ttl_seconds
                )
                return True
            else:
                logger.error(
                    "Failed to mark operation as processing",
                    idempotency_key=idempotency_key
                )
                return False

        except Exception as e:
            self.metrics.storage_errors += 1
            logger.error(
                "Failed to mark processing",
                idempotency_key=idempotency_key,
                error=str(e)
            )
            return False

    async def clear_processing(self, idempotency_key: str) -> bool:
        """
        Remove marca de processamento

        Args:
            idempotency_key: Chave de idempotência

        Returns:
            True se removido com sucesso
        """
        try:
            processing_key = self._make_processing_key(idempotency_key)
            deleted = await self.redis.delete(processing_key)

            if deleted:
                logger.debug(
                    "Processing mark cleared",
                    idempotency_key=idempotency_key
                )
            else:
                logger.debug(
                    "No processing mark to clear",
                    idempotency_key=idempotency_key
                )

            return True

        except Exception as e:
            logger.error(
                "Failed to clear processing mark",
                idempotency_key=idempotency_key,
                error=str(e)
            )
            return False

    async def invalidate_key(self, idempotency_key: str) -> bool:
        """
        Invalida chave de idempotência (remove do cache)

        Args:
            idempotency_key: Chave a ser invalidada

        Returns:
            True se invalidada com sucesso
        """
        try:
            key = self._make_key(idempotency_key)
            processing_key = self._make_processing_key(idempotency_key)

            # Remover ambos: resposta cacheada e marca de processamento
            deleted_count = await self.redis.delete(key, processing_key)

            logger.info(
                "Idempotency key invalidated",
                idempotency_key=idempotency_key,
                keys_deleted=deleted_count
            )

            return deleted_count > 0

        except Exception as e:
            logger.error(
                "Failed to invalidate idempotency key",
                idempotency_key=idempotency_key,
                error=str(e)
            )
            return False

    async def cleanup_expired(self) -> int:
        """
        Limpa registros expirados (chamado periodicamente)

        Returns:
            Número de registros removidos
        """
        try:
            # Redis já remove automaticamente com TTL, mas podemos
            # fazer limpeza manual se necessário
            # Por enquanto, apenas logging de métricas
            logger.info(
                "Idempotency cleanup completed",
                metrics=self.get_metrics()
            )
            return 0

        except Exception as e:
            logger.error("Failed to cleanup expired records", error=str(e))
            return 0

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais"""
        return {
            "total_requests": self.metrics.total_requests,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "hit_rate": self.metrics.hit_rate,
            "concurrent_blocks": self.metrics.concurrent_blocks,
            "storage_errors": self.metrics.storage_errors,
            "expired_cleanups": self.metrics.expired_cleanups
        }

    def _make_key(self, idempotency_key: str) -> str:
        """Cria chave Redis para resposta cacheada"""
        return f"{self.config.key_prefix}:{idempotency_key}"

    def _make_processing_key(self, idempotency_key: str) -> str:
        """Cria chave Redis para marca de processamento"""
        return f"{self.config.processing_prefix}:{idempotency_key}"

    def _hash_request_data(self, request_data: Dict[str, Any]) -> str:
        """
        Gera hash dos dados da requisição para detectar mudanças

        Args:
            request_data: Dados da requisição

        Returns:
            Hash SHA256 dos dados
        """
        # Normalizar dados para hash consistente
        normalized = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


class IdempotencyKeyGenerator:
    """
    Gerador de chaves de idempotência
    """

    @staticmethod
    def generate() -> str:
        """Gera nova chave de idempotência"""
        return str(uuid.uuid4())

    @staticmethod
    def is_valid(key: str) -> bool:
        """Valida formato da chave de idempotência"""
        try:
            uuid.UUID(key)
            return True
        except ValueError:
            return False


# Funções utilitárias

async def create_idempotency_manager(
    redis_url: str,
    config: Optional[IdempotencyConfig] = None
) -> IdempotencyManager:
    """
    Factory function para criar IdempotencyManager

    Args:
        redis_url: URL de conexão Redis
        config: Configuração opcional

    Returns:
        Instância configurada do IdempotencyManager
    """
    redis_client = Redis.from_url(redis_url, db=(config.redis_db if config else 1))
    return IdempotencyManager(redis_client, config)


def generate_idempotency_key() -> str:
    """Alias para geração rápida de chave"""
    return IdempotencyKeyGenerator.generate()


def validate_idempotency_key(key: str) -> bool:
    """Alias para validação rápida de chave"""
    return IdempotencyKeyGenerator.is_valid(key)