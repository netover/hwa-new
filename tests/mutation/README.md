# Mutation Testing Documentation

This directory contains documentation and configuration for mutation testing using mutmut to validate test effectiveness and code quality.

## Overview

Mutation testing is a technique that validates the quality of your test suite by introducing small changes (mutations) to your code and checking if your tests can detect these changes. A high mutation score indicates that your tests are effective at catching bugs.

## Configuration

Mutation testing is configured to run on the following core modules:

- `resync/core/agent_manager.py` - Agent lifecycle management
- `resync/core/ia_auditor.py` - AI-powered audit functionality
- `resync/core/async_cache.py` - Asynchronous caching system
- `resync/core/audit_lock.py` - Distributed locking for audit operations
- `resync/core/cache_hierarchy.py` - Multi-tier caching system

## Running Mutation Tests

### Prerequisites

1. Install mutmut:
   ```bash
   pip install mutmut
   ```

2. Ensure all tests pass:
   ```bash
   pytest tests/ --tb=short
   ```

### Execution

Run mutation testing using the dedicated script:

```bash
python scripts/mutation_test.py
```

Or run mutmut directly:

```bash
mutmut run --runner="pytest tests/ --tb=short" --timeout=10 --output-file=reports/mutation_results.json --exclude="tests/*,config/*,scripts/*,docs/*,static/*,templates/*" resync/core/agent_manager.py resync/core/ia_auditor.py resync/core/async_cache.py resync/core/audit_lock.py resync/core/cache_hierarchy.py
```

### Configuration Details

- **Test Runner**: `pytest tests/ --tb=short`
- **Timeout**: 10 seconds per mutation
- **Output**: `reports/mutation_results.json`
- **Excluded Paths**: Tests, config, scripts, docs, static files, templates

## Interpreting Results

### Mutation Score

The mutation score represents the percentage of mutations that were killed (detected) by your tests:

- **95-100%**: Excellent test coverage - tests are highly effective
- **85-94%**: Good test coverage - most bugs would be caught
- **70-84%**: Moderate test coverage - some bugs might slip through
- **<70%**: Poor test coverage - tests need significant improvement

### Success Criteria

The system must achieve:

1. **Mutation Score ≥ 95%** - At least 95% of mutations must be detected
2. **No survivors in critical paths** - Zero mutations should survive in:
   - Locking mechanisms (`audit_lock.py`)
   - Caching logic (`async_cache.py`, `cache_hierarchy.py`)
   - Audit functionality (`ia_auditor.py`)
   - Agent management (`agent_manager.py`)

## Handling Survived Mutants

When mutations survive (tests don't catch them), you have several options:

### 1. Improve Tests (Recommended)

Add or modify tests to catch the surviving mutations:

```python
# Example: If a mutation in cache logic survives
@pytest.mark.asyncio
async def test_cache_mutation_detection():
    """Test that catches mutations in cache behavior."""
    cache = AsyncTTLCache()
    await cache.set("key", "value")

    # This should detect mutations that break cache functionality
    assert await cache.get("key") == "value"
    assert await cache.get("nonexistent") is None
```

### 2. Accept Mutant (Use Sparingly)

If a mutation doesn't represent a real bug, you can accept it:

```bash
mutmut accept <mutant_id>
```

### 3. Skip Mutant (Use Sparingly)

If a mutation is not relevant to your codebase:

```bash
mutmut skip <mutant_id>
```

## Common Mutation Patterns

### Async Systems

Mutations in async code often involve:

- **Await removal**: `result = function()` instead of `result = await function()`
- **Lock bypass**: Missing `async with lock:` blocks
- **Exception handling**: Removed try/catch blocks

### Caching Systems

Mutations in caching logic typically involve:

- **Cache invalidation**: Missing `await cache.delete()` calls
- **TTL manipulation**: Incorrect TTL values
- **Race conditions**: Missing synchronization

### Audit Systems

Mutations in audit functionality often affect:

- **Lock acquisition**: Failed `await lock.acquire()` calls
- **Error handling**: Missing exception handling
- **Data validation**: Bypassed validation checks

## CI/CD Integration

Add mutation testing to your CI pipeline:

```yaml
- name: Run Mutation Tests
  run: |
    python scripts/mutation_test.py
  continue-on-error: false
  # Run after unit/integration tests pass
```

## Best Practices

1. **Run Regularly**: Execute mutation tests as part of your regular testing pipeline
2. **Fix Survivors**: Address surviving mutations promptly to maintain test quality
3. **Monitor Trends**: Track mutation scores over time to identify degrading test quality
4. **Balance Coverage**: Use mutation testing alongside traditional coverage metrics
5. **Focus on Critical Paths**: Prioritize mutations in security-sensitive and critical business logic

## Troubleshooting

### Windows Compatibility

mutmut has known compatibility issues on Windows due to the missing `resource` module. Consider:

- Running mutation tests in a Linux environment
- Using Windows Subsystem for Linux (WSL)
- Implementing alternative mutation testing approaches for Windows development

### Performance Issues

If mutation tests are too slow:

1. Increase timeout: `--timeout=30`
2. Run on fewer modules initially
3. Optimize your test suite for faster execution
4. Use parallel test execution if supported

### High Number of Survivors

If you have many surviving mutations:

1. Review test coverage for the affected modules
2. Add integration tests for complex interactions
3. Consider edge cases and error conditions
4. Verify that mutations represent real bugs before accepting them

## References

- [mutmut Documentation](https://mutmut.readthedocs.io/)
- [Mutation Testing Wikipedia](https://en.wikipedia.org/wiki/Mutation_testing)
- [Effective Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)
