# Background Tasks Fixture

This document explains how to use the `background_tasks` pytest fixture for testing code that creates background tasks with `asyncio.create_task()`.

## Overview

The `background_tasks` fixture allows you to:
1. Intercept calls to `asyncio.create_task()`
2. Store the coroutines for later execution
3. Manually execute tasks in a controlled manner
4. Test background task behavior deterministically

## Installation

The fixture is automatically available to all tests in the `tests/` directory because it's defined in `tests/conftest.py`.

## Usage

### Basic Usage

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_my_background_task(background_tasks):
    # Start capturing background tasks
    background_tasks.start_capturing()
    
    # Define an async function
    async def my_task():
        return "task_result"
    
    # Create a background task (will be captured, not executed)
    asyncio.create_task(my_task())
    
    # Verify the task was captured
    assert background_tasks.task_count == 1
    
    # Execute the task manually
    results = await background_tasks.run_all_async()
    
    # Verify the result
    assert results[0] == "task_result"
```

### With the Chat API Example

```python
import asyncio
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_chat_api_background_task(background_tasks):
    from resync.api.chat import run_auditor_safely
    
    # Start capturing tasks
    background_tasks.start_capturing()
    
    # Mock dependencies to avoid actual processing
    with patch("resync.api.chat.analyze_and_flag_memories") as mock_analyze:
        mock_analyze.return_value = {"processed": 1, "deleted": 0, "flagged": 0}
        
        # Create the background task as done in the chat API
        asyncio.create_task(run_auditor_safely())
        
        # Verify task was captured
        assert background_tasks.task_count == 1
        
        # Execute the task manually
        results = await background_tasks.run_all_async()
        
        # Verify execution
        assert len(results) == 1
        mock_analyze.assert_called_once()
```

## API Reference

### `background_tasks` Fixture Methods

#### `start_capturing()`
Start intercepting calls to `asyncio.create_task()`.

#### `stop_capturing()`
Stop intercepting calls to `asyncio.create_task()`.

#### `reset()`
Clear all captured tasks.

#### `captured_tasks`
Property that returns a list of captured tasks as tuples: `(coroutine, args, kwargs)`.

#### `task_count`
Property that returns the number of captured tasks.

#### `run_all_async()`
Execute all captured tasks asynchronously and return their results.

#### `run_all_sync()`
Execute all captured tasks synchronously and return their results.

## Benefits

1. **Deterministic Testing**: Control exactly when background tasks execute
2. **Isolation**: Prevent background tasks from interfering with test execution
3. **Verification**: Easily verify that background tasks are created correctly
4. **Mocking**: Combine with mocking to test complex background task interactions

## Best Practices

1. Always call `background_tasks.start_capturing()` before creating tasks you want to capture
2. Use `background_tasks.reset()` between test phases if needed
3. Call `background_tasks.stop_capturing()` when you want to allow normal task execution
4. Use `run_all_async()` for async tasks and `run_all_sync()` for sync tasks
5. Mock external dependencies when testing background tasks to keep tests focused

## Example Test File

See `tests/test_background_tasks.py` for comprehensive examples of how to use this fixture.