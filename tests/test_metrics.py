"""Tests for resync.core.metrics module."""

import pytest
from unittest.mock import Mock, patch
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from resync.core.metrics import MetricsRegistry, metrics_registry


class TestMetricsRegistry:
    """Test MetricsRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create a fresh MetricsRegistry instance."""
        return MetricsRegistry()

    def test_registry_initialization(self, registry):
        """Test that registry initializes with empty metrics."""
        assert len(registry.counters) == 0
        assert len(registry.gauges) == 0

    def test_increment_counter_new(self, registry):
        """Test incrementing a new counter."""
        registry.increment_counter("test_counter")
        assert registry.counters["test_counter"] == 1

    def test_increment_counter_existing(self, registry):
        """Test incrementing an existing counter."""
        registry.increment_counter("test_counter")
        registry.increment_counter("test_counter")
        registry.increment_counter("test_counter")
        assert registry.counters["test_counter"] == 3

    def test_increment_counter_with_value(self, registry):
        """Test incrementing counter with custom value."""
        registry.increment_counter("test_counter", 5)
        assert registry.counters["test_counter"] == 5
        
        registry.increment_counter("test_counter", 3)
        assert registry.counters["test_counter"] == 8

    def test_increment_counter_with_zero(self, registry):
        """Test incrementing counter with zero value."""
        registry.increment_counter("test_counter", 0)
        assert registry.counters["test_counter"] == 0

    def test_increment_counter_with_negative(self, registry):
        """Test incrementing counter with negative value."""
        registry.increment_counter("test_counter", 10)
        registry.increment_counter("test_counter", -3)
        assert registry.counters["test_counter"] == 7

    def test_set_gauge(self, registry):
        """Test setting gauge values."""
        registry.set_gauge("test_gauge", 42.5)
        assert registry.gauges["test_gauge"] == 42.5

    def test_set_gauge_overwrite(self, registry):
        """Test overwriting gauge values."""
        registry.set_gauge("test_gauge", 100.0)
        registry.set_gauge("test_gauge", 200.0)
        assert registry.gauges["test_gauge"] == 200.0

    def test_set_gauge_different_types(self, registry):
        """Test setting gauge with different numeric types."""
        registry.set_gauge("int_gauge", 42)
        registry.set_gauge("float_gauge", 42.5)
        registry.set_gauge("zero_gauge", 0.0)
        registry.set_gauge("negative_gauge", -10.5)
        
        assert registry.gauges["int_gauge"] == 42
        assert registry.gauges["float_gauge"] == 42.5
        assert registry.gauges["zero_gauge"] == 0.0
        assert registry.gauges["negative_gauge"] == -10.5

    def test_get_metrics_empty(self, registry):
        """Test getting metrics when registry is empty."""
        metrics = registry.get_metrics()
        
        assert "counters" in metrics
        assert "gauges" in metrics
        assert len(metrics["counters"]) == 0
        assert len(metrics["gauges"]) == 0

    def test_get_metrics_with_data(self, registry):
        """Test getting metrics with data."""
        # Add some test data
        registry.increment_counter("test_counter", 5)
        registry.set_gauge("test_gauge", 42.5)
        
        metrics = registry.get_metrics()
        
        assert metrics["counters"]["test_counter"] == 5
        assert metrics["gauges"]["test_gauge"] == 42.5

    def test_get_metrics_immutability(self, registry):
        """Test that returned metrics don't affect internal state."""
        registry.increment_counter("test_counter", 5)
        metrics = registry.get_metrics()
        
        # Modify returned metrics
        metrics["counters"]["test_counter"] = 999
        metrics["counters"]["new_counter"] = 123
        
        # Original should be unchanged
        original_metrics = registry.get_metrics()
        assert original_metrics["counters"]["test_counter"] == 5
        assert "new_counter" not in original_metrics["counters"]

    def test_reset_metrics(self, registry):
        """Test resetting all metrics."""
        # Add some test data
        registry.increment_counter("test_counter", 5)
        registry.set_gauge("test_gauge", 42.5)
        
        # Verify data exists
        metrics = registry.get_metrics()
        assert len(metrics["counters"]) == 1
        assert len(metrics["gauges"]) == 1
        
        # Reset and verify empty
        registry.reset()
        metrics = registry.get_metrics()
        assert len(metrics["counters"]) == 0
        assert len(metrics["gauges"]) == 0

    def test_generate_prometheus_metrics_empty(self, registry):
        """Test generating Prometheus metrics when empty."""
        prometheus_output = registry.generate_prometheus_metrics()
        assert prometheus_output == ""

    def test_generate_prometheus_metrics_with_data(self, registry):
        """Test generating Prometheus metrics with data."""
        registry.increment_counter("requests", 100)
        registry.set_gauge("cpu_usage", 75.5)
        
        prometheus_output = registry.generate_prometheus_metrics()
        
        # Check counter format
        assert "# HELP requests_total Automatically generated counter." in prometheus_output
        assert "# TYPE requests_total counter" in prometheus_output
        assert "requests_total 100" in prometheus_output
        
        # Check gauge format
        assert "# HELP cpu_usage Automatically generated gauge." in prometheus_output
        assert "# TYPE cpu_usage gauge" in prometheus_output
        assert "cpu_usage 75.5" in prometheus_output

    def test_concurrent_counter_increments(self, registry):
        """Test concurrent counter increments."""
        def increment_counter():
            for _ in range(100):
                registry.increment_counter("concurrent_counter")
        
        # Run multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=increment_counter)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have 10 threads * 100 increments = 1000
        assert registry.counters["concurrent_counter"] == 1000

    def test_concurrent_gauge_sets(self, registry):
        """Test concurrent gauge setting."""
        def set_gauge(value):
            registry.set_gauge("concurrent_gauge", float(value))
        
        values = list(range(100))
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(set_gauge, value) for value in values]
            
            # Wait for all to complete
            for future in as_completed(futures):
                future.result()
        
        # Final value should be one of the set values
        final_value = registry.gauges["concurrent_gauge"]
        assert final_value in values

    def test_metrics_with_special_characters(self, registry):
        """Test metrics with special characters in names."""
        special_names = [
            "metric-with-dashes",
            "metric_with_underscores", 
            "metric.with.dots",
            "metric/with/slashes",
            "metric:with:colons"
        ]
        
        for name in special_names:
            registry.increment_counter(name)
            registry.set_gauge(name, 42.0)
        
        metrics = registry.get_metrics()
        
        for name in special_names:
            assert name in metrics["counters"]
            assert name in metrics["gauges"]

    def test_large_metric_names(self, registry):
        """Test metrics with very long names."""
        long_name = "a" * 1000  # 1000 character name
        
        registry.increment_counter(long_name)
        registry.set_gauge(long_name, 42.0)
        
        metrics = registry.get_metrics()
        assert long_name in metrics["counters"]
        assert long_name in metrics["gauges"]

    def test_multiple_metrics_performance(self, registry):
        """Test performance with many metrics."""
        # Add many counters and gauges
        for i in range(1000):
            registry.increment_counter(f"counter_{i}")
            registry.set_gauge(f"gauge_{i}", float(i))
        
        # Getting metrics should be fast
        start_time = time.time()
        metrics = registry.get_metrics()
        end_time = time.time()
        
        assert end_time - start_time < 1.0  # Should take less than 1 second
        assert len(metrics["counters"]) == 1000
        assert len(metrics["gauges"]) == 1000

    def test_prometheus_format_special_characters(self, registry):
        """Test Prometheus format with special characters in metric names."""
        registry.increment_counter("metric-name", 5)
        registry.set_gauge("gauge.name", 10.5)
        
        prometheus_output = registry.generate_prometheus_metrics()
        
        # Should handle special characters in names
        assert "metric-name_total 5" in prometheus_output
        assert "gauge.name 10.5" in prometheus_output

    def test_defaultdict_behavior(self, registry):
        """Test that counters and gauges use defaultdict behavior."""
        # Accessing non-existent counter should return 0
        assert registry.counters["non_existent_counter"] == 0
        
        # Accessing non-existent gauge should return 0.0
        assert registry.gauges["non_existent_gauge"] == 0.0
        
        # After access, they should exist in the collections
        assert "non_existent_counter" in registry.counters
        assert "non_existent_gauge" in registry.gauges


