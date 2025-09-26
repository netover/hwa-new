# resync/api/rag_upload.py
from __future__ import annotations

import logging
import os

# Using a simple filename sanitization approach instead of external package
import re
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from resync.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rag", tags=["rag"])

RAG_DIRECTORY = settings.BASE_DIR / "rag"
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


@router.post("/upload", summary="Upload a document for RAG ingestion")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts a file upload and saves it to the RAG directory for processing.
    """
    # Sanitize the filename to prevent security risks like path traversal
    # Remove any path components and sanitize the filename
    basename = os.path.basename(file.filename)
    # Remove any characters that aren't alphanumeric, dots, underscores, or hyphens
    safe_filename = re.sub(r"[^\w\-_.]", "", basename)
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    destination = RAG_DIRECTORY / safe_filename

    # Ensure the RAG directory exists
    RAG_DIRECTORY.mkdir(exist_ok=True)

    try:
        logger.info(f"Receiving uploaded file: {safe_filename}")
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Successfully saved file to {destination}")

    except Exception as e:
        logger.error(
            f"Failed to save uploaded file {safe_filename}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Could not save file: {e}",
        ) from e
    finally:
        file.file.close()

    return {
        "filename": safe_filename,
        "content_type": file.content_type,
        "message": "File uploaded successfully and queued for ingestion.",
    }
