from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# --- Environment Setup ---
# Load environment variables from .env file if it exists
env_path = Path(".") / ".env"
if env_path.is_file():
    load_dotenv(dotenv_path=env_path)

# --- Type Definitions ---
ModelEndpoint = str

# --- Base Settings Class (moved to config/base.py) ---
# This file will now load the correct settings class based on APP_ENV

APP_ENV = os.environ.get("APP_ENV", "development").lower()

if APP_ENV == "development":
    from config.development import DevelopmentSettings as CurrentSettings
elif APP_ENV == "production":
    from config.production import ProductionSettings as CurrentSettings
else:
    raise ValueError(
        f"Unknown APP_ENV: {APP_ENV}. Must be 'development' or 'production'."
    )

# --- Global Settings Instance ---
settings: CurrentSettings = CurrentSettings()
from typing import Annotated, Callable

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
