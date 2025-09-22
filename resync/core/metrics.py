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

    def reset(self):
        """Resets all metrics back to their default state."""
        self.counters.clear()
        self.gauges.clear()
        logger.info("MetricsRegistry has been reset.")


# --- Singleton Instance ---
# Create a single, globally accessible instance of the MetricsRegistry.
metrics_registry = MetricsRegistry()
