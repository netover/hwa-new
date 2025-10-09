# resync/core/utils/llm.py
import asyncio
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

from ..exceptions import LLMError
from ...settings import settings
from ..resilience import circuit_breaker, retry_with_backoff, with_timeout
from .common_error_handlers import retry_on_exception
from ..structured_logger import get_logger

logger = get_logger(__name__)


@circuit_breaker(
    failure_threshold=3,
    recovery_timeout=60,
    name="llm_service"
)
@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    jitter=True
)
@with_timeout(settings.LLM_TIMEOUT)
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
    timeout: float = 30.0,
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
        timeout: Maximum time in seconds to wait for the LLM response.

    Returns:
        The content of the LLM's response.

    Raises:
        LLMError: If the LLM call fails after all retry attempts or times out.
    """
    start_time = time.time()
    
    # Use provided api_key or settings, handle default placeholder
    effective_api_key = api_key or settings.LLM_API_KEY
    if effective_api_key == "your_default_api_key_here":
        effective_api_key = None

    try:
        # Use LiteLLM's acompletion for enhanced functionality with timeout
        response = await asyncio.wait_for(
            acompletion(
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
            ),
            timeout=timeout
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
            "llm_call_completed",
            duration_seconds=round(total_time, 2),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )

        return content

    except asyncio.TimeoutError:
        logger.error("llm_timeout", timeout_seconds=timeout)
        raise LLMError(f"LLM call timed out after {timeout} seconds")
    except ContentPolicyViolationError as e:
        logger.warning("llm_content_policy_violation", error=str(e))
        raise LLMError(f"Content policy violation: {str(e)}")
    except ContextWindowExceededError as e:
        logger.error("llm_context_window_exceeded", error=str(e))
        raise LLMError(f"Context window exceeded: {str(e)}")
    except AuthenticationError as e:
        logger.error("llm_authentication_error", error=str(e))
        raise LLMError(f"Authentication error: {str(e)}")
    except RateLimitError as e:
        logger.warning("llm_rate_limit_exceeded", error=str(e))
        raise LLMError(f"Rate limit exceeded: {str(e)}")
    except InvalidRequestError as e:
        logger.error("llm_invalid_request", error=str(e))
        raise LLMError(f"Invalid request: {str(e)}")
    except APIError as e:
        logger.error("llm_api_error", error=str(e))
        raise LLMError(f"API error: {str(e)}")
    except Exception as e:
        logger.error("llm_unexpected_error", error=str(e))
        raise LLMError(f"Unexpected error: {str(e)}")
