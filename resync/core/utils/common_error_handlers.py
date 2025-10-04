"""
Common error handling utilities to eliminate code duplication.

This module contains standard error handling patterns that can be reused
across multiple modules in the application.
"""
import logging
from typing import Any, Callable, Type, Union, TypeVar, cast
import asyncio
from functools import wraps

from resync.core.exceptions import ResyncException

logger = logging.getLogger(__name__)

# Create a type variable for preserving function signatures
F = TypeVar('F', bound=Callable[..., Any])


def handle_parsing_errors(error_message: str = "Error occurred during parsing") -> Callable[[F], F]:
    """
    Decorator to handle parsing errors consistently.
    
    Args:
        error_message: Base error message to use when raising ParsingError
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.debug(f"{error_message}: {e}")
                from resync.core.exceptions import ParsingError
                raise ParsingError(f"{error_message}: {e}") from e
        return cast(F, wrapper)
    return decorator


def handle_llm_errors(error_message: str = "Error occurred during LLM call") -> Callable[[F], F]:
    """
    Decorator to handle LLM-related errors consistently.
    
    Args:
        error_message: Base error message to use when raising LLMError
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{error_message}: {e}", exc_info=True)
                from resync.core.exceptions import LLMError
                raise LLMError(f"{error_message}: {e}") from e
        return cast(F, wrapper)
    return decorator


def handle_api_errors(
    exception_class: Type[ResyncException], 
    error_message: str = "Error occurred in API call"
) -> Callable[[F], F]:
    """
    Decorator to handle API-related errors consistently.
    
    Args:
        exception_class: The ResyncException subclass to raise
        error_message: Base error message to use
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{error_message}: {e}", exc_info=True)
                raise exception_class(f"{error_message}: {e}") from e
        return cast(F, wrapper)
    return decorator


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: logging.Logger = None
) -> Callable[[F], F]:
    """
    Decorator to retry a function if specific exceptions are raised.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch
        logger: Logger to use for retry messages
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger_instance = logging.getLogger(func.__module__)
            else:
                logger_instance = logger
            
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt < max_retries:
                        logger_instance.info(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay:.2f} seconds..."
                        )
                        if asyncio.iscoroutinefunction(func):
                            # For async functions, properly await the sleep
                            import asyncio
                            # Create a new event loop if none exists
                            try:
                                loop = asyncio.get_running_loop()
                                if loop.is_running():
                                    # If loop is running, schedule the sleep
                                    import concurrent.futures
                                    with concurrent.futures.ThreadPoolExecutor() as executor:
                                        executor.submit(time.sleep, current_delay)
                                else:
                                    loop.run_until_complete(asyncio.sleep(current_delay))
                            except RuntimeError:
                                # No running loop, create a new one
                                asyncio.run(asyncio.sleep(current_delay))
                        else:
                            import time
                            time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger_instance.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {e}",
                            exc_info=True
                        )
                        raise e
            return None  # This should never be reached
        return cast(F, wrapper)
    return decorator


def log_and_handle_exception(
    exception_class: Type[ResyncException],
    message: str,
    log_level: int = logging.ERROR
) -> Callable[[F], F]:
    """
    Context manager or decorator to handle exceptions consistently.
    
    Args:
        exception_class: The ResyncException subclass to raise
        message: Error message to use
        log_level: Logging level to use for logging the exception
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.log(log_level, f"{message}: {e}", exc_info=True)
                raise exception_class(f"{message}: {e}") from e
        return cast(F, wrapper)
    return decorator