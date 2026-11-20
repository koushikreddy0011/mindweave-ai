"""PDF text extraction and semantic chunking service using PyMuPDF."""

import logging
from dataclasses import dataclass
import fitz  # PyMuPDF

logger = logging.getLogger("mindweave.services.pdf")


@dataclass
class ExtractedChunk:
    """Container for a chunk extracted from a PDF document."""

    chunk_index: int
    page_number: int
    content: str


@dataclass
class ExtractedPDF:
    """Container for extracted PDF content and metadata."""

    total_pages: int
    total_characters: int
    chunks: list[ExtractedChunk]


class PDFExtractionService:
    """Extracts clean text and constructs overlapping passages from PDF binaries in memory."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_and_chunk(self, file_bytes: bytes) -> ExtractedPDF:
        """Parse PDF byte stream, extract page text, and generate overlapping chunks."""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        total_pages = len(doc)
        chunks: list[ExtractedChunk] = []
        chunk_idx = 0
        total_chars = 0

        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            page_text = page.get_text("text").strip()
            total_chars += len(page_text)

            if not page_text:
                continue

            # Split page text into overlapping windows
            start = 0
            while start < len(page_text):
                end = min(start + self.chunk_size, len(page_text))
                chunk_str = page_text[start:end].strip()
                if chunk_str:
                    chunks.append(
                        ExtractedChunk(
                            chunk_index=chunk_idx,
                            page_number=page_num + 1,
                            content=chunk_str,
                        )
                    )
                    chunk_idx += 1

                if end == len(page_text):
                    break
                start += self.chunk_size - self.chunk_overlap

        doc.close()
        logger.info(
            "Extracted %d chunks across %d pages (%d chars total)",
            len(chunks), total_pages, total_chars
        )
        return ExtractedPDF(
            total_pages=total_pages,
            total_characters=total_chars,
            chunks=chunks,
        )
