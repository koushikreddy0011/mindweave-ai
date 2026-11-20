"""Document upload, parsing, and RAG chunk retrieval API endpoints."""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.services.embedding_service import EmbeddingService
from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.document import Document, DocumentChunk
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.document import DocumentRead
from app.services.pdf_service import PDFExtractionService

logger = logging.getLogger("mindweave.api.documents")

router = APIRouter(prefix="/documents", tags=["Documents & RAG"])

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post(
    "/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest a PDF document for RAG-grounded mindmaps",
)
async def upload_document(
    workspace_id: Annotated[uuid.UUID, Form(description="Target Workspace ID")],
    file: Annotated[UploadFile, File(description="PDF file to extract and vectorize")],
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentRead:
    """Upload a PDF, extract text into overlapping chunks, compute embeddings, and persist to pgvector."""
    # 1. Authorize workspace
    ws_query = await db.execute(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.user_id == current_user.id,
        )
    )
    workspace = ws_query.scalar_one_or_none()
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    # 2. Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are currently supported (.pdf)",
        )

    # 3. Read file bytes in memory
    file_bytes = await file.read()
    file_size = len(file_bytes)
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB",
        )

    # 4. Extract and chunk text
    pdf_service = PDFExtractionService()
    try:
        extracted = pdf_service.extract_and_chunk(file_bytes)
    except Exception as exc:
        logger.error("Failed to parse PDF '%s': %s", file.filename, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to extract text from PDF: {exc}",
        ) from exc

    if not extracted.chunks:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No readable text found in PDF. Scanned images without OCR are not supported.",
        )

    # 5. Create Document record
    doc_id = uuid.uuid4()
    document = Document(
        id=doc_id,
        workspace_id=workspace_id,
        filename=file.filename,
        file_size_bytes=file_size,
        total_pages=extracted.total_pages,
        status="processed",
    )
    db.add(document)
    await db.flush()

    # 6. Generate embeddings and persist chunks
    embedding_service = EmbeddingService()
    db_chunks = []
    for item in extracted.chunks:
        emb = await embedding_service.generate_embedding(item.content)
        chunk = DocumentChunk(
            id=uuid.uuid4(),
            document_id=doc_id,
            chunk_index=item.chunk_index,
            page_number=item.page_number,
            content=item.content,
            embedding=emb,
        )
        db_chunks.append(chunk)

    db.add_all(db_chunks)
    await db.commit()
    await db.refresh(document)

    logger.info("Successfully ingested document '%s' with %d chunks", document.filename, len(db_chunks))

    return DocumentRead(
        id=document.id,
        workspace_id=document.workspace_id,
        filename=document.filename,
        file_size_bytes=document.file_size_bytes,
        total_pages=document.total_pages,
        status=document.status,
        chunks_count=len(db_chunks),
        created_at=document.created_at,
    )


@router.get(
    "",
    response_model=list[DocumentRead],
    summary="List all documents accessible to the authenticated user",
)
async def list_documents(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    workspace_id: Annotated[uuid.UUID | None, Query(description="Filter by workspace ID")] = None,
) -> list[DocumentRead]:
    """Retrieve all ingested documents with chunk counts."""
    query = (
        select(Document)
        .join(Workspace, Document.workspace_id == Workspace.id)
        .where(Workspace.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    if workspace_id:
        query = query.where(Document.workspace_id == workspace_id)

    result = await db.execute(query)
    docs = result.scalars().all()

    return [
        DocumentRead(
            id=d.id,
            workspace_id=d.workspace_id,
            filename=d.filename,
            file_size_bytes=d.file_size_bytes,
            total_pages=d.total_pages,
            status=d.status,
            chunks_count=len(d.chunks),
            created_at=d.created_at,
        )
        for d in docs
    ]


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
    summary="Get details of a single document",
)
async def get_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DocumentRead:
    """Retrieve metadata and chunk stats for a specific document."""
    result = await db.execute(
        select(Document)
        .join(Workspace, Document.workspace_id == Workspace.id)
        .where(
            Document.id == document_id,
            Workspace.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return DocumentRead(
        id=doc.id,
        workspace_id=doc.workspace_id,
        filename=doc.filename,
        file_size_bytes=doc.file_size_bytes,
        total_pages=doc.total_pages,
        status=doc.status,
        chunks_count=len(doc.chunks),
        created_at=doc.created_at,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document and its vectorized chunks",
)
async def delete_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete document by ID with automatic cascade delete on chunks."""
    result = await db.execute(
        select(Document)
        .join(Workspace, Document.workspace_id == Workspace.id)
        .where(
            Document.id == document_id,
            Workspace.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    await db.delete(doc)
    await db.commit()
