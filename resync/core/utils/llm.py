# resync/core/utils/llm.py
import asyncio
import logging  # Use logging instead of print
import time

from litellm import acompletion
from litellm.exceptions import (
    AuthenticationError,
    ContentPolicyViolationError,
    ContextWindowExceededError,
    InvalidRequestError,
    RateLimitError,
    APIError
)

from resync.core.exceptions import LLMError
from resync.settings import settings
from resync.core.utils.common_error_handlers import retry_on_exception

logger = logging.getLogger(__name__)


@retry_on_exception(
    max_retries=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(AuthenticationError, RateLimitError, APIError, ConnectionError, TimeoutError, ValueError, Exception),
    logger=logger
)
async def call_llm(
    prompt: str,
    model: str,
    max_tokens: int = 200,
    temperature: float = 0.1,
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    api_base: str = None,
    api_key: str = None,
) -> str:
    """
    Calls an LLM through LiteLLM with support for multiple providers (OpenAI, Ollama, etc.).
    Provides enhanced error handling, cost tracking, and model flexibility.

    Args:
        prompt: The prompt to send to the LLM.
        model: The LLM model to use (e.g., "gpt-4o", "ollama/mistral", etc.).
        max_tokens: Maximum number of tokens in the LLM's response.
        temperature: Controls the randomness of the LLM's response.
        max_retries: Maximum number of retry attempts for the LLM call.
        initial_backoff: Initial delay in seconds before the first retry.
        api_base: Optional API base URL (for local models like Ollama).
        api_key: Optional API key (defaults to settings if not provided).

    Returns:
        The content of the LLM's response.

    Raises:
        LLMError: If the LLM call fails after all retry attempts.
    """
    start_time = time.time()
    
    # Use provided api_key or settings, handle default placeholder
    effective_api_key = api_key or settings.LLM_API_KEY
    if effective_api_key == "your_default_api_key_here":
        effective_api_key = None

    try:
        # Use LiteLLM's acompletion for enhanced functionality
        response = await acompletion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            api_base=api_base or getattr(settings, "LLM_ENDPOINT", None),
            api_key=effective_api_key,
            # Additional LiteLLM features
            metadata={
                "user_id": getattr(settings, "APP_NAME", "resync"),
                "session_id": f"tws_{int(time.time())}"
            }
        )

        # Validate response
        if not response.choices or len(response.choices) == 0:
            raise LLMError("Empty response received from LLM")

        content = response.choices[0].message.content
        if content is None:
            raise LLMError("LLM returned null content")

        content = content.strip()
        if not content:
            raise LLMError("LLM returned empty content")

        # Extract usage information for cost tracking
        usage = response.usage or {}
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        
        # Record successful call metrics
        total_time = time.time() - start_time
        logger.info(
            f"LLM call completed successfully in {total_time:.2f}s "
            f"(model: {model}, input_tokens: {input_tokens}, output_tokens: {output_tokens})"
        )

        return content

    except ContentPolicyViolationError as e:
        logger.warning(f"Content policy violation: {e}")
        raise LLMError(f"Content policy violation: {str(e)}")
    except ContextWindowExceededError as e:
        logger.error(f"Context window exceeded: {e}")
        raise LLMError(f"Context window exceeded: {str(e)}")
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise LLMError(f"Authentication error: {str(e)}")
    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        raise LLMError(f"Rate limit exceeded: {str(e)}")
    except InvalidRequestError as e:
        logger.error(f"Invalid request: {e}")
        raise LLMError(f"Invalid request: {str(e)}")
    except APIError as e:
        logger.error(f"API error: {e}")
        raise LLMError(f"API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in LLM call: {e}")
        raise LLMError(f"Unexpected error: {str(e)}")
