from unittest.mock import AsyncMock, MagicMock

import pytest
from openai import APIConnectionError, OpenAIError

from resync.core.exceptions import LLMError
from resync.core.utils.llm import call_llm

# Marks all tests in this file as async
pytestmark = pytest.mark.asyncio


async def test_call_llm_success(mocker):
    """
    Tests the happy path where the LLM call succeeds on the first attempt.
    """
    # Mock the response from the OpenAI client
    mock_choice = MagicMock()
    mock_choice.message.content = "  Mocked LLM Response  "
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    # Patch the client's method to return our mock response
    mock_create = AsyncMock(return_value=mock_response)
    mocker.patch("openai.AsyncOpenAI.chat.completions.create", mock_create)

    # Call the function
    result = await call_llm(prompt="test prompt", model="test-model")

    # Assertions
    assert result == "Mocked LLM Response"
    mock_create.assert_called_once()


async def test_call_llm_raises_llmerror_after_retries_on_apierror(mocker):
    """
    Ensures LLMError is raised after all retries fail due to an OpenAIError.
    This tests the primary error handling path for API-specific issues.
    """
    # Patch the client's method to consistently raise an OpenAIError
    mock_create = AsyncMock(side_effect=OpenAIError("API is down"))
    mocker.patch("openai.AsyncOpenAI.chat.completions.create", mock_create)

    # Call the function and assert that it raises our custom LLMError
    with pytest.raises(LLMError) as excinfo:
        await call_llm(prompt="test", model="test-model", max_retries=2, initial_backoff=0.01)

    # Assertions
    assert "LLM call failed after 2 retries" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, OpenAIError)
    # max_retries=2 means 1 initial call + 2 retries = 3 calls
    assert mock_create.call_count == 3


async def test_call_llm_raises_llmerror_after_retries_on_network_error(mocker):
    """
    Ensures LLMError is raised after all retries fail due to a network error.
    This tests the handling of connection-related issues.
    """
    # Patch the client's method to consistently raise a connection error
    mock_create = AsyncMock(side_effect=APIConnectionError(request=MagicMock()))
    mocker.patch("openai.AsyncOpenAI.chat.completions.create", mock_create)

    # Call the function and assert that it raises our custom LLMError
    with pytest.raises(LLMError) as excinfo:
        # Using ConnectionError directly is also an option, but APIConnectionError is more specific
        # to the library's network layer.
        await call_llm(prompt="test", model="test-model", max_retries=1, initial_backoff=0.01)

    # Assertions
    assert "Network-related error" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, APIConnectionError)
    # max_retries=1 means 1 initial call + 1 retry = 2 calls
    assert mock_create.call_count == 2
