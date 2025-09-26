# AsyncIteratorMock - Comprehensive Guide

## Overview

The `AsyncIteratorMock` is a robust testing utility designed to mock asynchronous iterators, particularly for testing streaming responses from AI agents like `agent.stream()`. It provides comprehensive features for simulating realistic streaming behavior in tests.

## Features

- ✅ **Multiple Data Types**: Support for text, JSON, dictionaries, and bytes
- ✅ **Configurable Delays**: Simulate realistic streaming delays between chunks
- ✅ **Error Injection**: Test error handling during streaming
- ✅ **Type Safety**: Full type annotations and validation
- ✅ **Flexible Configuration**: Extensive options for customizing behavior
- ✅ **Edge Case Handling**: Robust handling of various edge cases

## Installation

The `AsyncIteratorMock` is included in the test suite and doesn't require separate installation. Import it as:

```python
from tests.async_iterator_mock import AsyncIteratorMock, StreamChunk, StreamChunkType, create_text_stream, create_json_stream, create_mixed_stream
```

## Basic Usage

### Simple Text Streaming

```python
from tests.async_iterator_mock import AsyncIteratorMock

# Create a simple text stream
mock = AsyncIteratorMock(["Hello", " ", "World", "!"])

# Use in async context
async for chunk in mock:
    print(chunk)
# Output: Hello World !
```

### Text Stream with Delays

```python
# Simulate realistic streaming with delays
mock = AsyncIteratorMock(
    ["Processing", ".", ".", ".", " Complete!"],
    delay_between_chunks=0.1  # 100ms delay between chunks
)

async for chunk in mock:
    print(chunk, end="", flush=True)
# Output: Processing.... Complete! (with 100ms delays)
```

### Text Stream from String

```python
# Automatically split text into chunks
mock = AsyncIteratorMock.from_text(
    "This is a long text that will be split into chunks",
    chunk_size=20,
    delay_between_chunks=0.05
)

async for chunk in mock:
    print(f"[{chunk}]")
```

## Advanced Usage

### Mixed Data Types

```python
from tests.async_iterator_mock import StreamChunk, StreamChunkType

# Create chunks with different types
chunks = [
    StreamChunk("Starting analysis", StreamChunkType.TEXT, delay_before=0.1),
    StreamChunk({"status": "thinking"}, StreamChunkType.JSON, delay_before=0.2),
    StreamChunk("Analysis complete", StreamChunkType.TEXT, delay_before=0.1)
]

mock = AsyncIteratorMock.from_chunks(chunks)

async for chunk in mock:
    print(chunk)
```

### JSON Streaming

```python
# Stream structured data as JSON
data = {
    "id": "123",
    "status": "processing",
    "progress": 0.75,
    "message": "Almost done..."
}

mock = AsyncIteratorMock([data], delay_between_chunks=0.1)

async for chunk in mock:
    print(f"JSON: {chunk}")
```

### Error Injection

```python
# Test error handling during streaming
mock = AsyncIteratorMock(
    ["Chunk 1", "Chunk 2", "Chunk 3"],
    error_at_index=1,  # Error after first chunk
    error_type=ConnectionError("Network timeout")
)

try:
    async for chunk in mock:
        print(chunk)
except ConnectionError as e:
    print(f"Handled error: {e}")
```

## Convenience Functions

### create_text_stream()

```python
from tests.async_iterator_mock import create_text_stream

# Quick text streaming
mock = create_text_stream("Hello World", chunk_size=5, delay=0.1)

async for chunk in mock:
    print(chunk)
```

### create_json_stream()

```python
from tests.async_iterator_mock import create_json_stream

# Stream structured data
data = {"name": "John", "age": 30, "city": "New York"}
mock = create_json_stream(data, delay=0.1)

async for chunk in mock:
    print(chunk)
```

### create_mixed_stream()

```python
from tests.async_iterator_mock import create_mixed_stream

# Mixed content types
chunks = [
    "Processing request...",
    {"status": "loading", "progress": 50},
    "Request completed!"
]

mock = create_mixed_stream(chunks, delay=0.1)

async for chunk in mock:
    print(chunk)
```

