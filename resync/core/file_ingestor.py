# resync/core/file_ingestor.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

import docx
import openpyxl
import pypdf

from resync.core.knowledge_graph import knowledge_graph

logger = logging.getLogger(__name__)

# --- Text Chunking --- #


def chunk_text(
    text: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> Iterator[str]:
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
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {e}", exc_info=True)
        return ""


def read_docx(file_path: Path) -> str:
    """Extracts text from a DOCX file."""
    logger.info(f"Reading DOCX file: {file_path}")
    try:
        doc = docx.Document(file_path)
        text = "\n".join(para.text for para in doc.paragraphs if para.text)
        return text
    except Exception as e:
        logger.error(f"Failed to read DOCX {file_path}: {e}", exc_info=True)
        return ""


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
    except Exception as e:
        logger.error(f"Failed to read Excel {file_path}: {e}", exc_info=True)
        return ""


# --- Main Ingestion Logic --- #

FILE_READERS = {
    ".pdf": read_pdf,
    ".docx": read_docx,
    ".xlsx": read_excel,
}


async def ingest_file(file_path: Path):
    """Ingests a single file into the knowledge graph."""
    if not file_path.exists():
        logger.warning(f"File not found for ingestion: {file_path}")
        return

    file_ext = file_path.suffix.lower()
    reader = FILE_READERS.get(file_ext)

    if not reader:
        logger.warning(f"Unsupported file type: {file_ext}. Skipping.")
        return

    # Read the file content
    content = reader(file_path)
    if not content:
        logger.warning(f"No content extracted from {file_path}. Skipping.")
        return

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
            # Here we add the chunk to the knowledge graph.
            # We use the chunk itself as the content.
            await knowledge_graph.add(content=chunk, metadata=metadata)
            chunk_count += 1
        except Exception as e:
            logger.error(
                f"Failed to add chunk {i+1} from {file_path} to knowledge graph: {e}",
                exc_info=True,
            )

    logger.info(
        f"Successfully ingested {chunk_count}/{len(chunks)} chunks from {file_path}"
    )
