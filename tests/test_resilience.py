"""Testes para padrões de resiliência."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock

from resync.core.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    retry,
    retry_with_backoff,
    RetryConfig,
    RetryExhaustedError,
    timeout,
    with_timeout,
    ResilientCall,
    resilient,
)
from resync.core.exceptions import CircuitBreakerError, TimeoutError as AppTimeoutError


# ============================================================================
# CIRCUIT BREAKER TESTS
# ============================================================================

class TestCircuitBreaker:
    """Testes para Circuit Breaker."""
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Testa estado CLOSED (funcionamento normal)."""
        cb = CircuitBreaker("test")
        
        async def success_func():
            return "success"
        
        result = await cb.call(success_func)
        
        assert result == "success"
        assert cb.stats.state == CircuitState.CLOSED
        assert cb.stats.total_successes == 1
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Testa que o circuito abre após threshold de falhas."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker("test", config)
        
        async def failing_func():
            raise ValueError("Test error")
        
        # Executar até atingir threshold
        for _ in range(3):
            with pytest.raises(ValueError):
                await cb.call(failing_func)
        
        assert cb.stats.state == CircuitState.OPEN
        assert cb.stats.failure_count == 3
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_rejects_when_open(self):
        """Testa que requisições são rejeitadas quando circuito está aberto."""
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker("test", config)
        
        async def failing_func():
            raise ValueError("Test error")
        
        # Abrir o circuito
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing_func)
        
        # Tentar chamar novamente - deve rejeitar
        with pytest.raises(CircuitBreakerError):
            await cb.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_transition(self):
        """Testa transição para HALF_OPEN após timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout=0.1  # 100ms
        )
        cb = CircuitBreaker("test", config)
        
        async def failing_func():
            raise ValueError("Test error")
        
        # Abrir o circuito
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing_func)
        
        assert cb.stats.state == CircuitState.OPEN
        
        # Aguardar timeout
        await asyncio.sleep(0.2)
        
        # Próxima chamada deve transitar para HALF_OPEN
        async def success_func():
            return "success"
        
        result = await cb.call(success_func)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closes_after_successes(self):
        """Testa que circuito fecha após sucessos em HALF_OPEN."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout=0.1
        )
        cb = CircuitBreaker("test", config)
        
        async def failing_func():
            raise ValueError("Test error")
        
        async def success_func():
            return "success"
        
        # Abrir o circuito
        for _ in range(2):
            with pytest.raises(ValueError):
                await cb.call(failing_func)
        
        # Aguardar timeout
        await asyncio.sleep(0.2)
        
        # Executar sucessos para fechar
        for _ in range(2):
            await cb.call(success_func)
        
        assert cb.stats.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_stats(self):
        """Testa estatísticas do circuit breaker."""
        cb = CircuitBreaker("test")
        
        async def success_func():
            return "success"
        
        await cb.call(success_func)
        
        stats = cb.get_stats()
        
        assert stats["name"] == "test"
        assert stats["state"] == "closed"
        assert stats["total_calls"] == 1
        assert stats["total_successes"] == 1
        assert stats["total_failures"] == 0


# ============================================================================
# RETRY TESTS
# ============================================================================

