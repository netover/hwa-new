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
        # Validate file type and size
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Check file extension (only allow specific file types)
        allowed_extensions = {'.pdf', '.docx', '.xlsx', '.txt', '.csv', '.json'}
        file_extension = '.' + file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Check file size (limit to 10MB)
        # FastAPI doesn't provide file size directly for UploadFile, so we'll check after reading
        # But we can at least validate that the content type is appropriate
        if file.content_type and not any(allowed_type in file.content_type.lower() 
                                         for allowed_type in ['application/pdf', 'application/vnd.openxmlformats', 
                                                              'application/msword', 'text/plain', 'text/csv', 'application/json']):
            logger.warning(f"Potentially unsafe content type: {file.content_type}")
        
        # Check file size by reading and limiting
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        # Reset file pointer for saving
        await file.seek(0)
        
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
            "size": len(contents),
            "message": "File uploaded successfully and queued for ingestion.",
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
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
