# resync/core/utils/llm.py
import asyncio
import logging  # Use logging instead of print
import time

from openai import (  # Import OpenAIError for specific exception handling
    AsyncOpenAI,
    OpenAIError,
)

from resync.core.exceptions import LLMError
from resync.settings import settings
from resync.core.utils.common_error_handlers import retry_on_exception

logger = logging.getLogger(__name__)


@retry_on_exception(
    max_retries=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(OpenAIError, ConnectionError, TimeoutError, ValueError, Exception),
    logger=logger
)
async def call_llm(
    prompt: str,
    model: str,
    max_tokens: int = 200,
    temperature: float = 0.1,
    max_retries: int = 3,
    initial_backoff: float = 1.0,
) -> str:
    """
    Calls a generic OpenAI-compatible LLM endpoint with retry logic.

    Args:
        prompt: The prompt to send to the LLM.
        model: The LLM model to use.
        max_tokens: Maximum number of tokens in the LLM's response.
        temperature: Controls the randomness of the LLM's response.
        max_retries: Maximum number of retry attempts for the LLM call.
        initial_backoff: Initial delay in seconds before the first retry.

    Returns:
        The content of the LLM's response.

    Raises:
        LLMError: If the LLM call fails after all retry attempts.
    """
    start_time = time.time()
    api_key = (
        settings.LLM_API_KEY
        if settings.LLM_API_KEY != "your_default_api_key_here"
        else None
    )

    client = AsyncOpenAI(
        base_url=settings.LLM_ENDPOINT,
        api_key=api_key,
    )

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
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

    # Record successful call metrics
    total_time = time.time() - start_time
    logger.info(
        f"LLM call completed successfully in {total_time:.2f}s "
        f"(model: {model}, prompt_tokens: ~{len(prompt)//4})"
    )

    return content
