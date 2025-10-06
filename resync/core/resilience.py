"""Padrões de resiliência para operações distribuídas.

Este módulo implementa padrões essenciais de resiliência:
- Circuit Breaker: Previne cascata de falhas
- Retry com Exponential Backoff: Tenta novamente com atraso crescente
- Timeout: Limita tempo de execução
- Bulkhead: Isolamento de recursos

Baseado em padrões de Michael Nygard (Release It!) e Netflix Hystrix.
"""

import asyncio
import time
import random
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, Union
from functools import wraps
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from resync.core.exceptions import (
    CircuitBreakerError,
    TimeoutError as AppTimeoutError,
    ServiceUnavailableError,
)
from resync.core.structured_logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


# ============================================================================
# CIRCUIT BREAKER
# ============================================================================

class CircuitState(str, Enum):
    """Estados do Circuit Breaker."""
    CLOSED = "closed"      # Funcionando normalmente
    OPEN = "open"          # Circuito aberto, rejeitando requisições
    HALF_OPEN = "half_open"  # Testando se o serviço recuperou


@dataclass
class CircuitBreakerConfig:
    """Configuração do Circuit Breaker.
    
    Attributes:
        failure_threshold: Número de falhas para abrir o circuito
        success_threshold: Número de sucessos para fechar o circuito
        timeout: Tempo em segundos antes de tentar half-open
        expected_exception: Tipo de exceção que conta como falha
    """
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0
    expected_exception: type = Exception


@dataclass
class CircuitBreakerStats:
    """Estatísticas do Circuit Breaker."""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_state_change: datetime = field(default_factory=datetime.utcnow)
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0


