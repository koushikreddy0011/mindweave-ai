"""AI generation API endpoints orchestrating asynchronous and synchronous mindmap creation."""

import logging
import time
from typing import Annotated, Any
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.services import GraphNormalizer, MindmapGenerationService
from app.api.deps import get_current_active_user
from app.core.database import async_session_maker, get_db
from app.models.document import Document, DocumentChunk
from app.models.edge import Edge
from app.models.mindmap import Mindmap
from app.models.node import Node
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.ai import AsyncGenerationResponse, DocumentGenerationRequest, TopicGenerationRequest
from app.schemas.graph import MindmapGraphRead

logger = logging.getLogger("mindweave.generations")

router = APIRouter(prefix="/generations", tags=["AI Generations"])


async def _run_background_generation(
    mindmap_id: uuid.UUID,
    req: TopicGenerationRequest,
) -> None:
    """Independent background task processing AI hierarchy generation and persistence."""
    logger.info("Executing background AI generation for mindmap_id=%s (topic='%s')", mindmap_id, req.topic)
    async with async_session_maker() as session:
        try:
            # 1. Fetch mindmap record
            mm_res = await session.execute(select(Mindmap).where(Mindmap.id == mindmap_id))
            mindmap = mm_res.scalar_one_or_none()
            if not mindmap:
                logger.error("Background task: Mindmap '%s' not found", mindmap_id)
                return

            # 2. Invoke Gemini AI Hierarchy generation
            ai_service = MindmapGenerationService()
            start_gen = time.perf_counter()
            hierarchy = await ai_service.generate_topic_hierarchy(
                topic=req.topic,
                depth=req.depth,
                audience=req.audience,
                language=req.language,
            )
            duration = round(time.perf_counter() - start_gen, 2)
            logger.info("Background Gemini generation completed in %.2fs (nodes=%d)", duration, hierarchy.get_total_nodes())

            # 3. Normalize tree and compute 2D positions
            normalizer = GraphNormalizer()
            normalized = normalizer.normalize(hierarchy, mindmap_id=mindmap.id)

            # 4. Atomically persist nodes and edges
            await normalizer.persist_to_db(session, mindmap_id=mindmap.id, normalized=normalized)

            # 5. Mark as completed
            mindmap.status = "completed"
            mindmap.description = hierarchy.summary
            mindmap.root_node_id = normalized.root_node_id
            await session.commit()
            logger.info("Background task complete: Mindmap '%s' is now 'completed'", mindmap_id)

        except Exception as exc:
            logger.exception("Background generation failed for mindmap '%s': %s", mindmap_id, exc)
            try:
                mm_fail = await session.execute(select(Mindmap).where(Mindmap.id == mindmap_id))
                failed_map = mm_fail.scalar_one_or_none()
                if failed_map:
                    failed_map.status = "failed"
                    await session.commit()
            except Exception as commit_exc:
                logger.error("Failed to mark mindmap as failed: %s", commit_exc)


async def _run_background_document_generation(
    mindmap_id: uuid.UUID,
    document_id: uuid.UUID,
    req: DocumentGenerationRequest,
) -> None:
    """Background worker for document-grounded hierarchy generation."""
    logger.info("Executing background document mindmap generation for doc_id=%s", document_id)
    async with async_session_maker() as session:
        try:
            # 1. Fetch document and chunks
            doc_query = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            document = doc_query.scalar_one_or_none()
            if not document:
                logger.error("Document '%s' not found", document_id)
                return

            chunk_query = await session.execute(
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index.asc())
            )
            chunks = chunk_query.scalars().all()
            chunks_text = [c.content for c in chunks]

            # 2. Generate grounded hierarchy
            ai_service = MindmapGenerationService()
            hierarchy = await ai_service.generate_document_hierarchy(
                filename=document.filename,
                chunks_text=chunks_text,
                depth=req.depth,
                audience=req.audience,
                language=req.language,
            )

            # 3. Normalize & persist
            normalizer = GraphNormalizer()
            normalized = normalizer.normalize(hierarchy, mindmap_id=mindmap_id)
            await normalizer.persist_to_db(session, mindmap_id=mindmap_id, normalized=normalized)

            # 4. Mark completed
            mm_query = await session.execute(select(Mindmap).where(Mindmap.id == mindmap_id))
            mindmap = mm_query.scalar_one_or_none()
            if mindmap:
                mindmap.status = "completed"
                mindmap.description = hierarchy.summary
                mindmap.root_node_id = normalized.root_node_id
                await session.commit()
                logger.info("Document mindmap '%s' generation complete", mindmap_id)
        except Exception as exc:
            logger.exception("Failed document generation for '%s': %s", mindmap_id, exc)
            mm_fail = await session.execute(select(Mindmap).where(Mindmap.id == mindmap_id))
            m = mm_fail.scalar_one_or_none()
            if m:
                m.status = "failed"
                await session.commit()


