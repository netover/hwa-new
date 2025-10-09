"""
Testes unitários para o sistema de resiliência do Resync

Testa Circuit Breaker, Exponential Backoff, Timeout Manager
e decoradores de resiliência.

Author: Resync Team
Date: October 2025
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from resync.core.exceptions import CircuitBreakerError, TimeoutError
from resync.core.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    RetryWithBackoff,
    RetryConfig,
    TimeoutManager,
    circuit_breaker,
    retry_with_backoff,
    with_timeout,
    get_circuit_breaker_metrics
)


class TestCircuitBreaker:
    """Testes para o Circuit Breaker"""

    @pytest.fixture
    def config(self):
        return CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=1,  # 1 segundo para testes
            name="test_circuit"
        )

    @pytest.fixture
    def circuit_breaker_instance(self, config):
        return CircuitBreaker(config)

    @pytest.mark.asyncio
    async def test_successful_call(self, circuit_breaker_instance):
        """Testa chamada bem-sucedida"""

        async def success_func():
            return "success"

        result = await circuit_breaker_instance.call(success_func)
        assert result == "success"
        assert circuit_breaker_instance.metrics.successful_calls == 1
        assert circuit_breaker_instance.metrics.failed_calls == 0

    @pytest.mark.asyncio
    async def test_failure_then_success(self, circuit_breaker_instance):
        """Testa falha seguida de sucesso"""

        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First call fails")
            return "success"

        # Primeira chamada falha
        with pytest.raises(ValueError):
            await circuit_breaker_instance.call(failing_func)

        assert circuit_breaker_instance.metrics.failed_calls == 1

        # Segunda chamada tem sucesso
        result = await circuit_breaker_instance.call(failing_func)
        assert result == "success"
        assert circuit_breaker_instance.metrics.successful_calls == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens(self, circuit_breaker_instance):
        """Testa abertura do circuit breaker após falhas consecutivas"""

        async def always_fail():
            raise ValueError("Always fails")

        # Primeira falha
        with pytest.raises(ValueError):
            await circuit_breaker_instance.call(always_fail)

        # Segunda falha - circuit abre
        with pytest.raises(ValueError):
            await circuit_breaker_instance.call(always_fail)

        # Terceira chamada - circuit está aberto
        with pytest.raises(CircuitBreakerError):
            await circuit_breaker_instance.call(always_fail)

        assert circuit_breaker_instance.state.value == "open"

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self, circuit_breaker_instance):
        """Testa recuperação do circuit breaker para half-open"""

        async def always_fail():
            raise ValueError("Always fails")

        # Abrir circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                await circuit_breaker_instance.call(always_fail)

        assert circuit_breaker_instance.state.value == "open"

        # Aguardar tempo de recuperação
        await asyncio.sleep(1.1)

        # Próxima chamada deve ir para half-open e ainda falhar
        # (já que always_fail sempre falha)
        with pytest.raises(ValueError):
            await circuit_breaker_instance.call(always_fail)

    @pytest.mark.asyncio
    async def test_circuit_breaker_reset_after_success(self, circuit_breaker_instance):
        """Testa reset do circuit breaker após sucesso"""

        call_count = 0

        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # Falha duas vezes
                raise ValueError("Fails")
            return "success"

        # Abrir circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                await circuit_breaker_instance.call(fail_then_succeed)

        assert circuit_breaker_instance.state.value == "open"

        # Aguardar recuperação
        await asyncio.sleep(1.1)

        # Chamada de teste bem-sucedida - circuit volta para closed
        result = await circuit_breaker_instance.call(fail_then_succeed)
        assert result == "success"
        assert circuit_breaker_instance.state.value == "closed"

    def test_get_metrics(self, circuit_breaker_instance):
        """Testa obtenção de métricas"""
        metrics = circuit_breaker_instance.get_metrics()

        assert "name" in metrics
        assert "state" in metrics
        assert "total_calls" in metrics
        assert "successful_calls" in metrics
        assert "failed_calls" in metrics
        assert "success_rate" in metrics
        assert metrics["name"] == "test_circuit"
        assert metrics["state"] == "closed"


class TestRetryWithBackoff:
    """Testes para Retry com Exponential Backoff"""

    @pytest.fixture
    def config(self):
        return RetryConfig(
            max_retries=3,
            base_delay=0.1,  # Delay curto para testes
            max_delay=1.0,
            jitter=False  # Desabilitar jitter para testes determinísticos
        )

    @pytest.fixture
    def retry_instance(self, config):
        return RetryWithBackoff(config)

    @pytest.mark.asyncio
    async def test_successful_first_attempt(self, retry_instance):
        """Testa sucesso na primeira tentativa"""

        async def success_func():
            return "success"

        result = await retry_instance.execute(success_func)
        assert result == "success"
        assert retry_instance.metrics.successful_attempts == 1
        assert retry_instance.metrics.failed_attempts == 0

    @pytest.mark.asyncio
    async def test_retry_after_failure(self, retry_instance):
        """Testa retry após falha"""

        call_count = 0

        async def fail_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Attempt {call_count} failed")
            return "success"

        start_time = time.time()
        result = await retry_instance.execute(fail_then_succeed)
        end_time = time.time()

        assert result == "success"
        assert call_count == 3
        assert retry_instance.metrics.successful_attempts == 1

        # Verificar que houve delay (aproximadamente 0.1 + 0.2 = 0.3 segundos)
        elapsed = end_time - start_time
        assert elapsed >= 0.25  # Pelo menos 250ms de delay

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, retry_instance):
        """Testa quando máximo de retries é excedido"""

        async def always_fail():
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            await retry_instance.execute(always_fail)

        assert retry_instance.metrics.failed_attempts == 1

    @pytest.mark.asyncio
    async def test_exponential_backoff_delays(self, retry_instance):
        """Testa delays exponenciais"""

        delays = []

        async def failing_func():
            delays.append(time.time())
            raise ValueError("Fails")

        start_time = time.time()
        with pytest.raises(ValueError):
            await retry_instance.execute(failing_func)

        # Verificar delays: tentativa inicial + 3 retries = 4 tentativas
        assert len(delays) == 4
        # Verificar delays crescentes (0.1, 0.2, 0.4 aproximadamente)
        assert delays[1] - delays[0] >= 0.08  # ~0.1s entre primeira e segunda
        assert delays[2] - delays[1] >= 0.18  # ~0.2s entre segunda e terceira
        assert delays[3] - delays[2] >= 0.38  # ~0.4s entre terceira e quarta

    def test_get_metrics(self, retry_instance):
        """Testa obtenção de métricas"""
        metrics = retry_instance.get_metrics()

        assert "total_attempts" in metrics
        assert "successful_attempts" in metrics
        assert "failed_attempts" in metrics
        assert "success_rate" in metrics
        assert "average_retry_delay" in metrics


class TestTimeoutManager:
    """Testes para Timeout Manager"""

    @pytest.mark.asyncio
    async def test_successful_operation_within_timeout(self):
        """Testa operação bem-sucedida dentro do timeout"""

        async def quick_operation():
            await asyncio.sleep(0.1)
            return "success"

        result = await TimeoutManager.with_timeout(quick_operation(), 1.0)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """Testa quando timeout é excedido"""

        async def slow_operation():
            await asyncio.sleep(2.0)
            return "success"

        with pytest.raises(TimeoutError):
            await TimeoutManager.with_timeout(slow_operation(), 0.5)

    @pytest.mark.asyncio
    async def test_custom_timeout_exception(self):
        """Testa exceção customizada de timeout"""

        class CustomTimeoutError(Exception):
            pass

        async def slow_operation():
            await asyncio.sleep(1.0)
            return "success"

        with pytest.raises(CustomTimeoutError):
            await TimeoutManager.with_timeout(
                slow_operation(),
                0.5,
                CustomTimeoutError("Custom timeout")
            )


class TestDecorators:
    """Testes para decoradores de resiliência"""

    @pytest.mark.asyncio
    async def test_circuit_breaker_decorator(self):
        """Testa decorator de circuit breaker"""

        call_count = 0

        @circuit_breaker(failure_threshold=2, recovery_timeout=1, name="test_decorator")
        async def decorated_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ValueError("Fails")
            return "success"

        # Primeiras chamadas falham
        for _ in range(2):
            with pytest.raises(ValueError):
                await decorated_func()

        # Circuit abre
        with pytest.raises(CircuitBreakerError):
            await decorated_func()

        # Verificar se circuit breaker foi anexado
        assert hasattr(decorated_func, 'circuit_breaker')
        assert decorated_func.circuit_breaker.config.name == "test_decorator"

    @pytest.mark.asyncio
    async def test_retry_decorator(self):
        """Testa decorator de retry"""

        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.1, jitter=False)
        async def decorated_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError(f"Attempt {call_count}")
            return "success"

        result = await decorated_func()
        assert result == "success"
        assert call_count == 3

        # Verificar se retry handler foi anexado
        assert hasattr(decorated_func, 'retry_handler')

    @pytest.mark.asyncio
    async def test_timeout_decorator(self):
        """Testa decorator de timeout"""

        @with_timeout(1.0)
        async def quick_func():
            await asyncio.sleep(0.1)
            return "success"

        result = await quick_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_timeout_decorator_exceeded(self):
        """Testa decorator de timeout quando excedido"""

        @with_timeout(0.2)
        async def slow_func():
            await asyncio.sleep(0.5)
            return "success"

        with pytest.raises(TimeoutError):
            await slow_func()


class TestIntegration:
    """Testes de integração dos padrões de resiliência"""

    @pytest.mark.asyncio
    async def test_combined_patterns(self):
        """Testa combinação de múltiplos padrões"""

        call_count = 0

        @circuit_breaker(failure_threshold=3, recovery_timeout=1, name="combined_test")
        @retry_with_backoff(max_retries=2, base_delay=0.1, jitter=False)
        @with_timeout(2.0)
        async def resilient_func():
            nonlocal call_count
            call_count += 1

            if call_count <= 5:  # Circuit abre após algumas falhas
                await asyncio.sleep(0.05)  # Operação rápida
                raise ValueError(f"Attempt {call_count}")
            else:
                return "success"

        # Executar múltiplas vezes - algumas falharão
        for i in range(10):
            try:
                result = await resilient_func()
                if result == "success":
                    break
            except (ValueError, CircuitBreakerError):
                continue

        # Verificar que teve múltiplas tentativas
        assert call_count > 2


class TestMetrics:
    """Testes de métricas e monitoramento"""

    def test_get_circuit_breaker_metrics_empty(self):
        """Testa obtenção de métricas quando não há circuit breakers"""
        metrics = get_circuit_breaker_metrics()
        assert isinstance(metrics, dict)
        # Pode estar vazio ou ter circuit breakers de outros testes

    @pytest.mark.asyncio
    async def test_circuit_breaker_metrics_collection(self):
        """Testa coleta de métricas de circuit breaker"""

        @circuit_breaker(failure_threshold=2, recovery_timeout=1, name="metrics_test")
        async def test_func():
            return "success"

        # Executar algumas chamadas
        for _ in range(3):
            await test_func()

        # Obter métricas globais
        all_metrics = get_circuit_breaker_metrics()

        # Verificar se nosso circuit breaker está nas métricas
        assert "metrics_test" in all_metrics
        metrics = all_metrics["metrics_test"]

        assert metrics["total_calls"] >= 3
        assert metrics["successful_calls"] >= 3
        assert "state" in metrics
        assert "success_rate" in metrics


# Fixtures para configuração de testes

@pytest.fixture(autouse=True)
def reset_circuit_breakers():
    """Reseta circuit breakers entre testes"""
    # Limpar circuit breakers globais se necessário
    yield
    # Cleanup se necessário


@pytest.fixture
def event_loop():
    """Cria event loop para testes assíncronos"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()