class CircuitBreaker:
    """Implementação do padrão Circuit Breaker.
    
    Previne cascata de falhas ao detectar serviços com problemas
    e temporariamente rejeitar requisições.
    
    Estados:
    - CLOSED: Funcionando normalmente, todas as requisições passam
    - OPEN: Circuito aberto, requisições são rejeitadas imediatamente
    - HALF_OPEN: Testando recuperação, permite algumas requisições
    
    Example:
        ```python
        cb = CircuitBreaker(name="external_api")
        
        @cb.call
        async def call_api():
            return await external_api.get_data()
        ```
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ):
        """Inicializa o Circuit Breaker.
        
        Args:
            name: Nome identificador do circuit breaker
            config: Configuração customizada
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Executa função com proteção do circuit breaker.
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função
            
        Raises:
            CircuitBreakerError: Se o circuito estiver aberto
        """
        async with self._lock:
            self.stats.total_calls += 1
            
            # Verificar estado do circuito
            if self.stats.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    logger.info(
                        f"Circuit breaker '{self.name}' transitioning to HALF_OPEN",
                        circuit_breaker=self.name,
                        state="half_open"
                    )
                    self.stats.state = CircuitState.HALF_OPEN
                    self.stats.success_count = 0
                else:
                    logger.warning(
                        f"Circuit breaker '{self.name}' is OPEN, rejecting call",
                        circuit_breaker=self.name,
                        state="open"
                    )
                    raise CircuitBreakerError(
                        message=f"Circuit breaker '{self.name}' is open",
                        service_name=self.name
                    )
        
        # Executar função
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await self._on_success()
            return result
        
        except self.config.expected_exception as e:
            await self._on_failure()
            raise
    
    async def _on_success(self) -> None:
        """Callback de sucesso."""
        async with self._lock:
            self.stats.total_successes += 1
            self.stats.failure_count = 0
            
            if self.stats.state == CircuitState.HALF_OPEN:
                self.stats.success_count += 1
                
                if self.stats.success_count >= self.config.success_threshold:
                    logger.info(
                        f"Circuit breaker '{self.name}' closing after {self.stats.success_count} successes",
                        circuit_breaker=self.name,
                        state="closed"
                    )
                    self.stats.state = CircuitState.CLOSED
                    self.stats.success_count = 0
                    self.stats.last_state_change = datetime.utcnow()
    
    async def _on_failure(self) -> None:
        """Callback de falha."""
        async with self._lock:
            self.stats.total_failures += 1
            self.stats.failure_count += 1
            self.stats.last_failure_time = datetime.utcnow()
            self.stats.success_count = 0
            
            if self.stats.failure_count >= self.config.failure_threshold:
                if self.stats.state != CircuitState.OPEN:
                    logger.error(
                        f"Circuit breaker '{self.name}' opening after {self.stats.failure_count} failures",
                        circuit_breaker=self.name,
                        state="open",
                        failure_count=self.stats.failure_count
                    )
                    self.stats.state = CircuitState.OPEN
                    self.stats.last_state_change = datetime.utcnow()
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuito."""
        if self.stats.last_state_change is None:
            return True
        
        elapsed = (datetime.utcnow() - self.stats.last_state_change).total_seconds()
        return elapsed >= self.config.timeout
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do circuit breaker."""
        return {
            "name": self.name,
            "state": self.stats.state.value,
            "failure_count": self.stats.failure_count,
            "success_count": self.stats.success_count,
            "total_calls": self.stats.total_calls,
            "total_failures": self.stats.total_failures,
            "total_successes": self.stats.total_successes,
            "last_failure_time": self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None,
            "last_state_change": self.stats.last_state_change.isoformat(),
        }


# ============================================================================
# RETRY COM EXPONENTIAL BACKOFF
# ============================================================================

@dataclass
class RetryConfig:
    """Configuração de retry.
    
    Attributes:
        max_attempts: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        max_delay: Delay máximo em segundos
        exponential_base: Base para cálculo exponencial
        jitter: Se deve adicionar jitter aleatório
        retryable_exceptions: Tupla de exceções que devem ser retentadas
    """
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (Exception,)


class RetryExhaustedError(Exception):
    """Exceção quando todas as tentativas de retry falharam."""
    pass


async def retry_with_backoff(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    *args,
    **kwargs
) -> T:
    """Executa função com retry e exponential backoff.
    
    Args:
        func: Função a ser executada
        config: Configuração de retry
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
        
    Returns:
        Resultado da função
        
    Raises:
        RetryExhaustedError: Se todas as tentativas falharem
    """
    config = config or RetryConfig()
    last_exception = None
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            logger.debug(
                f"Retry attempt {attempt}/{config.max_attempts}",
                attempt=attempt,
                max_attempts=config.max_attempts
            )
            
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        
        except config.retryable_exceptions as e:
            last_exception = e
            
            if attempt == config.max_attempts:
                logger.error(
                    f"All retry attempts exhausted",
                    attempt=attempt,
                    max_attempts=config.max_attempts,
                    error=str(e)
                )
                break
            
            # Calcular delay com exponential backoff
            delay = min(
                config.initial_delay * (config.exponential_base ** (attempt - 1)),
                config.max_delay
            )
            
            # Adicionar jitter se configurado
            if config.jitter:
                delay = delay * (0.5 + random.random())
            
            logger.warning(
                f"Retry attempt {attempt} failed, waiting {delay:.2f}s",
                attempt=attempt,
                delay=delay,
                error=str(e)
            )
            
            await asyncio.sleep(delay)
    
    raise RetryExhaustedError(
        f"Failed after {config.max_attempts} attempts"
    ) from last_exception


def retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,)
):
    """Decorator para retry com exponential backoff.
    
    Args:
        max_attempts: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        max_delay: Delay máximo em segundos
        exponential_base: Base para cálculo exponencial
        jitter: Se deve adicionar jitter aleatório
        retryable_exceptions: Tupla de exceções que devem ser retentadas
        
    Example:
        ```python
        @retry(max_attempts=3, initial_delay=1.0)
        async def call_api():
            return await api.get_data()
        ```
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await retry_with_backoff(func, config, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Para funções síncronas, usar versão síncrona
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        break
                    
                    delay = min(
                        config.initial_delay * (config.exponential_base ** (attempt - 1)),
                        config.max_delay
                    )
                    
                    if config.jitter:
                        delay = delay * (0.5 + random.random())
                    
                    time.sleep(delay)
            
            raise RetryExhaustedError(
                f"Failed after {config.max_attempts} attempts"
            ) from last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ============================================================================
# TIMEOUT
# ============================================================================

async def with_timeout(
    func: Callable[..., T],
    timeout_seconds: float,
    *args,
    **kwargs
) -> T:
    """Executa função com timeout.
    
    Args:
        func: Função a ser executada
        timeout_seconds: Timeout em segundos
        *args: Argumentos posicionais
        **kwargs: Argumentos nomeados
        
    Returns:
        Resultado da função
        
    Raises:
        AppTimeoutError: Se exceder o timeout
    """
    try:
        if asyncio.iscoroutinefunction(func):
            return await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=timeout_seconds
            )
        else:
            # Para funções síncronas, executar em executor
            loop = asyncio.get_event_loop()
            return await asyncio.wait_for(
                loop.run_in_executor(None, func, *args, **kwargs),
                timeout=timeout_seconds
            )
    
    except asyncio.TimeoutError as e:
        logger.error(
            f"Operation timed out after {timeout_seconds}s",
            timeout_seconds=timeout_seconds
        )
        raise AppTimeoutError(
            message=f"Operation timed out after {timeout_seconds}s",
            timeout_seconds=timeout_seconds
        ) from e