@router.post(
    "/topic",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate hierarchical mindmap asynchronously (or synchronously with async_mode=false)",
)
async def generate_topic_mindmap(
    req: TopicGenerationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks,
    response: Response,
    async_mode: Annotated[bool, Query(description="Run generation asynchronously")] = True,
) -> Any:
    """Orchestrate AI topic hierarchy generation, supporting both 202 Accepted async queuing and sync execution."""
    # Step 1: Verify workspace authorization
    ws_res = await db.execute(
        select(Workspace).where(
            Workspace.id == req.workspace_id,
            Workspace.user_id == current_user.id,
        )
    )
    workspace = ws_res.scalar_one_or_none()
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    # Step 2: Initialize Mindmap record in processing status
    mindmap = Mindmap(
        id=uuid.uuid4(),
        workspace_id=req.workspace_id,
        title=req.topic,
        input_type="topic",
        input_prompt=req.topic,
        status="processing",
    )
    db.add(mindmap)
    await db.commit()
    await db.refresh(mindmap)

    # Step 3A: Async Mode (Default for UI) -> Return 202 Accepted immediately
    if async_mode:
        background_tasks.add_task(_run_background_generation, mindmap.id, req)
        response.status_code = status.HTTP_202_ACCEPTED
        return AsyncGenerationResponse(
            mindmap_id=mindmap.id,
            status="processing",
            message="Mindmap generation initiated in the background",
        )

    # Step 3B: Synchronous Mode (For automated tests)
    ai_service = MindmapGenerationService()
    try:
        hierarchy = await ai_service.generate_topic_hierarchy(
            topic=req.topic,
            depth=req.depth,
            audience=req.audience,
            language=req.language,
        )
    except Exception as exc:
        mindmap.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI generation failed: {exc}",
        ) from exc

    normalizer = GraphNormalizer()
    normalized = normalizer.normalize(hierarchy, mindmap_id=mindmap.id)
    await normalizer.persist_to_db(db, mindmap_id=mindmap.id, normalized=normalized)

    mindmap.status = "completed"
    mindmap.description = hierarchy.summary
    mindmap.root_node_id = normalized.root_node_id
    await db.commit()
    await db.refresh(mindmap)

    nodes_result = await db.execute(
        select(Node).where(Node.mindmap_id == mindmap.id).order_by(Node.depth.asc(), Node.created_at.asc())
    )
    nodes = nodes_result.scalars().all()

    edges_result = await db.execute(
        select(Edge).where(Edge.mindmap_id == mindmap.id).order_by(Edge.created_at.asc())
    )
    edges = edges_result.scalars().all()

    response.status_code = status.HTTP_201_CREATED
    return {
        "mindmap": mindmap,
        "nodes": nodes,
        "edges": edges,
    }


@router.post(
    "/document",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate hierarchical mindmap grounded on uploaded PDF document",
)
async def generate_document_mindmap(
    req: DocumentGenerationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks,
    response: Response,
    async_mode: Annotated[bool, Query(description="Run generation asynchronously")] = True,
) -> Any:
    """Orchestrate document-grounded AI hierarchy generation."""
    # Verify document exists and belongs to workspace
    doc_res = await db.execute(
        select(Document)
        .join(Workspace, Document.workspace_id == Workspace.id)
        .where(
            Document.id == req.document_id,
            Workspace.user_id == current_user.id,
        )
    )
    document = doc_res.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    mindmap_title = document.filename.rsplit(".", 1)[0].replace("_", " ").title()
    mindmap = Mindmap(
        id=uuid.uuid4(),
        workspace_id=req.workspace_id,
        title=f"Doc: {mindmap_title}",
        input_type="document",
        input_prompt=f"Grounded on file: {document.filename}",
        status="processing",
    )
    db.add(mindmap)
    await db.commit()
    await db.refresh(mindmap)

    if async_mode:
        background_tasks.add_task(_run_background_document_generation, mindmap.id, document.id, req)
        response.status_code = status.HTTP_202_ACCEPTED
        return AsyncGenerationResponse(
            mindmap_id=mindmap.id,
            status="processing",
            message="Document-grounded mindmap generation started in the background",
        )

    # Synchronous execution
    chunks_q = await db.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == document.id).order_by(DocumentChunk.chunk_index.asc())
    )
    chunks = chunks_q.scalars().all()
    ai_service = MindmapGenerationService()
    hierarchy = await ai_service.generate_document_hierarchy(
        filename=document.filename,
        chunks_text=[c.content for c in chunks],
        depth=req.depth,
        audience=req.audience,
        language=req.language,
    )
    normalizer = GraphNormalizer()
    normalized = normalizer.normalize(hierarchy, mindmap_id=mindmap.id)
    await normalizer.persist_to_db(db, mindmap_id=mindmap.id, normalized=normalized)
    mindmap.status = "completed"
    mindmap.description = hierarchy.summary
    mindmap.root_node_id = normalized.root_node_id
    await db.commit()
    await db.refresh(mindmap)

    nodes = (await db.execute(select(Node).where(Node.mindmap_id == mindmap.id))).scalars().all()
    edges = (await db.execute(select(Edge).where(Edge.mindmap_id == mindmap.id))).scalars().all()
    response.status_code = status.HTTP_201_CREATED
    return {"mindmap": mindmap, "nodes": nodes, "edges": edges}