## Agent Streaming Mock

### Mocking agent.stream() Response

```python
# Mock a realistic agent response
agent_response = "I understand your question about TWS job management. Based on the system status, I can help you restart the failed job. Let me provide you with the correct procedure step by step."

mock = create_text_stream(agent_response, chunk_size=50, delay=0.05)

# In your test
async def test_agent_stream():
    agent = create_mock_agent()
    agent.stream.return_value = mock

    response = ""
    async for chunk in agent.stream("How do I restart a job?"):
        response += chunk

    assert "TWS job management" in response
    assert "restart the failed job" in response
```

### Mocking with Metadata

```python
# Advanced streaming with metadata
chunks = [
    StreamChunk("Analyzing query", StreamChunkType.TEXT,
                metadata={"tokens_used": 3}, delay_before=0.1),
    StreamChunk({"thinking": "Job restart procedure"}, StreamChunkType.JSON,
                metadata={"tokens_used": 8}, delay_before=0.2),
    StreamChunk("Here's how to restart:", StreamChunkType.TEXT,
                metadata={"tokens_used": 5}, delay_before=0.1)
]

mock = AsyncIteratorMock.from_chunks(chunks)
```

## Configuration Options

### Constructor Parameters

```python
mock = AsyncIteratorMock(
    items=["chunk1", "chunk2", "chunk3"],
    delay_between_chunks=0.1,        # Default delay between chunks
    error_at_index=1,                # Inject error at index 1
    error_type=ValueError("Test"),   # Type of error to inject
    auto_convert_types=True,         # Auto-detect chunk types
    chunk_size=50                    # Split large text into chunks
)
```

### StreamChunk Configuration

```python
chunk = StreamChunk(
    content="Hello World",           # The actual content
    chunk_type=StreamChunkType.TEXT, # Type of content
    metadata={"source": "agent"},    # Optional metadata
    delay_before=0.1                 # Delay before this chunk
)
```

## Best Practices

### 1. Realistic Chunk Sizes
```python
# Use appropriate chunk sizes for your use case
small_chunks = AsyncIteratorMock.from_text("Long text", chunk_size=10)
medium_chunks = AsyncIteratorMock.from_text("Long text", chunk_size=50)
large_chunks = AsyncIteratorMock.from_text("Long text", chunk_size=200)
```

### 2. Appropriate Delays
```python
# Simulate different streaming speeds
fast_stream = AsyncIteratorMock(["a", "b", "c"], delay_between_chunks=0.01)
normal_stream = AsyncIteratorMock(["a", "b", "c"], delay_between_chunks=0.1)
slow_stream = AsyncIteratorMock(["a", "b", "c"], delay_between_chunks=0.5)
```

### 3. Error Testing
```python
# Test various error scenarios
network_error = AsyncIteratorMock(["ok"], error_at_index=0, error_type=ConnectionError())
timeout_error = AsyncIteratorMock(["ok"], error_at_index=0, error_type=TimeoutError())
custom_error = AsyncIteratorMock(["ok"], error_at_index=0, error_type=ValueError("Custom"))
```

### 4. Type Consistency
```python
# Be consistent with data types in your tests
text_stream = AsyncIteratorMock(["text", "chunks", "only"])
mixed_stream = AsyncIteratorMock([
    "text",
    {"json": "data"},
    "more text"
], auto_convert_types=True)
```

## Testing Patterns

### Pattern 1: Simple Response Testing
```python
async def test_simple_response():
    mock = AsyncIteratorMock(["Hello", " ", "World"])
    result = await mock.to_list_async()
    assert result == ["Hello", " ", "World"]
```

### Pattern 2: Streaming Response Testing
```python
async def test_streaming_response():
    mock = AsyncIteratorMock(["Processing", ".", ".", "."], delay_between_chunks=0.1)

    chunks = []
    async for chunk in mock:
        chunks.append(chunk)

    assert len(chunks) == 4
    assert chunks[0] == "Processing"
    assert chunks[3] == "."
```

