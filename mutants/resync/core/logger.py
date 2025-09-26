import logging
import re

logger = logging.getLogger("resync.core")
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


def x_log_info__mutmut_orig(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_1(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = None
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_2(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(None, "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_3(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", None, msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_4(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", None, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_5(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=None)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_6(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub("password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_7(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_8(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_9(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(
        r"password=[^&\s]+",
        "password=***",
        msg,
    )
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_10(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"XXpassword=[^&\s]+XX", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_11(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_12(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"PASSWORD=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_13(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "XXpassword=***XX", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_14(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "PASSWORD=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(masked)


def x_log_info__mutmut_15(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = None
    logger.info(masked)


def x_log_info__mutmut_16(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace(None, "***")
    logger.info(masked)


def x_log_info__mutmut_17(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", None)
    logger.info(masked)


def x_log_info__mutmut_18(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("***")
    logger.info(masked)


def x_log_info__mutmut_19(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace(
        "api_key",
    )
    logger.info(masked)


def x_log_info__mutmut_20(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("XXapi_keyXX", "***")
    logger.info(masked)


def x_log_info__mutmut_21(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("API_KEY", "***")
    logger.info(masked)


def x_log_info__mutmut_22(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "XX***XX")
    logger.info(masked)


def x_log_info__mutmut_23(msg: str) -> None:
    """Log info message with sensitive data masking."""
    # Mask password values like password=secret
    masked = re.sub(r"password=[^&\s]+", "password=***", msg, flags=re.IGNORECASE)
    masked = masked.replace("api_key", "***")
    logger.info(None)


x_log_info__mutmut_mutants: ClassVar[MutantDict] = {
    "x_log_info__mutmut_1": x_log_info__mutmut_1,
    "x_log_info__mutmut_2": x_log_info__mutmut_2,
    "x_log_info__mutmut_3": x_log_info__mutmut_3,
    "x_log_info__mutmut_4": x_log_info__mutmut_4,
    "x_log_info__mutmut_5": x_log_info__mutmut_5,
    "x_log_info__mutmut_6": x_log_info__mutmut_6,
    "x_log_info__mutmut_7": x_log_info__mutmut_7,
    "x_log_info__mutmut_8": x_log_info__mutmut_8,
    "x_log_info__mutmut_9": x_log_info__mutmut_9,
    "x_log_info__mutmut_10": x_log_info__mutmut_10,
    "x_log_info__mutmut_11": x_log_info__mutmut_11,
    "x_log_info__mutmut_12": x_log_info__mutmut_12,
    "x_log_info__mutmut_13": x_log_info__mutmut_13,
    "x_log_info__mutmut_14": x_log_info__mutmut_14,
    "x_log_info__mutmut_15": x_log_info__mutmut_15,
    "x_log_info__mutmut_16": x_log_info__mutmut_16,
    "x_log_info__mutmut_17": x_log_info__mutmut_17,
    "x_log_info__mutmut_18": x_log_info__mutmut_18,
    "x_log_info__mutmut_19": x_log_info__mutmut_19,
    "x_log_info__mutmut_20": x_log_info__mutmut_20,
    "x_log_info__mutmut_21": x_log_info__mutmut_21,
    "x_log_info__mutmut_22": x_log_info__mutmut_22,
    "x_log_info__mutmut_23": x_log_info__mutmut_23,
}


def log_info(*args, **kwargs):
    result = _mutmut_trampoline(
        x_log_info__mutmut_orig, x_log_info__mutmut_mutants, args, kwargs
    )
    return result


log_info.__signature__ = _mutmut_signature(x_log_info__mutmut_orig)
x_log_info__mutmut_orig.__name__ = "x_log_info"
