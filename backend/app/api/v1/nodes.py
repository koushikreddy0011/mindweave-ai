"""Node management API endpoints with relational authorization."""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.ai.services import NodeExplanationService
from app.core.database import get_db
from app.models.explanation import NodeExplanation
from app.models.mindmap import Mindmap
from app.models.node import Node
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.explanation import NodeExplanationRead
from app.schemas.node import NodeRead, NodeUpdate

logger = logging.getLogger("mindweave.nodes")

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.patch(
    "/{node_id}",
    response_model=NodeRead,
    summary="Update node details",
)
async def update_node(
    node_id: uuid.UUID,
    node_in: NodeUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Node:
    """Partially update concept node attributes if authorized."""
    result = await db.execute(
        select(Node)
        .join(Mindmap, Node.mindmap_id == Mindmap.id)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Node.id == node_id,
            Workspace.user_id == current_user.id,
        )
    )
    node = result.scalar_one_or_none()
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    update_data = node_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(node, field, value)

    await db.commit()
    await db.refresh(node)
    return node


@router.delete(
    "/{node_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete node",
)
async def delete_node(
    node_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Delete a concept node and cascade deletions to descendants and connecting edges."""
    result = await db.execute(
        select(Node, Mindmap)
        .join(Mindmap, Node.mindmap_id == Mindmap.id)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Node.id == node_id,
            Workspace.user_id == current_user.id,
        )
    )
    row = result.first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    node, mindmap = row

    # Clear root_node_id if the deleted node was the root
    if mindmap.root_node_id == node.id:
        mindmap.root_node_id = None

    await db.delete(node)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{node_id}/explain",
    response_model=NodeExplanationRead,
    summary="Generate or fetch cached explanation for a concept node",
)
async def explain_node(
    node_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    level: str = Query(default="beginner", pattern="^(beginner|intermediate|advanced)$"),
) -> NodeExplanation:
    """Generate or retrieve a cached educational explanation for an authorized concept node."""
    result = await db.execute(
        select(Node)
        .join(Mindmap, Node.mindmap_id == Mindmap.id)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Node.id == node_id,
            Workspace.user_id == current_user.id,
        )
    )
    node = result.scalar_one_or_none()
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    service = NodeExplanationService()
    try:
        explanation = await service.get_or_generate_explanation(db, node_id=node.id, level=level)
        return explanation
    except Exception as exc:
        logger.error(
            "Failed generating explanation for node '%s': %s",
            node_id,
            exc,
            exc_info=True,
        )
        err_str = str(exc)
        status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
            if "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str.lower()
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        raise HTTPException(
            status_code=status_code,
            detail=f"AI explanation generation error: {exc}",
        ) from exc


@router.get(
    "/{node_id}/explanation",
    response_model=NodeExplanationRead,
    summary="Get cached explanation for a concept node",
)
async def get_node_explanation(
    node_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    level: str = Query(default="beginner", pattern="^(beginner|intermediate|advanced)$"),
) -> NodeExplanation:
    """Retrieve an existing cached explanation for an authorized concept node."""
    result = await db.execute(
        select(Node)
        .join(Mindmap, Node.mindmap_id == Mindmap.id)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Node.id == node_id,
            Workspace.user_id == current_user.id,
        )
    )
    node = result.scalar_one_or_none()
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    exp_result = await db.execute(
        select(NodeExplanation)
        .where(
            NodeExplanation.node_id == node_id,
            NodeExplanation.level == level,
        )
        .order_by(NodeExplanation.created_at.desc())
    )
    explanation = exp_result.scalars().first()
    if explanation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Explanation at '{level}' level not found for this node",
        )
    return explanation
