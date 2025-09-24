"""
AsyncIteratorMock - A comprehensive mock for testing async iterators.

This module provides a robust AsyncIteratorMock class that can be used to mock
asynchronous iterators in tests, particularly for testing agent.stream() methods.

The mock supports various data types, streaming delays, error injection, and
comprehensive configuration options.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union, AsyncIterator
from dataclasses import dataclass
from enum import Enum


class StreamChunkType(Enum):
    """Types of data that can be streamed."""
    TEXT = "text"
    JSON = "json"
    DICT = "dict"
    BYTES = "bytes"


@dataclass
class StreamChunk:
    """Represents a single chunk in the stream with optional metadata."""
    content: Any
    chunk_type: StreamChunkType = StreamChunkType.TEXT
    metadata: Optional[Dict[str, Any]] = None
    delay_before: float = 0.0  # Delay in seconds before yielding this chunk


class AsyncIteratorMock:
    """
    A comprehensive mock class that implements the asynchronous iterator protocol.

    This class can be used to mock asynchronous iterators in tests, allowing
    for controlled iteration over a sequence of items with proper async/await support.

    Features:
    - Support for multiple data types (text, JSON, dict, bytes)
    - Configurable streaming delays
    - Error injection capabilities
    - Comprehensive configuration options
    - Type safety with proper annotations
    - Edge case handling

    Examples:
        Basic usage:
        ```python
        # Simple text streaming
        mock = AsyncIteratorMock(["Hello", " ", "World"])
        async for chunk in mock:
            print(chunk)
        ```

        Advanced usage with mixed types:
        ```python
        chunks = [
            StreamChunk("Processing", chunk_type=StreamChunkType.TEXT, delay_before=0.1),
            StreamChunk({"status": "thinking"}, chunk_type=StreamChunkType.JSON, delay_before=0.2),
            StreamChunk("Done!", chunk_type=StreamChunkType.TEXT)
        ]
        mock = AsyncIteratorMock.from_chunks(chunks)
        ```

        Error injection:
        ```python
        mock = AsyncIteratorMock(
            ["Chunk 1", "Chunk 2"],
            error_at_index=1,  # Raise error after first chunk
            error_type=ValueError("Test error")
        )
        ```
    """

    def __init__(
        self,
        items: Union[List[Any], List[StreamChunk]],
        delay_between_chunks: float = 0.0,
        error_at_index: Optional[int] = None,
        error_type: Optional[Exception] = None,
        auto_convert_types: bool = True,
        chunk_size: Optional[int] = None
    ):
        """
        Initialize the AsyncIteratorMock.

        Args:
            items: List of items or StreamChunk objects to iterate over
            delay_between_chunks: Default delay between chunks in seconds
            error_at_index: Index at which to inject an error (None for no error)
            error_type: Exception to raise at the specified index
            auto_convert_types: Whether to auto-detect and convert chunk types
            chunk_size: If specified, split large content into chunks of this size

        Raises:
            ValueError: If configuration is invalid
        """
        self.delay_between_chunks = delay_between_chunks
        self.error_at_index = error_at_index
        self.error_type = error_type or RuntimeError("Mock stream error")
        self.auto_convert_types = auto_convert_types

        # Process items into StreamChunk objects
        self.chunks = self._process_items(items, chunk_size)
        self.index = 0

        # Validate error configuration
        if error_at_index is not None and (error_at_index < 0 or error_at_index >= len(self.chunks)):
            raise ValueError(f"error_at_index {error_at_index} is out of range [0, {len(self.chunks)-1}]")

    def _process_items(self, items: Union[List[Any], List[StreamChunk]], chunk_size: Optional[int]) -> List[StreamChunk]:
        """Process raw items into StreamChunk objects."""
        chunks = []

        for item in items:
            if isinstance(item, StreamChunk):
                chunks.append(item)
            else:
                # Auto-detect type if enabled
                chunk_type = StreamChunkType.TEXT
                if self.auto_convert_types:
                    chunk_type = self._detect_chunk_type(item)

                # Split large content if chunk_size is specified
                if chunk_size and isinstance(item, str) and len(item) > chunk_size:
                    split_items = [item[i:i+chunk_size] for i in range(0, len(item), chunk_size)]
                    for split_item in split_items:
                        chunks.append(StreamChunk(split_item, chunk_type, delay_before=self.delay_between_chunks))
                else:
                    chunks.append(StreamChunk(item, chunk_type, delay_before=self.delay_between_chunks))

        return chunks

    def _detect_chunk_type(self, item: Any) -> StreamChunkType:
        """Auto-detect the appropriate chunk type for an item."""
        if isinstance(item, (dict, list)):
            return StreamChunkType.JSON
        elif isinstance(item, bytes):
            return StreamChunkType.BYTES
        else:
            return StreamChunkType.TEXT

    def __aiter__(self) -> 'AsyncIteratorMock':
        """Return the asynchronous iterator object."""
        return self

    async def __anext__(self) -> Any:
        """
        Get the next item in the asynchronous iteration.

        Returns:
            The next item in the sequence, processed according to its type

        Raises:
            StopAsyncIteration: When there are no more items to iterate over
            Exception: If error injection is configured for the current index
        """
        if self.index >= len(self.chunks):
            raise StopAsyncIteration

        # Check for error injection
        if self.error_at_index == self.index:
            self.index += 1
            raise self.error_type

        chunk = self.chunks[self.index]
        self.index += 1

        # Apply delay if specified
        if chunk.delay_before > 0:
            await asyncio.sleep(chunk.delay_before)

        # Process content based on type
        return self._process_chunk_content(chunk)

    def _process_chunk_content(self, chunk: StreamChunk) -> Any:
        """Process chunk content based on its type."""
        if chunk.chunk_type == StreamChunkType.JSON:
            # For JSON chunks, convert dict/list to JSON string
            if isinstance(chunk.content, (dict, list)):
                import json
                return json.dumps(chunk.content)
            return chunk.content
        elif chunk.chunk_type == StreamChunkType.BYTES:
            # Ensure bytes content is properly handled
            if isinstance(chunk.content, str):
                return chunk.content.encode('utf-8')
            return chunk.content
        else:
            # Text and other types
            return chunk.content

    def reset(self):
        """Reset the iterator to the beginning."""
        self.index = 0

    def remaining_count(self) -> int:
        """Get the number of remaining chunks."""
        return len(self.chunks) - self.index

    def is_exhausted(self) -> bool:
        """Check if the iterator is exhausted."""
        return self.index >= len(self.chunks)

    @classmethod
    def from_text(
        cls,
        text: str,
        chunk_size: int = 50,
        delay_between_chunks: float = 0.0,
        **kwargs
    ) -> 'AsyncIteratorMock':
        """
        Create an AsyncIteratorMock from text, splitting it into chunks.

        Args:
            text: The text to split into chunks
            chunk_size: Size of each chunk
            delay_between_chunks: Delay between chunks
            **kwargs: Additional arguments passed to constructor

        Returns:
            AsyncIteratorMock configured for text streaming
        """
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i+chunk_size]
            delay = delay_between_chunks if i > 0 else 0.0  # No delay for first chunk
            chunks.append(StreamChunk(chunk_text, StreamChunkType.TEXT, delay_before=delay))

        return cls(chunks, **kwargs)

    @classmethod
    def from_chunks(cls, chunks: List[StreamChunk]) -> 'AsyncIteratorMock':
        """
        Create an AsyncIteratorMock from a list of StreamChunk objects.

        Args:
            chunks: List of StreamChunk objects

        Returns:
            AsyncIteratorMock with the specified chunks
        """
        return cls(chunks, auto_convert_types=False)

    def to_list(self) -> List[Any]:
        """
        Convert all chunks to a list synchronously.

        Returns:
            List of all chunk contents
        """
        result = []
        for chunk in self.chunks:
            result.append(self._process_chunk_content(chunk))
        return result

    async def to_list_async(self) -> List[Any]:
        """
        Convert all chunks to a list asynchronously.

        Returns:
            List of all chunk contents
        """
        result = []
        async for chunk in self:
            result.append(chunk)
        return result

    def __len__(self) -> int:
        """Return the total number of chunks."""
        return len(self.chunks)

    def __getitem__(self, index: int) -> Any:
        """Get a chunk by index (synchronously)."""
        if index < 0 or index >= len(self.chunks):
            raise IndexError("Chunk index out of range")
        return self._process_chunk_content(self.chunks[index])


# Convenience functions for common use cases
def create_text_stream(text: str, chunk_size: int = 50, delay: float = 0.0) -> AsyncIteratorMock:
    """Create a text stream mock from a string."""
    return AsyncIteratorMock.from_text(text, chunk_size, delay)


def create_json_stream(data: Union[Dict, List], delay: float = 0.0) -> AsyncIteratorMock:
    """Create a JSON stream mock from structured data."""
    import json
    json_str = json.dumps(data)
    return AsyncIteratorMock.from_text(json_str, chunk_size=100, delay_between_chunks=delay)


def create_mixed_stream(chunks: List[Union[str, Dict, StreamChunk]], delay: float = 0.0) -> AsyncIteratorMock:
    """Create a mixed-type stream with different content types."""
    processed_chunks = []
    for chunk in chunks:
        if isinstance(chunk, StreamChunk):
            processed_chunks.append(chunk)
        elif isinstance(chunk, dict):
            processed_chunks.append(StreamChunk(chunk, StreamChunkType.JSON, delay_before=delay))
        else:
            processed_chunks.append(StreamChunk(chunk, StreamChunkType.TEXT, delay_before=delay))
    return AsyncIteratorMock(processed_chunks)