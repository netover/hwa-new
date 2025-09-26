from __future__ import annotations

import logging
from typing import Generator

from resync.core.agent_manager import agent_manager
from resync.services.mock_tws_service import MockTWSClient
from resync.services.tws_service import OptimizedTWSClient
from resync.settings import settings

# --- Logging Setup ---
logger = logging.getLogger(__name__)
from inspect import signature as _mutmut_signature
from typing import Annotated, Callable, ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg=None):
    """Forward call to original or mutated function, depending on the environment"""
    import os

    mutant_under_test = os.environ["MUTANT_UNDER_TEST"]
    if mutant_under_test == "fail":
        from mutmut.__main__ import MutmutProgrammaticFailException

        raise MutmutProgrammaticFailException("Failed programmatically")
    elif mutant_under_test == "stats":
        from mutmut.__main__ import record_trampoline_hit

        record_trampoline_hit(orig.__module__ + "." + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + "." + orig.__name__ + "__mutmut_"
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition(".")[-1]
    if self_arg:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


def x_get_tws_client__mutmut_orig() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_1() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug(None)

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_2() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("XXDependency 'get_tws_client' called.XX")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_3() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_4() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("DEPENDENCY 'GET_TWS_CLIENT' CALLED.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_5() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info(None)
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_6() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("XXTWS_MOCK_MODE is enabled. Returning MockTWSClient.XX")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_7() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("tws_mock_mode is enabled. returning mocktwsclient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_8() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE IS ENABLED. RETURNING MOCKTWSCLIENT.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_9() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                and agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_10() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_11() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(None, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_12() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, None)
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_13() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr("_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_14() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(
                    agent_manager,
                )
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_15() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "XX_mock_tws_clientXX")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_16() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_MOCK_TWS_CLIENT")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_17() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is not None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_18() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = None
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_19() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = None
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_20() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = None

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=True)
        raise


def x_get_tws_client__mutmut_21() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(None, exc_info=True)
        raise


def x_get_tws_client__mutmut_22() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=None)
        raise


def x_get_tws_client__mutmut_23() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(exc_info=True)
        raise


def x_get_tws_client__mutmut_24() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(
            f"Failed to retrieve TWS client: {e}",
        )
        raise


def x_get_tws_client__mutmut_25() -> (
    Generator[OptimizedTWSClient | MockTWSClient, None, None]
):
    """
    Dependency injector for the TWS client.

    This function provides a reliable way to get the singleton TWS client
    instance, either the real OptimizedTWSClient or a MockTWSClient based on settings.

    Yields:
        The singleton instance of the TWS client.
    """
    try:
        logger.debug("Dependency 'get_tws_client' called.")

        if settings.TWS_MOCK_MODE:
            logger.info("TWS_MOCK_MODE is enabled. Returning MockTWSClient.")
            # We need to ensure a singleton for the mock client as well
            if (
                not hasattr(agent_manager, "_mock_tws_client")
                or agent_manager._mock_tws_client is None
            ):
                agent_manager._mock_tws_client = MockTWSClient()
            client = agent_manager._mock_tws_client
        else:
            # The agent_manager is responsible for lazily initializing the real client
            client = agent_manager._get_tws_client()

        yield client
    except Exception as e:
        # This is a critical failure, as the application cannot function
        # without a TWS client.
        logger.error(f"Failed to retrieve TWS client: {e}", exc_info=False)
        raise


x_get_tws_client__mutmut_mutants: ClassVar[MutantDict] = {
    "x_get_tws_client__mutmut_1": x_get_tws_client__mutmut_1,
    "x_get_tws_client__mutmut_2": x_get_tws_client__mutmut_2,
    "x_get_tws_client__mutmut_3": x_get_tws_client__mutmut_3,
    "x_get_tws_client__mutmut_4": x_get_tws_client__mutmut_4,
    "x_get_tws_client__mutmut_5": x_get_tws_client__mutmut_5,
    "x_get_tws_client__mutmut_6": x_get_tws_client__mutmut_6,
    "x_get_tws_client__mutmut_7": x_get_tws_client__mutmut_7,
    "x_get_tws_client__mutmut_8": x_get_tws_client__mutmut_8,
    "x_get_tws_client__mutmut_9": x_get_tws_client__mutmut_9,
    "x_get_tws_client__mutmut_10": x_get_tws_client__mutmut_10,
    "x_get_tws_client__mutmut_11": x_get_tws_client__mutmut_11,
    "x_get_tws_client__mutmut_12": x_get_tws_client__mutmut_12,
    "x_get_tws_client__mutmut_13": x_get_tws_client__mutmut_13,
    "x_get_tws_client__mutmut_14": x_get_tws_client__mutmut_14,
    "x_get_tws_client__mutmut_15": x_get_tws_client__mutmut_15,
    "x_get_tws_client__mutmut_16": x_get_tws_client__mutmut_16,
    "x_get_tws_client__mutmut_17": x_get_tws_client__mutmut_17,
    "x_get_tws_client__mutmut_18": x_get_tws_client__mutmut_18,
    "x_get_tws_client__mutmut_19": x_get_tws_client__mutmut_19,
    "x_get_tws_client__mutmut_20": x_get_tws_client__mutmut_20,
    "x_get_tws_client__mutmut_21": x_get_tws_client__mutmut_21,
    "x_get_tws_client__mutmut_22": x_get_tws_client__mutmut_22,
    "x_get_tws_client__mutmut_23": x_get_tws_client__mutmut_23,
    "x_get_tws_client__mutmut_24": x_get_tws_client__mutmut_24,
    "x_get_tws_client__mutmut_25": x_get_tws_client__mutmut_25,
}


def get_tws_client(*args, **kwargs):
    result = _mutmut_trampoline(
        x_get_tws_client__mutmut_orig, x_get_tws_client__mutmut_mutants, args, kwargs
    )
    return result


get_tws_client.__signature__ = _mutmut_signature(x_get_tws_client__mutmut_orig)
x_get_tws_client__mutmut_orig.__name__ = "x_get_tws_client"