def timeout(seconds: float):
    """Decorator para adicionar timeout a funções.
    
    Args:
        seconds: Timeout em segundos
        
    Example:
        ```python
        @timeout(30.0)
        async def slow_operation():
            await asyncio.sleep(60)  # Vai falhar
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await with_timeout(func, seconds, *args, **kwargs)
        
        return wrapper
    
    return decorator


# ============================================================================
# COMBINAÇÃO DE PADRÕES
# ============================================================================

class ResilientCall:
    """Combina múltiplos padrões de resiliência.
    
    Permite aplicar Circuit Breaker, Retry e Timeout em uma única chamada.
    
    Example:
        ```python
        resilient = ResilientCall(
            circuit_breaker=CircuitBreaker("api"),
            retry_config=RetryConfig(max_attempts=3),
            timeout_seconds=30.0
        )
        
        result = await resilient.execute(api.get_data)
        ```
    """
    
    def __init__(
        self,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_config: Optional[RetryConfig] = None,
        timeout_seconds: Optional[float] = None
    ):
        """Inicializa ResilientCall.
        
        Args:
            circuit_breaker: Circuit breaker a ser usado
            retry_config: Configuração de retry
            timeout_seconds: Timeout em segundos
        """
        self.circuit_breaker = circuit_breaker
        self.retry_config = retry_config
        self.timeout_seconds = timeout_seconds
    
    async def execute(
        self,
        func: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """Executa função com todos os padrões de resiliência.
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função
        """
        async def _execute():
            # Aplicar timeout se configurado
            if self.timeout_seconds:
                return await with_timeout(func, self.timeout_seconds, *args, **kwargs)
            else:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
        
        # Aplicar circuit breaker se configurado
        if self.circuit_breaker:
            async def _with_cb():
                return await self.circuit_breaker.call(_execute)
            
            target_func = _with_cb
        else:
            target_func = _execute
        
        # Aplicar retry se configurado
        if self.retry_config:
            return await retry_with_backoff(target_func, self.retry_config)
        else:
            return await target_func()


def resilient(
    circuit_breaker_name: Optional[str] = None,
    max_attempts: int = 3,
    timeout_seconds: Optional[float] = None,
    **retry_kwargs
):
    """Decorator que combina todos os padrões de resiliência.
    
    Args:
        circuit_breaker_name: Nome do circuit breaker
        max_attempts: Número máximo de tentativas
        timeout_seconds: Timeout em segundos
        **retry_kwargs: Argumentos adicionais para RetryConfig
        
    Example:
        ```python
        @resilient(
            circuit_breaker_name="external_api",
            max_attempts=3,
            timeout_seconds=30.0
        )
        async def call_api():
            return await api.get_data()
        ```
    """
    cb = CircuitBreaker(circuit_breaker_name) if circuit_breaker_name else None
    retry_config = RetryConfig(max_attempts=max_attempts, **retry_kwargs)
    
    resilient_call = ResilientCall(
        circuit_breaker=cb,
        retry_config=retry_config,
        timeout_seconds=timeout_seconds
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await resilient_call.execute(func, *args, **kwargs)
        
        return wrapper
    
    return decorator


__all__ = [
    # Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerConfig',
    'CircuitBreakerStats',
    'CircuitState',
    # Retry
    'retry',
    'retry_with_backoff',
    'RetryConfig',
    'RetryExhaustedError',
    # Timeout
    'timeout',
    'with_timeout',
    # Combinação
    'ResilientCall',
    'resilient',
]
