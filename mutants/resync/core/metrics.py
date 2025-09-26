from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, DefaultDict

# --- Logging Setup ---
logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class MetricsRegistry:
    """
    A simple, in-memory registry for collecting application metrics.

    This class provides a basic mechanism for counters and gauges. It is not
    intended to replace robust monitoring solutions like Prometheus, but serves
    as a lightweight, built-in tool for tracking key application events.
    """

    def xǁMetricsRegistryǁ__init____mutmut_orig(self) -> None:
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        logger.info("MetricsRegistry initialized.")

    def xǁMetricsRegistryǁ__init____mutmut_1(self) -> None:
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = None
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        logger.info("MetricsRegistry initialized.")

    def xǁMetricsRegistryǁ__init____mutmut_2(self) -> None:
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = defaultdict(None)
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        logger.info("MetricsRegistry initialized.")

    def xǁMetricsRegistryǁ__init____mutmut_3(self) -> None:
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = None
        logger.info("MetricsRegistry initialized.")

    def xǁMetricsRegistryǁ__init____mutmut_4(self) -> None:
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = defaultdict(None)
        logger.info("MetricsRegistry initialized.")

    def xǁMetricsRegistryǁ__init____mutmut_5(self) -> None:
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        logger.info(None)

    def xǁMetricsRegistryǁ__init____mutmut_6(self) -> None:
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        logger.info("XXMetricsRegistry initialized.XX")

    def xǁMetricsRegistryǁ__init____mutmut_7(self) -> None:
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        logger.info("metricsregistry initialized.")

    def xǁMetricsRegistryǁ__init____mutmut_8(self) -> None:
        """Initializes the registry with empty dictionaries for counters and gauges."""
        self.counters: DefaultDict[str, int] = defaultdict(int)
        self.gauges: DefaultDict[str, float] = defaultdict(float)
        logger.info("METRICSREGISTRY INITIALIZED.")

    xǁMetricsRegistryǁ__init____mutmut_mutants: ClassVar[MutantDict] = {
        "xǁMetricsRegistryǁ__init____mutmut_1": xǁMetricsRegistryǁ__init____mutmut_1,
        "xǁMetricsRegistryǁ__init____mutmut_2": xǁMetricsRegistryǁ__init____mutmut_2,
        "xǁMetricsRegistryǁ__init____mutmut_3": xǁMetricsRegistryǁ__init____mutmut_3,
        "xǁMetricsRegistryǁ__init____mutmut_4": xǁMetricsRegistryǁ__init____mutmut_4,
        "xǁMetricsRegistryǁ__init____mutmut_5": xǁMetricsRegistryǁ__init____mutmut_5,
        "xǁMetricsRegistryǁ__init____mutmut_6": xǁMetricsRegistryǁ__init____mutmut_6,
        "xǁMetricsRegistryǁ__init____mutmut_7": xǁMetricsRegistryǁ__init____mutmut_7,
        "xǁMetricsRegistryǁ__init____mutmut_8": xǁMetricsRegistryǁ__init____mutmut_8,
    }

    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁMetricsRegistryǁ__init____mutmut_orig"),
            object.__getattribute__(self, "xǁMetricsRegistryǁ__init____mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    __init__.__signature__ = _mutmut_signature(xǁMetricsRegistryǁ__init____mutmut_orig)
    xǁMetricsRegistryǁ__init____mutmut_orig.__name__ = "xǁMetricsRegistryǁ__init__"

    def xǁMetricsRegistryǁincrement_counter__mutmut_orig(
        self, name: str, value: int = 1
    ) -> None:
        """
        Increments a counter metric by a given value.

        Args:
            name: The name of the counter.
            value: The integer value to add to the counter. Defaults to 1.
        """
        self.counters[name] += value
        logger.debug(f"Counter '{name}' incremented to {self.counters[name]}")

    def xǁMetricsRegistryǁincrement_counter__mutmut_1(
        self, name: str, value: int = 2
    ) -> None:
        """
        Increments a counter metric by a given value.

        Args:
            name: The name of the counter.
            value: The integer value to add to the counter. Defaults to 1.
        """
        self.counters[name] += value
        logger.debug(f"Counter '{name}' incremented to {self.counters[name]}")

    def xǁMetricsRegistryǁincrement_counter__mutmut_2(
        self, name: str, value: int = 1
    ) -> None:
        """
        Increments a counter metric by a given value.

        Args:
            name: The name of the counter.
            value: The integer value to add to the counter. Defaults to 1.
        """
        self.counters[name] = value
        logger.debug(f"Counter '{name}' incremented to {self.counters[name]}")

    def xǁMetricsRegistryǁincrement_counter__mutmut_3(
        self, name: str, value: int = 1
    ) -> None:
        """
        Increments a counter metric by a given value.

        Args:
            name: The name of the counter.
            value: The integer value to add to the counter. Defaults to 1.
        """
        self.counters[name] -= value
        logger.debug(f"Counter '{name}' incremented to {self.counters[name]}")

    def xǁMetricsRegistryǁincrement_counter__mutmut_4(
        self, name: str, value: int = 1
    ) -> None:
        """
        Increments a counter metric by a given value.

        Args:
            name: The name of the counter.
            value: The integer value to add to the counter. Defaults to 1.
        """
        self.counters[name] += value
        logger.debug(None)

    xǁMetricsRegistryǁincrement_counter__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁMetricsRegistryǁincrement_counter__mutmut_1": xǁMetricsRegistryǁincrement_counter__mutmut_1,
        "xǁMetricsRegistryǁincrement_counter__mutmut_2": xǁMetricsRegistryǁincrement_counter__mutmut_2,
        "xǁMetricsRegistryǁincrement_counter__mutmut_3": xǁMetricsRegistryǁincrement_counter__mutmut_3,
        "xǁMetricsRegistryǁincrement_counter__mutmut_4": xǁMetricsRegistryǁincrement_counter__mutmut_4,
    }

    def increment_counter(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁMetricsRegistryǁincrement_counter__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁMetricsRegistryǁincrement_counter__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    increment_counter.__signature__ = _mutmut_signature(
        xǁMetricsRegistryǁincrement_counter__mutmut_orig
    )
    xǁMetricsRegistryǁincrement_counter__mutmut_orig.__name__ = (
        "xǁMetricsRegistryǁincrement_counter"
    )

    def xǁMetricsRegistryǁset_gauge__mutmut_orig(self, name: str, value: float) -> None:
        """
        Sets a gauge metric to a specific value.

        Args:
            name: The name of the gauge.
            value: The float value to set the gauge to.
        """
        self.gauges[name] = value
        logger.debug(f"Gauge '{name}' set to {self.gauges[name]}")

    def xǁMetricsRegistryǁset_gauge__mutmut_1(self, name: str, value: float) -> None:
        """
        Sets a gauge metric to a specific value.

        Args:
            name: The name of the gauge.
            value: The float value to set the gauge to.
        """
        self.gauges[name] = None
        logger.debug(f"Gauge '{name}' set to {self.gauges[name]}")

    def xǁMetricsRegistryǁset_gauge__mutmut_2(self, name: str, value: float) -> None:
        """
        Sets a gauge metric to a specific value.

        Args:
            name: The name of the gauge.
            value: The float value to set the gauge to.
        """
        self.gauges[name] = value
        logger.debug(None)

    xǁMetricsRegistryǁset_gauge__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁMetricsRegistryǁset_gauge__mutmut_1": xǁMetricsRegistryǁset_gauge__mutmut_1,
        "xǁMetricsRegistryǁset_gauge__mutmut_2": xǁMetricsRegistryǁset_gauge__mutmut_2,
    }

    def set_gauge(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁMetricsRegistryǁset_gauge__mutmut_orig"),
            object.__getattribute__(
                self, "xǁMetricsRegistryǁset_gauge__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    set_gauge.__signature__ = _mutmut_signature(
        xǁMetricsRegistryǁset_gauge__mutmut_orig
    )
    xǁMetricsRegistryǁset_gauge__mutmut_orig.__name__ = "xǁMetricsRegistryǁset_gauge"

    def xǁMetricsRegistryǁget_metrics__mutmut_orig(self) -> dict[str, Any]:
        """
        Returns a snapshot of all current metrics.

        Returns:
            A dictionary containing all counters and gauges.
        """
        return {"counters": dict(self.counters), "gauges": dict(self.gauges)}

    def xǁMetricsRegistryǁget_metrics__mutmut_1(self) -> dict[str, Any]:
        """
        Returns a snapshot of all current metrics.

        Returns:
            A dictionary containing all counters and gauges.
        """
        return {"XXcountersXX": dict(self.counters), "gauges": dict(self.gauges)}

    def xǁMetricsRegistryǁget_metrics__mutmut_2(self) -> dict[str, Any]:
        """
        Returns a snapshot of all current metrics.

        Returns:
            A dictionary containing all counters and gauges.
        """
        return {"COUNTERS": dict(self.counters), "gauges": dict(self.gauges)}

    def xǁMetricsRegistryǁget_metrics__mutmut_3(self) -> dict[str, Any]:
        """
        Returns a snapshot of all current metrics.

        Returns:
            A dictionary containing all counters and gauges.
        """
        return {"counters": dict(None), "gauges": dict(self.gauges)}

    def xǁMetricsRegistryǁget_metrics__mutmut_4(self) -> dict[str, Any]:
        """
        Returns a snapshot of all current metrics.

        Returns:
            A dictionary containing all counters and gauges.
        """
        return {"counters": dict(self.counters), "XXgaugesXX": dict(self.gauges)}

    def xǁMetricsRegistryǁget_metrics__mutmut_5(self) -> dict[str, Any]:
        """
        Returns a snapshot of all current metrics.

        Returns:
            A dictionary containing all counters and gauges.
        """
        return {"counters": dict(self.counters), "GAUGES": dict(self.gauges)}

    def xǁMetricsRegistryǁget_metrics__mutmut_6(self) -> dict[str, Any]:
        """
        Returns a snapshot of all current metrics.

        Returns:
            A dictionary containing all counters and gauges.
        """
        return {"counters": dict(self.counters), "gauges": dict(None)}

    xǁMetricsRegistryǁget_metrics__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁMetricsRegistryǁget_metrics__mutmut_1": xǁMetricsRegistryǁget_metrics__mutmut_1,
        "xǁMetricsRegistryǁget_metrics__mutmut_2": xǁMetricsRegistryǁget_metrics__mutmut_2,
        "xǁMetricsRegistryǁget_metrics__mutmut_3": xǁMetricsRegistryǁget_metrics__mutmut_3,
        "xǁMetricsRegistryǁget_metrics__mutmut_4": xǁMetricsRegistryǁget_metrics__mutmut_4,
        "xǁMetricsRegistryǁget_metrics__mutmut_5": xǁMetricsRegistryǁget_metrics__mutmut_5,
        "xǁMetricsRegistryǁget_metrics__mutmut_6": xǁMetricsRegistryǁget_metrics__mutmut_6,
    }

    def get_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁMetricsRegistryǁget_metrics__mutmut_orig"),
            object.__getattribute__(
                self, "xǁMetricsRegistryǁget_metrics__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    get_metrics.__signature__ = _mutmut_signature(
        xǁMetricsRegistryǁget_metrics__mutmut_orig
    )
    xǁMetricsRegistryǁget_metrics__mutmut_orig.__name__ = (
        "xǁMetricsRegistryǁget_metrics"
    )

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_orig(self) -> str:
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

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_1(self) -> str:
        """
        Generates metrics in Prometheus text exposition format.
        """
        output = None

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

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_2(self) -> str:
        """
        Generates metrics in Prometheus text exposition format.
        """
        output = []

        # Counters
        for name, value in self.counters.items():
            # Example: # HELP my_counter_total My counter description.
            # # TYPE my_counter_total counter
            # my_counter_total 123
            output.append(None)
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

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_3(self) -> str:
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
            output.append(None)
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

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_4(self) -> str:
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
            output.append(None)

        # Gauges
        for name, value in self.gauges.items():
            # Example: # HELP my_gauge My gauge description.
            # # TYPE my_gauge gauge
            # my_gauge 45.6
            output.append(f"# HELP {name} Automatically generated gauge.\n")
            output.append(f"# TYPE {name} gauge\n")
            output.append(f"{name} {value}\n")

        return "".join(output)

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_5(self) -> str:
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
            output.append(None)
            output.append(f"# TYPE {name} gauge\n")
            output.append(f"{name} {value}\n")

        return "".join(output)

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_6(self) -> str:
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
            output.append(None)
            output.append(f"{name} {value}\n")

        return "".join(output)

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_7(self) -> str:
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
            output.append(None)

        return "".join(output)

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_8(self) -> str:
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

        return "".join(None)

    def xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_9(self) -> str:
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

        return "XXXX".join(output)

    xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_mutants: ClassVar[
        MutantDict
    ] = {
        "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_1": xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_1,
        "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_2": xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_2,
        "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_3": xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_3,
        "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_4": xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_4,
        "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_5": xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_5,
        "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_6": xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_6,
        "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_7": xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_7,
        "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_8": xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_8,
        "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_9": xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_9,
    }

    def generate_prometheus_metrics(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(
                self, "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_orig"
            ),
            object.__getattribute__(
                self, "xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_mutants"
            ),
            args,
            kwargs,
            self,
        )
        return result

    generate_prometheus_metrics.__signature__ = _mutmut_signature(
        xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_orig
    )
    xǁMetricsRegistryǁgenerate_prometheus_metrics__mutmut_orig.__name__ = (
        "xǁMetricsRegistryǁgenerate_prometheus_metrics"
    )

    def xǁMetricsRegistryǁreset__mutmut_orig(self) -> None:
        """Resets all metrics back to their default state."""
        self.counters.clear()
        self.gauges.clear()
        logger.info("MetricsRegistry has been reset.")

    def xǁMetricsRegistryǁreset__mutmut_1(self) -> None:
        """Resets all metrics back to their default state."""
        self.counters.clear()
        self.gauges.clear()
        logger.info(None)

    def xǁMetricsRegistryǁreset__mutmut_2(self) -> None:
        """Resets all metrics back to their default state."""
        self.counters.clear()
        self.gauges.clear()
        logger.info("XXMetricsRegistry has been reset.XX")

    def xǁMetricsRegistryǁreset__mutmut_3(self) -> None:
        """Resets all metrics back to their default state."""
        self.counters.clear()
        self.gauges.clear()
        logger.info("metricsregistry has been reset.")

    def xǁMetricsRegistryǁreset__mutmut_4(self) -> None:
        """Resets all metrics back to their default state."""
        self.counters.clear()
        self.gauges.clear()
        logger.info("METRICSREGISTRY HAS BEEN RESET.")

    xǁMetricsRegistryǁreset__mutmut_mutants: ClassVar[MutantDict] = {
        "xǁMetricsRegistryǁreset__mutmut_1": xǁMetricsRegistryǁreset__mutmut_1,
        "xǁMetricsRegistryǁreset__mutmut_2": xǁMetricsRegistryǁreset__mutmut_2,
        "xǁMetricsRegistryǁreset__mutmut_3": xǁMetricsRegistryǁreset__mutmut_3,
        "xǁMetricsRegistryǁreset__mutmut_4": xǁMetricsRegistryǁreset__mutmut_4,
    }

    def reset(self, *args, **kwargs):
        result = _mutmut_trampoline(
            object.__getattribute__(self, "xǁMetricsRegistryǁreset__mutmut_orig"),
            object.__getattribute__(self, "xǁMetricsRegistryǁreset__mutmut_mutants"),
            args,
            kwargs,
            self,
        )
        return result

    reset.__signature__ = _mutmut_signature(xǁMetricsRegistryǁreset__mutmut_orig)
    xǁMetricsRegistryǁreset__mutmut_orig.__name__ = "xǁMetricsRegistryǁreset"


# --- Singleton Instance ---
# Create a single, globally accessible instance of the MetricsRegistry.
metrics_registry = MetricsRegistry()
