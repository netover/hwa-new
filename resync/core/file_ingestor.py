# resync/core/file_ingestor.py
from __future__ import annotations

import logging
import os
import re
import shutil
from pathlib import Path
from typing import Iterator, Optional

import docx
import openpyxl
import pypdf
from openpyxl.utils.exceptions import InvalidFileException

from resync.core.exceptions import FileProcessingError, KnowledgeGraphError
from resync.core.interfaces import IFileIngestor, IKnowledgeGraph
from resync.settings import settings

logger = logging.getLogger(__name__)


# --- Text Chunking --- #

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> Iterator[str]:
    """Splits a long text into smaller chunks with overlap."""
    if not text:
        return

    start = 0
    while start < len(text):
        end = start + chunk_size
        yield text[start:end]
        start += chunk_size - chunk_overlap


# --- File Readers --- #

def read_pdf(file_path: Path) -> str:
    """Extracts text from a PDF file."""
    logger.info(f"Reading PDF file: {file_path}")
    try:
        reader = pypdf.PdfReader(file_path)
        text = "".join(
            page.extract_text() for page in reader.pages if page.extract_text()
        )
        return text
    except FileNotFoundError as e:
        logger.error("PDF file not found: %s - %s", file_path, e, exc_info=True)
        return ""
    except PermissionError as e:
        logger.error("Permission denied accessing PDF file: %s - %s", file_path, e, exc_info=True)
        return ""
    except pypdf.errors.PdfReadError as e:
        logger.error("PDF read error: %s - %s", file_path, e, exc_info=True)
        return ""
    except ValueError as e:
        logger.error("Invalid PDF content: %s - %s", file_path, e, exc_info=True)
        return ""
    except Exception as e:
        logger.error("Unexpected error reading PDF %s: %s", file_path, e, exc_info=True)
        raise FileProcessingError(f"Failed to read PDF {file_path}: {e}") from e


def read_docx(file_path: Path) -> str:
    """Extracts text from a DOCX file."""
    logger.info(f"Reading DOCX file: {file_path}")
    try:
        doc = docx.Document(file_path)
        text = "\n".join(para.text for para in doc.paragraphs if para.text)
        return text
    except FileNotFoundError as e:
        logger.error("DOCX file not found: %s - %s", file_path, e, exc_info=True)
        return ""
    except PermissionError as e:
        logger.error("Permission denied accessing DOCX file: %s - %s", file_path, e, exc_info=True)
        return ""
    except PackageNotFoundError as e:
        logger.error("Invalid DOCX package: %s - %s", file_path, e, exc_info=True)
        return ""
    except ValueError as e:
        logger.error("Invalid DOCX content: %s - %s", file_path, e, exc_info=True)
        return ""
    except Exception as e:
        logger.error("Unexpected error reading DOCX %s: %s", file_path, e, exc_info=True)
        raise FileProcessingError(f"Failed to read DOCX {file_path}: {e}") from e


def read_excel(file_path: Path) -> str:
    """Extracts text from an XLSX file, iterating through all sheets and cells."""
    logger.info(f"Reading Excel file: {file_path}")
    text_parts = []
    try:
        workbook = openpyxl.load_workbook(file_path, read_only=True)
        for sheetname in workbook.sheetnames:
            sheet = workbook[sheetname]
            text_parts.append(f"Sheet: {sheetname}\n")
            for row in sheet.iter_rows():
                row_texts = []
                for cell in row:
                    if cell.value is not None:
                        row_texts.append(str(cell.value))
                if row_texts:
                    text_parts.append(" | ".join(row_texts))
        return "\n".join(text_parts)
    except FileNotFoundError as e:
        logger.error("Excel file not found: %s - %s", file_path, e, exc_info=True)
        return ""
    except PermissionError as e:
        logger.error("Permission denied accessing Excel file: %s - %s", file_path, e, exc_info=True)
        return ""
    except InvalidFileException as e:
        logger.error("Invalid Excel file: %s - %s", file_path, e, exc_info=True)
        return ""
    except ValueError as e:
        logger.error("Invalid Excel content: %s - %s", file_path, e, exc_info=True)
        return ""
    except Exception as e:
        logger.error("Unexpected error reading Excel %s: %s", file_path, e, exc_info=True)
        raise FileProcessingError(f"Failed to read Excel {file_path}: {e}") from e


# --- Main Ingestion Logic --- #

