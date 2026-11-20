"""Pydantic schemas for Document management and RAG ingestion."""

import datetime
import uuid
from pydantic import BaseModel, ConfigDict


class DocumentChunkRead(BaseModel):
    """Schema representing an extracted document chunk."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chunk_index: int
    page_number: int
    content: str


class DocumentRead(BaseModel):
    """Schema representing uploaded document metadata and chunk stats."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    filename: str
    file_size_bytes: int
    total_pages: int
    status: str
    chunks_count: int
    created_at: datetime.datetime
