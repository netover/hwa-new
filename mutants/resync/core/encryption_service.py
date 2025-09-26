"""
Encryption service for Resync core.
"""

import logging
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


class EncryptionService:
    """Simple encryption service for sensitive data handling."""

    @staticmethod
    def encrypt(data: str) -> str:
        """Encrypt sensitive data."""
        return f"encrypted_{data}"

    @staticmethod
    def decrypt(encrypted_data: str) -> str:
        """Decrypt data."""
        return encrypted_data.replace("encrypted_", "")


# Logger masking
logger = logging.getLogger(__name__)


def x_mask_sensitive_data_in_logs__mutmut_orig(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_1(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") or "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_2(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(None, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_3(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, None) and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_4(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr("msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_5(record) -> None:
    """Mask sensitive data in log records."""
    if (
        hasattr(
            record,
        )
        and "password" in str(record.msg).lower()
    ):
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_6(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "XXmsgXX") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_7(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "MSG") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_8(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "XXpasswordXX" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_9(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "PASSWORD" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_10(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" not in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_11(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).upper():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_12(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(None).lower():
        record.msg = str(record.msg).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_13(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = None
    return True


def x_mask_sensitive_data_in_logs__mutmut_14(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace(None, "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_15(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", None)
    return True


def x_mask_sensitive_data_in_logs__mutmut_16(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_17(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace(
            "password",
        )
    return True


def x_mask_sensitive_data_in_logs__mutmut_18(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(None).replace("password", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_19(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("XXpasswordXX", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_20(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("PASSWORD", "***")
    return True


def x_mask_sensitive_data_in_logs__mutmut_21(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "XX***XX")
    return True


def x_mask_sensitive_data_in_logs__mutmut_22(record) -> None:
    """Mask sensitive data in log records."""
    if hasattr(record, "msg") and "password" in str(record.msg).lower():
        record.msg = str(record.msg).replace("password", "***")
    return False


x_mask_sensitive_data_in_logs__mutmut_mutants: ClassVar[MutantDict] = {
    "x_mask_sensitive_data_in_logs__mutmut_1": x_mask_sensitive_data_in_logs__mutmut_1,
    "x_mask_sensitive_data_in_logs__mutmut_2": x_mask_sensitive_data_in_logs__mutmut_2,
    "x_mask_sensitive_data_in_logs__mutmut_3": x_mask_sensitive_data_in_logs__mutmut_3,
    "x_mask_sensitive_data_in_logs__mutmut_4": x_mask_sensitive_data_in_logs__mutmut_4,
    "x_mask_sensitive_data_in_logs__mutmut_5": x_mask_sensitive_data_in_logs__mutmut_5,
    "x_mask_sensitive_data_in_logs__mutmut_6": x_mask_sensitive_data_in_logs__mutmut_6,
    "x_mask_sensitive_data_in_logs__mutmut_7": x_mask_sensitive_data_in_logs__mutmut_7,
    "x_mask_sensitive_data_in_logs__mutmut_8": x_mask_sensitive_data_in_logs__mutmut_8,
    "x_mask_sensitive_data_in_logs__mutmut_9": x_mask_sensitive_data_in_logs__mutmut_9,
    "x_mask_sensitive_data_in_logs__mutmut_10": x_mask_sensitive_data_in_logs__mutmut_10,
    "x_mask_sensitive_data_in_logs__mutmut_11": x_mask_sensitive_data_in_logs__mutmut_11,
    "x_mask_sensitive_data_in_logs__mutmut_12": x_mask_sensitive_data_in_logs__mutmut_12,
    "x_mask_sensitive_data_in_logs__mutmut_13": x_mask_sensitive_data_in_logs__mutmut_13,
    "x_mask_sensitive_data_in_logs__mutmut_14": x_mask_sensitive_data_in_logs__mutmut_14,
    "x_mask_sensitive_data_in_logs__mutmut_15": x_mask_sensitive_data_in_logs__mutmut_15,
    "x_mask_sensitive_data_in_logs__mutmut_16": x_mask_sensitive_data_in_logs__mutmut_16,
    "x_mask_sensitive_data_in_logs__mutmut_17": x_mask_sensitive_data_in_logs__mutmut_17,
    "x_mask_sensitive_data_in_logs__mutmut_18": x_mask_sensitive_data_in_logs__mutmut_18,
    "x_mask_sensitive_data_in_logs__mutmut_19": x_mask_sensitive_data_in_logs__mutmut_19,
    "x_mask_sensitive_data_in_logs__mutmut_20": x_mask_sensitive_data_in_logs__mutmut_20,
    "x_mask_sensitive_data_in_logs__mutmut_21": x_mask_sensitive_data_in_logs__mutmut_21,
    "x_mask_sensitive_data_in_logs__mutmut_22": x_mask_sensitive_data_in_logs__mutmut_22,
}


def mask_sensitive_data_in_logs(*args, **kwargs):
    result = _mutmut_trampoline(
        x_mask_sensitive_data_in_logs__mutmut_orig,
        x_mask_sensitive_data_in_logs__mutmut_mutants,
        args,
        kwargs,
    )
    return result


mask_sensitive_data_in_logs.__signature__ = _mutmut_signature(
    x_mask_sensitive_data_in_logs__mutmut_orig
)
x_mask_sensitive_data_in_logs__mutmut_orig.__name__ = "x_mask_sensitive_data_in_logs"


logging.getLogger().addFilter(mask_sensitive_data_in_logs)