### Pattern 3: Error Handling Testing
```python
async def test_stream_error_handling():
    mock = AsyncIteratorMock(
        ["Good", "Bad"],
        error_at_index=1,
        error_type=ValueError("Stream failed")
    )

    with pytest.raises(ValueError, match="Stream failed"):
        async for chunk in mock:
            if chunk == "Bad":
                break  # Simulate early termination
```

### Pattern 4: Performance Testing
```python
async def test_stream_performance():
    large_text = "A" * 1000  # 1000 character text
    mock = AsyncIteratorMock.from_text(large_text, chunk_size=10, delay_between_chunks=0.001)

    start_time = time.time()
    chunks = await mock.to_list_async()
    end_time = time.time()

    assert len(chunks) == 100  # 1000/10 = 100 chunks
    assert end_time - start_time < 1.0  # Should complete quickly
```

## Common Pitfalls

### 1. Forgetting Async Context
```python
# ❌ Wrong - blocking usage
mock = AsyncIteratorMock(["test"])
for chunk in mock:  # This won't work
    print(chunk)

# ✅ Correct - async usage
async def example():
    async for chunk in mock:
        print(chunk)
```

### 2. Incorrect Error Index
```python
# ❌ Wrong - index out of range
mock = AsyncIteratorMock(["a", "b"], error_at_index=5)  # IndexError

# ✅ Correct - valid index
mock = AsyncIteratorMock(["a", "b", "c"], error_at_index=1)  # Error after "a"
```

### 3. Mixing Chunk Types Incorrectly
```python
# ❌ Wrong - inconsistent types
mock = AsyncIteratorMock([
    "text",
    123,  # Inconsistent type
    {"key": "value"}  # Mixed types without proper configuration
])

# ✅ Correct - consistent types or proper configuration
mock = AsyncIteratorMock([
    "text",
    "123",
    '{"key": "value"}'
], auto_convert_types=False)
```

## Integration with Existing Tests

### Migrating from Basic Lists

```python
# Before (basic)
async def test_old_way():
    mock = AsyncIteratorMock(["chunk1", "chunk2"])
    # ... test code

# After (enhanced)
async def test_new_way():
    mock = create_text_stream("chunk1 chunk2", chunk_size=10)
    # ... same test code, more realistic
```

### Adding Error Testing

```python
# Before (no error testing)
async def test_without_errors():
    mock = AsyncIteratorMock(["success"])
    # ... test only success case

# After (comprehensive testing)
async def test_with_error_handling():
    # Test success case
    success_mock = AsyncIteratorMock(["success"])

    # Test error case
    error_mock = AsyncIteratorMock(
        ["success"],
        error_at_index=0,
        error_type=ConnectionError()
    )

    # Test both scenarios
```

## Troubleshooting

### Issue: Iterator Not Working in Async Context
**Problem**: Using synchronous iteration on async iterator
**Solution**: Always use `async for` with AsyncIteratorMock

### Issue: No Chunks Being Yielded
**Problem**: Empty items list or exhausted iterator
**Solution**: Check `mock.is_exhausted()` or call `mock.reset()`

### Issue: Unexpected Delays
**Problem**: Delay configuration not set correctly
**Solution**: Check `delay_between_chunks` parameter and `StreamChunk.delay_before`

### Issue: Type Errors
**Problem**: Incorrect data types or type conversion issues
**Solution**: Use `auto_convert_types=True` or specify `StreamChunkType` explicitly

## Examples in Test Files

See `test_integration.py` for complete examples of how AsyncIteratorMock is used in real test scenarios, including:

- Basic streaming response testing
- Error handling during streaming
- Integration with WebSocket endpoints
- Performance testing with large datasets

## Contributing

When extending AsyncIteratorMock:

1. Maintain backward compatibility
2. Add comprehensive tests
3. Update this documentation
4. Follow existing code style and patterns
5. Add type annotations for new features