class TestGlobalMetricsRegistry:
    """Test the global metrics registry instance."""

    def test_global_registry_exists(self):
        """Test that global registry instance exists."""
        assert metrics_registry is not None
        assert isinstance(metrics_registry, MetricsRegistry)

    def test_global_registry_functionality(self):
        """Test basic functionality of global registry."""
        # Clear any existing metrics
        metrics_registry.reset()
        
        # Test basic operations
        metrics_registry.increment_counter("global_test_counter")
        metrics_registry.set_gauge("global_test_gauge", 123.0)
        
        metrics = metrics_registry.get_metrics()
        
        assert metrics["counters"]["global_test_counter"] == 1
        assert metrics["gauges"]["global_test_gauge"] == 123.0
        
        # Clean up
        metrics_registry.reset()

    def test_global_registry_persistence(self):
        """Test that global registry persists across imports."""
        # Clear and set a value
        metrics_registry.reset()
        metrics_registry.increment_counter("persistence_test")
        
        # Import again and check value persists
        from resync.core.metrics import metrics_registry as imported_registry
        
        metrics = imported_registry.get_metrics()
        assert metrics["counters"]["persistence_test"] == 1
        
        # Clean up
        metrics_registry.reset()

    def test_global_registry_thread_safety(self):
        """Test thread safety of global registry."""
        metrics_registry.reset()
        
        def worker():
            for i in range(100):
                metrics_registry.increment_counter("thread_safety_test")
                metrics_registry.set_gauge("thread_gauge", float(i))
        
        # Run multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        metrics = metrics_registry.get_metrics()
        
        # Counter should have 5 threads * 100 increments = 500
        assert metrics["counters"]["thread_safety_test"] == 500
        
        # Gauge should have some final value
        assert "thread_gauge" in metrics["gauges"]
        
        # Clean up
        metrics_registry.reset()

    def test_global_registry_prometheus_output(self):
        """Test Prometheus output from global registry."""
        metrics_registry.reset()
        
        metrics_registry.increment_counter("http_requests", 150)
        metrics_registry.set_gauge("memory_usage", 85.5)
        
        prometheus_output = metrics_registry.generate_prometheus_metrics()
        
        assert "http_requests_total 150" in prometheus_output
        assert "memory_usage 85.5" in prometheus_output
        
        # Clean up
        metrics_registry.reset()

    def test_global_registry_concurrent_access(self):
        """Test concurrent access to global registry."""
        metrics_registry.reset()
        
        def counter_worker():
            for _ in range(50):
                metrics_registry.increment_counter("concurrent_test")
        
        def gauge_worker():
            for i in range(50):
                metrics_registry.set_gauge("concurrent_gauge", float(i))
        
        # Run mixed workload
        threads = []
        for _ in range(3):
            threads.append(threading.Thread(target=counter_worker))
        for _ in range(2):
            threads.append(threading.Thread(target=gauge_worker))
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        metrics = metrics_registry.get_metrics()
        
        # Should have processed all counter increments
        assert metrics["counters"]["concurrent_test"] == 150  # 3 threads * 50
        
        # Gauge should have some final value
        assert "concurrent_gauge" in metrics["gauges"]
        
        # Clean up
        metrics_registry.reset()

    def test_global_registry_logging(self):
        """Test that logging occurs for global registry operations."""
        with patch('resync.core.metrics.logger') as mock_logger:
            metrics_registry.reset()
            
            metrics_registry.increment_counter("log_test")
            metrics_registry.set_gauge("log_gauge", 42.0)
            metrics_registry.reset()
            
            # Should have logged debug messages for increment and set operations
            assert mock_logger.debug.call_count >= 2
            assert mock_logger.info.call_count >= 2  # At least one for init, one for reset