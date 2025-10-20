from unittest.mock import AsyncMock, MagicMock

import pytest
from litellm.exceptions import APIError, APIConnectionError

from ..exceptions import LLMError
from .llm import call_llm

# Marks all tests in this file as async
pytestmark = pytest.mark.asyncio


async def test_call_llm_success(mocker):
    """
    Tests the happy path where the LLM call succeeds on the first attempt.
    """
    # Mock the response from LiteLLM
    mock_choice = MagicMock()
    mock_choice.message.content = "  Mocked LLM Response  "
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = {"prompt_tokens": 10, "completion_tokens": 20}

    # Patch the LiteLLM acompletion function to return our mock response
    mock_acompletion = AsyncMock(return_value=mock_response)
    mocker.patch("resync.core.utils.llm.acompletion", mock_acompletion)

    # Call the function
    result = await call_llm(prompt="test prompt", model="test-model")

    # Assertions
    assert result == "Mocked LLM Response"
    mock_acompletion.assert_called_once()


async def test_call_llm_raises_llmerror_after_retries_on_apierror(mocker):
    """
    Ensures LLMError is raised after all retries fail due to an APIError.
    This tests the primary error handling path for API-specific issues.
    """
    # Patch the LiteLLM acompletion function to consistently raise an APIError
    mock_acompletion = AsyncMock(side_effect=APIError("API is down"))
    mocker.patch("resync.core.utils.llm.acompletion", mock_acompletion)

    # Call the function and assert that it raises our custom LLMError
    with pytest.raises(LLMError) as excinfo:
        await call_llm(
            prompt="test", model="test-model", max_retries=2, initial_backoff=0.01
        )

    # Assertions
    assert "API error" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, APIError)
    # max_retries=2 means 1 initial call + 2 retries = 3 calls
    assert mock_acompletion.call_count == 3


async def test_call_llm_raises_llmerror_after_retries_on_network_error(mocker):
    """
    Ensures LLMError is raised after all retries fail due to a network error.
    This tests the handling of connection-related issues.
    """
    # Patch the LiteLLM acompletion function to consistently raise a connection error
    mock_acompletion = AsyncMock(side_effect=APIConnectionError("Network error"))
    mocker.patch("resync.core.utils.llm.acompletion", mock_acompletion)

    # Call the function and assert that it raises our custom LLMError
    with pytest.raises(LLMError) as excinfo:
        await call_llm(
            prompt="test", model="test-model", max_retries=1, initial_backoff=0.01
        )

    # Assertions
    assert "Connection error" in str(excinfo.value)
    assert isinstance(excinfo.value.__cause__, APIConnectionError)
    # max_retries=1 means 1 initial call + 1 retry = 2 calls
    assert mock_acompletion.call_count == 2
