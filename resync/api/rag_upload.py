# resync/api/rag_upload.py
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from resync.core.exceptions import FileProcessingError
from resync.core.fastapi_di import get_file_ingestor
from resync.core.interfaces import IFileIngestor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rag", tags=["rag"])


@router.post("/upload", summary="Upload a document for RAG ingestion")
async def upload_document(
    file: UploadFile = File(...),
    file_ingestor: IFileIngestor = Depends(get_file_ingestor),
):
    """
    Accepts a file upload and saves it to the RAG directory for processing.
    """
    try:
        # Save the uploaded file
        destination = await file_ingestor.save_uploaded_file(
            file_name=file.filename,
            file_content=file.file,
        )

        # Start file ingestion in the background
        # We don't want to block the response while processing potentially large files
        asyncio.create_task(file_ingestor.ingest_file(destination))

        # Get the filename from the path
        safe_filename = destination.name

        return {
            "filename": safe_filename,
            "content_type": file.content_type,
            "message": "File uploaded successfully and queued for ingestion.",
        }
    except FileProcessingError as e:
        logger.error(f"File processing error: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Failed to process uploaded file: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Could not process file: {e}",
        ) from e
    finally:
        await file.close()
