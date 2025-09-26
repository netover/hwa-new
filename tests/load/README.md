# Load Testing for Audit Processing

This directory contains comprehensive load testing for the audit processing system, designed to validate system behavior under high concurrency scenarios.

## Overview

The load tests simulate realistic production load with 100+ concurrent audit requests to ensure the system maintains performance and reliability under stress.

## Test Structure

### `test_audit_load.py`

Contains the main load test suite with:

- **Concurrent Audit Processing**: Simulates 120+ concurrent audit requests using `asyncio.gather()`
- **Mock Dependencies**: Uses `MockAuditQueue` and `MockIAAuditor` to isolate testing from external dependencies
- **Metrics Collection**: Tracks latency percentiles, error rates, memory usage, and lock contention
- **System Validation**: Ensures 0 duplicate flagging, <1% error rate, <500ms p99 latency, and no memory leaks

## Running Load Tests

### Prerequisites

Ensure the following dependencies are installed:
```bash
pip install pytest pytest-asyncio
```

### Basic Execution

Run the load test with:
```bash
pytest tests/load/test_audit_load.py::test_audit_load_test -v
```

### With Timeout (CI/CD)

For CI/CD integration with a 120-second timeout:
```bash
pytest tests/load/test_audit_load.py::test_audit_load_test --timeout=120 -v
```

### Custom Configuration

You can modify test parameters in the test file:
- `NUM_CONCURRENT_REQUESTS`: Number of concurrent requests (default: 120)
- `TIMEOUT_SECONDS`: Test timeout in seconds (default: 10)
- Error rate threshold: <1%
- Latency thresholds: p99 < 500ms

## Metrics and Validation

### Key Metrics Collected

1. **Total Processing Time**: Time to complete all concurrent requests
2. **Error Rate**: Percentage of failed requests (must be <1%)
3. **Latency Percentiles**:
   - P50: Median response time
   - P90: 90th percentile response time
   - P99: 99th percentile response time (must be <500ms)
4. **Lock Contention Rate**: Redis lock acquisition failures
5. **Memory Usage**: Before/after comparison to detect leaks
6. **Concurrent Process Count**: Number of active processes

### System Invariants Verified

- **Zero Duplicate Flagging**: No memory records flagged multiple times
- **Error Rate < 1%**: System maintains reliability under load
- **P99 Latency < 500ms**: Response times remain acceptable
- **No Memory Leaks**: Memory usage stable throughout test
- **Lock Contention < 1%**: Redis locks acquired efficiently

## Interpreting Results

### Sample Output
```
📊 LOAD TEST RESULTS:
   Total requests: 120
   Successful: 118
   Failed: 2 (1.67%)
   Total time: 45.123s
   Average latency: 0.376s
   P50 latency: 0.342s
   P90 latency: 0.421s
   P99 latency: 0.478s
   Lock contention: 1 (0.83%)
   Mock memory usage: stable (no leaks detected)
```

### Success Criteria

The test passes if:
- ✅ Error rate < 1%
- ✅ P99 latency < 500ms
- ✅ No duplicate flagging incidents
- ✅ Lock contention < 1%
- ✅ Total time < 60 seconds for 120 requests
- ✅ No memory leaks detected

### Failure Scenarios

1. **High Error Rate**: Indicates system instability under load
2. **High Latency**: Suggests performance bottlenecks
3. **Duplicate Flagging**: Race condition in audit processing
4. **Memory Leaks**: Resource management issues
5. **Lock Contention**: Redis lock configuration problems

## CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
- name: Run Load Tests
  run: |
    pytest tests/load/test_audit_load.py::test_audit_load_test --timeout=120 -v
  continue-on-error: false
```

## Troubleshooting

### Common Issues

1. **Timeout Errors**: Increase `TIMEOUT_SECONDS` or reduce `NUM_CONCURRENT_REQUESTS`
2. **High Error Rates**: Check mock configurations and system resources
3. **Memory Issues**: Monitor system memory during test execution
4. **Lock Contention**: Review Redis configuration and connection pooling

### Debugging

Enable detailed logging by modifying the test:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

Based on load test results, consider:

1. **Connection Pooling**: Increase Redis connection pool size
2. **Async Optimization**: Review async/await patterns in audit processing
3. **Resource Scaling**: Scale Redis or add more worker processes
4. **Caching**: Implement caching for frequently accessed data
5. **Monitoring**: Add production monitoring for key metrics

## Maintenance

- Review and update test parameters based on production load patterns
- Monitor system performance regularly and adjust thresholds as needed
- Update mock configurations to reflect changes in the actual system
- Run load tests as part of regression testing for major changes
