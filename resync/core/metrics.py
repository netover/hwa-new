from __future__ import annotations

import logging
from collections import defaultdict
from typing import DefaultDict

# --- Logging Setup ---
logger = logging.getLogger(__name__)


class MetricsRegistry:
    """
    A simple, in-memory registry for collecting application metrics.

    This class provides a basic mechanism for counters and gauges. It is not
    intended to replace robust monitoring solutions like Prometheus, but serves
    as a lightweight, built-in tool for tracking key application events.
    """

    def __init__(self):
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        logger.info("MetricsRegistry initialized.")

    def increment_counter(self, name: str, value: int = 1):
        """
        Increments a counter metric by a given value.

        Args:
            name: The name of the counter.
            value: The integer value to add to the counter. Defaults to 1.
        """
        self.counters[name] += value
        logger.debug(f"Counter '{name}' incremented to {self.counters[name]}")

    def set_gauge(self, name: str, value: float):
        """
        Sets a gauge metric to a specific value.

        Args:
            name: The name of the gauge.
            value: The float value to set the gauge to.
        """
        self.gauges[name] = value
        logger.debug(f"Gauge '{name}' set to {self.gauges[name]}")

    def get_metrics(self) -> dict:
        """
        Returns a snapshot of all current metrics.

        Returns:
            A dictionary containing all counters and gauges.
        """
        return {"counters": dict(self.counters), "gauges": dict(self.gauges)}

    def generate_prometheus_metrics(self) -> str:
        """
        Generates metrics in Prometheus text exposition format.
        """
        output = []

        # Counters
        for name, value in self.counters.items():
            # Example: # HELP my_counter_total My counter description.
            # # TYPE my_counter_total counter
            # my_counter_total 123
            output.append(f"# HELP {name}_total Automatically generated counter.\n")
            output.append(f"# TYPE {name}_total counter\n")
            output.append(f"{name}_total {value}\n")

        # Gauges
        for name, value in self.gauges.items():
            # Example: # HELP my_gauge My gauge description.
            # # TYPE my_gauge gauge
            # my_gauge 45.6
            output.append(f"# HELP {name} Automatically generated gauge.\n")
            output.append(f"# TYPE {name} gauge\n")
            output.append(f"{name} {value}\n")
        
        return "".join(output)

    def reset(self):
        """Resets all metrics back to their default state."""
        self.counters.clear()
        self.gauges.clear()
        logger.info("MetricsRegistry has been reset.")


# --- Singleton Instance ---
# Create a single, globally accessible instance of the MetricsRegistry.
metrics_registry = MetricsRegistry()