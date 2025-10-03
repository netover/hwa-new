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

logger = logging.getLogger(__name__)


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

    for attempt in range(max_retries + 1):
        try:
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
                f"(model: {model}, prompt_tokens: ~{len(prompt)//4}, attempt: {attempt + 1})"
            )
            
            return content
        except OpenAIError as e:  # Catch specific OpenAI API errors
            total_time = time.time() - start_time
            logger.warning(
                f"LLM call failed (attempt {attempt + 1}/{max_retries + 1}) for model {model} at {settings.LLM_ENDPOINT}: {e} "
                f"(elapsed: {total_time:.2f}s)"
            )
            if attempt < max_retries:
                delay = initial_backoff * (2**attempt)  # Exponential backoff
                logger.info(f"Retrying LLM call in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            else:
                total_time = time.time() - start_time
                logger.error(
                    f"LLM call failed after {max_retries} retries for model {model} at {settings.LLM_ENDPOINT}: {e} "
                    f"(total elapsed: {total_time:.2f}s)",
                    exc_info=True,
                )
                raise LLMError(
                    f"LLM call failed after {max_retries} retries: {e}"
                ) from e
        except (ConnectionError, TimeoutError) as e:
            total_time = time.time() - start_time
            logger.error(
                "Connection error during LLM call (attempt %d/%d): %s (elapsed: %.2fs)",
                attempt + 1,
                max_retries + 1,
                e,
                total_time,
                exc_info=True,
            )
            if attempt < max_retries:
                delay = initial_backoff * (2**attempt)
                logger.info("Retrying LLM call in %.2f seconds...", delay)
                await asyncio.sleep(delay)
            else:
                total_time = time.time() - start_time
                logger.error(
                    f"Connection error failed after {max_retries} retries: {e} "
                    f"(total elapsed: {total_time:.2f}s)",
                    exc_info=True,
                )
                raise LLMError(
                    f"Network-related error during LLM call after {max_retries} retries: {e}"
                ) from e
        except ValueError as e:
            total_time = time.time() - start_time
            logger.error(
                "Value error during LLM call (attempt %d/%d): %s (elapsed: %.2fs)",
                attempt + 1,
                max_retries + 1,
                e,
                total_time,
                exc_info=True,
            )
            if attempt < max_retries:
                delay = initial_backoff * (2**attempt)
                logger.info("Retrying LLM call in %.2f seconds...", delay)
                await asyncio.sleep(delay)
            else:
                total_time = time.time() - start_time
                logger.error(
                    f"Value error failed after {max_retries} retries: {e} "
                    f"(total elapsed: {total_time:.2f}s)",
                    exc_info=True,
                )
                raise LLMError(
                    f"Value error during LLM call after {max_retries} retries: {e}"
                ) from e
        except Exception as e:  # Catch any other unexpected errors
            total_time = time.time() - start_time
            logger.error(
                "Unexpected error during LLM call (attempt %d/%d): %s (elapsed: %.2fs)",
                attempt + 1,
                max_retries + 1,
                e,
                total_time,
                exc_info=True,
            )
            if attempt < max_retries:
                delay = initial_backoff * (2**attempt)
                logger.info("Retrying LLM call in %.2f seconds...", delay)
                await asyncio.sleep(delay)
            else:
                total_time = time.time() - start_time
                logger.error(
                    f"Unexpected error failed after {max_retries} retries: {e} "
                    f"(total elapsed: {total_time:.2f}s)",
                    exc_info=True,
                )
                raise LLMError(
                    f"Unexpected error during LLM call after {max_retries} retries: {e}"
                ) from e
