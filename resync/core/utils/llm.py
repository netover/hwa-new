# resync/core/utils/llm.py
import asyncio
import logging  # Use logging instead of print

from openai import (  # Import OpenAIError for specific exception handling
    AsyncOpenAI,
    OpenAIError,
)

from resync.core.exceptions import LLMError, NetworkError
from resync.settings import settings

logger = logging.getLogger(__name__)


class LLMCallError(LLMError):
    """Custom exception for LLM call failures."""


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
        LLMCallError: If the LLM call fails after all retry attempts.
    """
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
            return response.choices[0].message.content.strip()
        except OpenAIError as e:  # Catch specific OpenAI API errors
            logger.warning(
                f"LLM call failed (attempt {attempt + 1}/{max_retries + 1}) for model {model} at {settings.LLM_ENDPOINT}: {e}"
            )
            if attempt < max_retries:
                delay = initial_backoff * (2**attempt)  # Exponential backoff
                logger.info(f"Retrying LLM call in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"LLM call failed after {max_retries} retries for model {model} at {settings.LLM_ENDPOINT}: {e}",
                    exc_info=True,
                )
                raise LLMCallError(
                    f"LLM call failed after {max_retries} retries: {e}"
                ) from e
        except ConnectionError as e:
            logger.error(
                "Connection error during LLM call (attempt %d/%d): %s",
                attempt + 1,
                max_retries + 1,
                e,
                exc_info=True,
            )
            if attempt < max_retries:
                delay = initial_backoff * (2**attempt)
                logger.info("Retrying LLM call in %.2f seconds...", delay)
                await asyncio.sleep(delay)
            else:
                raise NetworkError(
                    f"Connection error during LLM call after {max_retries} retries: {e}"
                ) from e
        except TimeoutError as e:
            logger.error(
                "Timeout during LLM call (attempt %d/%d): %s",
                attempt + 1,
                max_retries + 1,
                e,
                exc_info=True,
            )
            if attempt < max_retries:
                delay = initial_backoff * (2**attempt)
                logger.info("Retrying LLM call in %.2f seconds...", delay)
                await asyncio.sleep(delay)
            else:
                raise NetworkError(
                    f"Timeout during LLM call after {max_retries} retries: {e}"
                ) from e
        except ValueError as e:
            logger.error(
                "Value error during LLM call (attempt %d/%d): %s",
                attempt + 1,
                max_retries + 1,
                e,
                exc_info=True,
            )
            if attempt < max_retries:
                delay = initial_backoff * (2**attempt)
                logger.info("Retrying LLM call in %.2f seconds...", delay)
                await asyncio.sleep(delay)
            else:
                raise LLMCallError(
                    f"Value error during LLM call after {max_retries} retries: {e}"
                ) from e
        except Exception as e:  # Catch any other unexpected errors
            logger.error(
                "Unexpected error during LLM call (attempt %d/%d): %s",
                attempt + 1,
                max_retries + 1,
                e,
                exc_info=True,
            )
            if attempt < max_retries:
                delay = initial_backoff * (2**attempt)
                logger.info("Retrying LLM call in %.2f seconds...", delay)
                await asyncio.sleep(delay)
            else:
                raise LLMCallError(
                    f"Unexpected error during LLM call after {max_retries} retries: {e}"
                ) from e
