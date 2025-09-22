from collections import defaultdict
from typing import Any, DefaultDict, Dict


class MetricsRegistry:
    """
    Um registro simples e centralizado para métricas da aplicação.
    Este é um stub que pode ser expandido para se integrar com sistemas
    de monitoramento como Prometheus, StatsD ou Datadog.
    """
    def __init__(self) -> None:
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        # Latency/timing pode ser mais complexo, por agora vamos usar uma lista simples
        self.timings: DefaultDict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, value: int = 1) -> None:
        """Incrementa um contador."""
        self.counters[name] += value
        print(f"METRIC_COUNTER: {name} incremented by {value}")

    def set_gauge(self, name: str, value: float) -> None:
        """Define o valor de um medidor."""
        self.gauges[name] = value
        print(f"METRIC_GAUGE: {name} set to {value}")

    def add_timing(self, name: str, value: float) -> None:
        """Adiciona uma medição de tempo."""
        self.timings[name].append(value)
        print(f"METRIC_TIMING: {name} recorded as {value}")

    def get_all_metrics(self) -> Dict[str, Any]:
        """Retorna todas as métricas coletadas."""
        return {
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "timings": dict(self.timings),
        }

# Instância única para ser usada em toda a aplicação
metrics_registry = MetricsRegistry()
