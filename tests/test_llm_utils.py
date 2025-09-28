"""Tests for resync.core.utils.llm module."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from openai import OpenAIError

from resync.core.exceptions import LLMError, NetworkError
from resync.core.utils.llm import (
    LLMCallError,
    call_llm,
)


class TestLLMCallError:
    """Test suite for LLMCallError exception."""

    def test_llm_call_error_inheritance(self):
        """Test that LLMCallError inherits from LLMError."""
        error = LLMCallError("Test error")
        assert isinstance(error, LLMError)
        assert isinstance(error, Exception)

    def test_llm_call_error_message(self):
        """Test LLMCallError message handling."""
        message = "Custom error message"
        error = LLMCallError(message)
        assert str(error) == message

    def test_llm_call_error_empty_message(self):
        """Test LLMCallError with empty message."""
        error = LLMCallError("")
        assert str(error) == ""


class TestCallLLM:
    """Test suite for call_llm function."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch('resync.core.utils.llm.settings') as mock_settings:
            mock_settings.LLM_API_KEY = "test_api_key"
            mock_settings.LLM_ENDPOINT = "https://api.example.com"
            yield mock_settings

    @pytest.fixture
    def mock_client(self):
        """Mock OpenAI client."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    async def test_call_llm_success_first_attempt(self, mock_settings, mock_client):
        """Test successful LLM call on first attempt."""
        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo")

            assert result == "Test response"
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs["model"] == "gpt-3.5-turbo"
            assert call_args.kwargs["messages"] == [{"role": "user", "content": "Test prompt"}]
            assert call_args.kwargs["max_tokens"] == 200
            assert call_args.kwargs["temperature"] == 0.1

    async def test_call_llm_success_after_retries(self, mock_settings):
        """Test successful LLM call after retries."""
        # Create a mock that fails twice then succeeds
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Success after retries"

        # Fail on first two calls, succeed on third
        mock_client.chat.completions.create.side_effect = [
            OpenAIError("API Error 1"),
            OpenAIError("API Error 2"),
            mock_response
        ]

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo", max_retries=2)

            assert result == "Success after retries"
            assert mock_client.chat.completions.create.call_count == 3

    async def test_call_llm_max_retries_exceeded(self, mock_settings):
        """Test LLM call fails after max retries."""
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = OpenAIError("Persistent API Error")

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            with pytest.raises(LLMCallError, match="LLM call failed after 3 retries"):
                await call_llm("Test prompt", "gpt-3.5-turbo", max_retries=3)

            assert mock_client.chat.completions.create.call_count == 4  # initial + 3 retries

    async def test_call_llm_custom_parameters(self, mock_settings, mock_client):
        """Test LLM call with custom parameters."""
        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            await call_llm(
                "Custom prompt",
                "gpt-4",
                max_tokens=500,
                temperature=0.7,
                max_retries=5,
                initial_backoff=2.0
            )

            call_args = mock_client.chat.completions.create.call_args
            assert call_args.kwargs["model"] == "gpt-4"
            assert call_args.kwargs["messages"] == [{"role": "user", "content": "Custom prompt"}]
            assert call_args.kwargs["max_tokens"] == 500
            assert call_args.kwargs["temperature"] == 0.7

    async def test_call_llm_connection_error_retries(self, mock_settings):
        """Test LLM call retries on connection errors."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Success after connection retry"

        # Fail with connection error once, then succeed
        mock_client.chat.completions.create.side_effect = [
            ConnectionError("Network unreachable"),
            mock_response
        ]

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo", max_retries=2)

            assert result == "Success after connection retry"
            assert mock_client.chat.completions.create.call_count == 2

    async def test_call_llm_connection_error_max_retries(self, mock_settings):
        """Test LLM call fails after max retries on connection errors."""
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = ConnectionError("Persistent network error")

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            with pytest.raises(NetworkError, match="Connection error during LLM call after 2 retries"):
                await call_llm("Test prompt", "gpt-3.5-turbo", max_retries=2)

    async def test_call_llm_timeout_error_retries(self, mock_settings):
        """Test LLM call retries on timeout errors."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Success after timeout retry"

        # Fail with timeout error once, then succeed
        mock_client.chat.completions.create.side_effect = [
            TimeoutError("Request timeout"),
            mock_response
        ]

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo", max_retries=2)

            assert result == "Success after timeout retry"
            assert mock_client.chat.completions.create.call_count == 2

    async def test_call_llm_value_error_retries(self, mock_settings):
        """Test LLM call retries on value errors."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Success after value error retry"

        # Fail with value error once, then succeed
        mock_client.chat.completions.create.side_effect = [
            ValueError("Invalid parameter"),
            mock_response
        ]

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo", max_retries=2)

            assert result == "Success after value error retry"
            assert mock_client.chat.completions.create.call_count == 2

    async def test_call_llm_unexpected_error_retries(self, mock_settings):
        """Test LLM call retries on unexpected errors."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Success after unexpected error retry"

        # Fail with unexpected error once, then succeed
        mock_client.chat.completions.create.side_effect = [
            RuntimeError("Unexpected runtime error"),
            mock_response
        ]

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo", max_retries=2)

            assert result == "Success after unexpected error retry"
            assert mock_client.chat.completions.create.call_count == 2

    async def test_call_llm_no_api_key(self, mock_settings):
        """Test LLM call with no API key."""
        mock_settings.LLM_API_KEY = None

        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Response without API key"

        mock_client.chat.completions.create.return_value = mock_response

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo")

            assert result == "Response without API key"
            # Verify that api_key=None was passed to the client
            call_args = mock_client.chat.completions.create.call_args
            # The client should be initialized with api_key=None

    async def test_call_llm_default_api_key(self, mock_settings):
        """Test LLM call with default API key."""
        mock_settings.LLM_API_KEY = "your_default_api_key_here"

        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Response with default key"

        mock_client.chat.completions.create.return_value = mock_response

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo")

            assert result == "Response with default key"
            # The default key should be treated as None

    async def test_call_llm_response_stripping(self, mock_settings, mock_client):
        """Test that LLM response is properly stripped."""
        # Mock response with extra whitespace
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "  Test response with whitespace  \n  "
        mock_client.chat.completions.create.return_value = mock_response

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo")

            assert result == "Test response with whitespace"

    async def test_call_llm_empty_response(self, mock_settings, mock_client):
        """Test LLM call with empty response."""
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = ""
        mock_client.chat.completions.create.return_value = mock_response

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            result = await call_llm("Test prompt", "gpt-3.5-turbo")

            assert result == ""

    async def test_call_llm_logging_on_failure(self, mock_settings, caplog):
        """Test that failures are properly logged."""
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = OpenAIError("API Error")

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            with pytest.raises(LLMCallError):
                await call_llm("Test prompt", "gpt-3.5-turbo", max_retries=1)

            # Check that warning and error logs were created
            assert any("LLM call failed" in record.message for record in caplog.records)
            assert any("LLM call failed after" in record.message for record in caplog.records)

    async def test_call_llm_exponential_backoff(self, mock_settings):
        """Test exponential backoff timing."""
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = OpenAIError("API Error")

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            with patch('asyncio.sleep') as mock_sleep:
                with pytest.raises(LLMCallError):
                    await call_llm("Test prompt", "gpt-3.5-turbo", max_retries=2, initial_backoff=1.0)

                # Should have called sleep twice with exponential backoff
                assert mock_sleep.call_count == 2
                # First retry: 1.0 * 2^0 = 1.0
                # Second retry: 1.0 * 2^1 = 2.0
                mock_sleep.assert_any_call(1.0)
                mock_sleep.assert_any_call(2.0)

    async def test_call_llm_different_models(self, mock_settings, mock_client):
        """Test LLM calls with different models."""
        test_cases = [
            ("gpt-3.5-turbo", "gpt-3.5-turbo"),
            ("gpt-4", "gpt-4"),
            ("claude-3-opus", "claude-3-opus"),
            ("custom-model", "custom-model"),
        ]

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            for model_name, expected_model in test_cases:
                mock_client.reset_mock()

                await call_llm("Test prompt", model_name)

                call_args = mock_client.chat.completions.create.call_args
                assert call_args.kwargs["model"] == expected_model

    async def test_call_llm_concurrent_calls(self, mock_settings):
        """Test concurrent LLM calls."""
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Concurrent response"
        mock_client.chat.completions.create.return_value = mock_response

        with patch('resync.core.utils.llm.AsyncOpenAI', return_value=mock_client):
            # Make multiple concurrent calls
            tasks = [
                call_llm(f"Prompt {i}", "gpt-3.5-turbo")
                for i in range(3)
            ]

            results = await asyncio.gather(*tasks)

            assert len(results) == 3
            assert all(result == "Concurrent response" for result in results)
            assert mock_client.chat.completions.create.call_count == 3