class TestRetry:
    """Testes para Retry com Exponential Backoff."""
    
    @pytest.mark.asyncio
    async def test_retry_success_on_first_attempt(self):
        """Testa sucesso na primeira tentativa."""
        call_count = 0
        
        async def success_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        config = RetryConfig(max_attempts=3)
        result = await retry_with_backoff(success_func, config)
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """Testa sucesso após algumas falhas."""
        call_count = 0
        
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01,
            jitter=False
        )
        result = await retry_with_backoff(flaky_func, config)
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Testa quando todas as tentativas falham."""
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")
        
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01,
            jitter=False
        )
        
        with pytest.raises(RetryExhaustedError):
            await retry_with_backoff(failing_func, config)
        
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_decorator(self):
        """Testa decorator de retry."""
        call_count = 0
        
        @retry(max_attempts=3, initial_delay=0.01, jitter=False)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = await flaky_func()
        
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_with_specific_exceptions(self):
        """Testa retry apenas para exceções específicas."""
        call_count = 0
        
        async def func_with_different_errors():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Retryable")
            raise TypeError("Not retryable")
        
        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01,
            retryable_exceptions=(ValueError,)
        )
        
        with pytest.raises(TypeError):
            await retry_with_backoff(func_with_different_errors, config)
        
        # Deve ter tentado apenas 2 vezes (1 ValueError, 1 TypeError)
        assert call_count == 2


# ============================================================================
# TIMEOUT TESTS
# ============================================================================

class TestTimeout:
    """Testes para Timeout."""
    
    @pytest.mark.asyncio
    async def test_timeout_success(self):
        """Testa operação que completa dentro do timeout."""
        async def fast_func():
            await asyncio.sleep(0.01)
            return "success"
        
        result = await with_timeout(fast_func, 1.0)
        
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """Testa operação que excede o timeout."""
        async def slow_func():
            await asyncio.sleep(1.0)
            return "success"
        
        with pytest.raises(AppTimeoutError):
            await with_timeout(slow_func, 0.1)
    
    @pytest.mark.asyncio
    async def test_timeout_decorator(self):
        """Testa decorator de timeout."""
        @timeout(0.1)
        async def slow_func():
            await asyncio.sleep(1.0)
            return "success"
        
        with pytest.raises(AppTimeoutError):
            await slow_func()


# ============================================================================
# RESILIENT CALL TESTS
# ============================================================================

class TestResilientCall:
    """Testes para ResilientCall (combinação de padrões)."""
    
    @pytest.mark.asyncio
    async def test_resilient_call_with_all_patterns(self):
        """Testa ResilientCall com todos os padrões."""
        call_count = 0
        
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary error")
            return "success"
        
        cb = CircuitBreaker("test")
        retry_config = RetryConfig(
            max_attempts=3,
            initial_delay=0.01,
            jitter=False
        )
        
        resilient_call = ResilientCall(
            circuit_breaker=cb,
            retry_config=retry_config,
            timeout_seconds=1.0
        )
        
        result = await resilient_call.execute(flaky_func)
        
        assert result == "success"
        assert call_count == 2
        assert cb.stats.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_resilient_decorator(self):
        """Testa decorator resilient."""
        call_count = 0
        
        @resilient(
            circuit_breaker_name="test",
            max_attempts=3,
            timeout_seconds=1.0,
            initial_delay=0.01,
            jitter=False
        )
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = await flaky_func()
        
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_resilient_call_circuit_breaker_opens(self):
        """Testa que circuit breaker abre em ResilientCall."""
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker("test", config)
        retry_config = RetryConfig(max_attempts=1)
        
        resilient_call = ResilientCall(
            circuit_breaker=cb,
            retry_config=retry_config
        )
        
        async def failing_func():
            raise ValueError("Error")
        
        # Falhar até abrir o circuito
        for _ in range(2):
            with pytest.raises((ValueError, RetryExhaustedError)):
                await resilient_call.execute(failing_func)
        
        # Próxima chamada deve ser rejeitada pelo circuit breaker
        with pytest.raises(CircuitBreakerError):
            await resilient_call.execute(failing_func)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Testes de integração."""
    
    @pytest.mark.asyncio
    async def test_real_world_scenario(self):
        """Testa cenário real com serviço externo instável."""
        call_count = 0
        
        @resilient(
            circuit_breaker_name="external_api",
            max_attempts=5,
            timeout_seconds=2.0,
            initial_delay=0.01,
            jitter=False
        )
        async def call_external_api():
            nonlocal call_count
            call_count += 1
            
            # Simular serviço instável
            if call_count <= 2:
                raise ConnectionError("Service unavailable")
            
            await asyncio.sleep(0.1)
            return {"data": "success"}
        
        result = await call_external_api()
        
        assert result == {"data": "success"}
        assert call_count == 3  # Falhou 2x, sucesso na 3ª


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