class FileIngestor(IFileIngestor):
    """
    Service for ingesting files into the knowledge graph.
    
    This class handles file uploads, saving, and processing for RAG.
    """
    
    def __init__(self, knowledge_graph: IKnowledgeGraph):
        """
        Initialize the FileIngestor with dependencies.
        
        Args:
            knowledge_graph: The knowledge graph service to store extracted content
        """
        self.knowledge_graph = knowledge_graph
        self.rag_directory = settings.BASE_DIR / "rag"
        self.file_readers = {
            ".pdf": read_pdf,
            ".docx": read_docx,
            ".xlsx": read_excel,
        }
        # Ensure the RAG directory exists
        self.rag_directory.mkdir(exist_ok=True)
        logger.info(f"FileIngestor initialized with RAG directory: {self.rag_directory}")
    
    async def save_uploaded_file(self, file_name: str, file_content) -> Path:
        """
        Saves an uploaded file to the RAG directory with proper sanitization.
        
        Args:
            file_name: The original filename
            file_content: A file-like object containing the content
            
        Returns:
            Path to the saved file
            
        Raises:
            FileProcessingError: If the file cannot be saved
        """
        # Sanitize the filename to prevent security risks like path traversal
        basename = os.path.basename(file_name)
        # Remove any characters that aren't alphanumeric, dots, underscores, or hyphens
        safe_filename = re.sub(r"[^\w\-_.]", "", basename)
        if not safe_filename:
            raise FileProcessingError("Invalid filename.")
        
        destination = self.rag_directory / safe_filename
        
        try:
            logger.info(f"Saving uploaded file: {safe_filename}")
            with destination.open("wb") as buffer:
                shutil.copyfileobj(file_content, buffer)
            logger.info(f"Successfully saved file to {destination}")
            return destination
        except Exception as e:
            logger.error(f"Failed to save uploaded file {safe_filename}: {e}", exc_info=True)
            raise FileProcessingError(f"Could not save file: {e}") from e
    
    async def ingest_file(self, file_path: Path) -> bool:
        """
        Ingests a single file into the knowledge graph.
        
        Args:
            file_path: Path to the file to ingest
            
        Returns:
            True if ingestion was successful, False otherwise
        """
        if not file_path.exists():
            logger.warning(f"File not found for ingestion: {file_path}")
            return False
        
        file_ext = file_path.suffix.lower()
        reader = self.file_readers.get(file_ext)
        
        if not reader:
            logger.warning(f"Unsupported file type: {file_ext}. Skipping.")
            return False
        
        # Read the file content
        content = reader(file_path)
        if not content:
            logger.warning(f"No content extracted from {file_path}. Skipping.")
            return False
        
        # Chunk the content and add to knowledge graph
        chunks = list(chunk_text(content))
        chunk_count = 0
        for i, chunk in enumerate(chunks):
            try:
                metadata = {
                    "source_file": str(file_path.name),
                    "chunk_index": i + 1,
                    "total_chunks": len(chunks),
                }
                # Here we add the chunk to the knowledge graph
                await self.knowledge_graph.add_content(content=chunk, metadata=metadata)
                chunk_count += 1
            except KnowledgeGraphError as e:
                logger.error(
                    "Knowledge graph error adding chunk %d from %s: %s", 
                    i+1, file_path, e,
                    exc_info=True,
                )
            except ValueError as e:
                logger.error(
                    "Value error adding chunk %d from %s: %s", 
                    i+1, file_path, e,
                    exc_info=True,
                )
            except TypeError as e:
                logger.error(
                    "Type error adding chunk %d from %s: %s", 
                    i+1, file_path, e,
                    exc_info=True,
                )
            except Exception as e:
                logger.error(
                    "Unexpected error adding chunk %d from %s: %s", 
                    i+1, file_path, e,
                    exc_info=True,
                )
                # We don't re-raise here to allow processing of other chunks
        
        logger.info(
            f"Successfully ingested {chunk_count}/{len(chunks)} chunks from {file_path}"
        )
        return chunk_count > 0


def create_file_ingestor(knowledge_graph: IKnowledgeGraph) -> FileIngestor:
    """
    Factory function to create a FileIngestor instance.
    
    Args:
        knowledge_graph: The knowledge graph service to use
        
    Returns:
        A configured FileIngestor instance
    """
    return FileIngestor(knowledge_graph)