# resync/core/rag_watcher.py
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from watchfiles import awatch

from resync.core.file_ingestor import ingest_file
from resync.settings import settings

logger = logging.getLogger(__name__)

RAG_DIRECTORY = settings.BASE_DIR / "rag"
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


async def x_watch_rag_directory__mutmut_orig():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_1():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=None)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_2():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=False)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_3():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(None)
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_4():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(None):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_5():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name != "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_6():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "XXaddedXX":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_7():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "ADDED":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_8():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = None
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_9():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(None)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_10():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(None)
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_11():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(None)

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_12():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(None))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=True)


async def x_watch_rag_directory__mutmut_13():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception:
        logger.error(None, exc_info=True)


async def x_watch_rag_directory__mutmut_14():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=None)


async def x_watch_rag_directory__mutmut_15():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception:
        logger.error(exc_info=True)


async def x_watch_rag_directory__mutmut_16():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(
            f"Error in RAG directory watcher: {e}",
        )


async def x_watch_rag_directory__mutmut_17():
    """Watches the rag/ directory for new files and triggers ingestion."""
    # Ensure the directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    logger.info(f"Starting RAG watcher on directory: {RAG_DIRECTORY}")
    try:
        async for changes in awatch(RAG_DIRECTORY):
            for change_type, path_str in changes:
                # We only care about new files being added.
                if change_type.name == "added":
                    file_path = Path(path_str)
                    logger.info(f"New file detected in RAG directory: {file_path.name}")
                    # Schedule ingestion as a background task to avoid blocking the watcher
                    asyncio.create_task(ingest_file(file_path))

    except Exception as e:
        logger.error(f"Error in RAG directory watcher: {e}", exc_info=False)


x_watch_rag_directory__mutmut_mutants: ClassVar[MutantDict] = {
    "x_watch_rag_directory__mutmut_1": x_watch_rag_directory__mutmut_1,
    "x_watch_rag_directory__mutmut_2": x_watch_rag_directory__mutmut_2,
    "x_watch_rag_directory__mutmut_3": x_watch_rag_directory__mutmut_3,
    "x_watch_rag_directory__mutmut_4": x_watch_rag_directory__mutmut_4,
    "x_watch_rag_directory__mutmut_5": x_watch_rag_directory__mutmut_5,
    "x_watch_rag_directory__mutmut_6": x_watch_rag_directory__mutmut_6,
    "x_watch_rag_directory__mutmut_7": x_watch_rag_directory__mutmut_7,
    "x_watch_rag_directory__mutmut_8": x_watch_rag_directory__mutmut_8,
    "x_watch_rag_directory__mutmut_9": x_watch_rag_directory__mutmut_9,
    "x_watch_rag_directory__mutmut_10": x_watch_rag_directory__mutmut_10,
    "x_watch_rag_directory__mutmut_11": x_watch_rag_directory__mutmut_11,
    "x_watch_rag_directory__mutmut_12": x_watch_rag_directory__mutmut_12,
    "x_watch_rag_directory__mutmut_13": x_watch_rag_directory__mutmut_13,
    "x_watch_rag_directory__mutmut_14": x_watch_rag_directory__mutmut_14,
    "x_watch_rag_directory__mutmut_15": x_watch_rag_directory__mutmut_15,
    "x_watch_rag_directory__mutmut_16": x_watch_rag_directory__mutmut_16,
    "x_watch_rag_directory__mutmut_17": x_watch_rag_directory__mutmut_17,
}


def watch_rag_directory(*args, **kwargs):
    result = _mutmut_trampoline(
        x_watch_rag_directory__mutmut_orig,
        x_watch_rag_directory__mutmut_mutants,
        args,
        kwargs,
    )
    return result


watch_rag_directory.__signature__ = _mutmut_signature(
    x_watch_rag_directory__mutmut_orig
)
x_watch_rag_directory__mutmut_orig.__name__ = "x_watch_rag_directory"
