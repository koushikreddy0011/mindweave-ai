"""Mindmap management API endpoints with relational authorization."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.edge import Edge
from app.models.mindmap import Mindmap
from app.models.node import Node
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.graph import MindmapGraphRead
from app.schemas.mindmap import MindmapCreate, MindmapRead, MindmapUpdate
from app.schemas.node import BatchPositionUpdate, NodeCreate, NodeRead

router = APIRouter(prefix="/mindmaps", tags=["Mindmaps"])


@router.get(
    "",
    response_model=list[MindmapRead],
    summary="List all mindmaps accessible to the authenticated user",
)
@router.get(
    "/",
    response_model=list[MindmapRead],
    include_in_schema=False,
)
async def list_mindmaps(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    workspace_id: Annotated[uuid.UUID | None, Query(description="Filter by workspace ID")] = None,
) -> list[Mindmap]:
    """Retrieve all mindmaps belonging to the user's workspaces."""
    query = (
        select(Mindmap)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(Workspace.user_id == current_user.id)
    )
    if workspace_id is not None:
        query = query.where(Mindmap.workspace_id == workspace_id)

    query = query.order_by(Mindmap.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post(
    "",
    response_model=MindmapRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new mindmap",
)
@router.post(
    "/",
    response_model=MindmapRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_mindmap(
    mindmap_in: MindmapCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Mindmap:
    """Create a new mindmap within an authorized user workspace."""
    ws_result = await db.execute(
        select(Workspace).where(
            Workspace.id == mindmap_in.workspace_id,
            Workspace.user_id == current_user.id,
        )
    )
    workspace = ws_result.scalar_one_or_none()
    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    mindmap = Mindmap(
        workspace_id=mindmap_in.workspace_id,
        title=mindmap_in.title,
        description=mindmap_in.description,
        input_type=mindmap_in.input_type,
        input_prompt=mindmap_in.input_prompt,
        status="draft",
    )
    db.add(mindmap)
    await db.commit()
    await db.refresh(mindmap)
    return mindmap


@router.get(
    "/{mindmap_id}",
    response_model=MindmapRead,
    summary="Get mindmap by ID",
)
async def get_mindmap(
    mindmap_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Mindmap:
    """Retrieve a single mindmap if owned by the authenticated user."""
    result = await db.execute(
        select(Mindmap)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Mindmap.id == mindmap_id,
            Workspace.user_id == current_user.id,
        )
    )
    mindmap = result.scalar_one_or_none()
    if mindmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mindmap not found",
        )
    return mindmap


@router.patch(
    "/{mindmap_id}",
    response_model=MindmapRead,
    summary="Update mindmap details",
)
async def update_mindmap(
    mindmap_id: uuid.UUID,
    mindmap_in: MindmapUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Mindmap:
    """Partially update mindmap attributes if owned by the authenticated user."""
    result = await db.execute(
        select(Mindmap)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Mindmap.id == mindmap_id,
            Workspace.user_id == current_user.id,
        )
    )
    mindmap = result.scalar_one_or_none()
    if mindmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mindmap not found",
        )

    update_data = mindmap_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mindmap, field, value)

    await db.commit()
    await db.refresh(mindmap)
    return mindmap


@router.delete(
    "/{mindmap_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete mindmap",
)
async def delete_mindmap(
    mindmap_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Delete a mindmap if owned by the authenticated user."""
    result = await db.execute(
        select(Mindmap)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Mindmap.id == mindmap_id,
            Workspace.user_id == current_user.id,
        )
    )
    mindmap = result.scalar_one_or_none()
    if mindmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mindmap not found",
        )

    await db.delete(mindmap)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ==============================================================================
# Graph and Node sub-endpoints
# ==============================================================================


@router.get(
    "/{mindmap_id}/graph",
    response_model=MindmapGraphRead,
    summary="Get complete mindmap graph (metadata, nodes, and edges)",
)
async def get_mindmap_graph(
    mindmap_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Retrieve full graph visualization payload for React Flow canvas rendering."""
    # 1. Authorize mindmap ownership
    map_result = await db.execute(
        select(Mindmap)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Mindmap.id == mindmap_id,
            Workspace.user_id == current_user.id,
        )
    )
    mindmap = map_result.scalar_one_or_none()
    if mindmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mindmap not found",
        )

    # 2. Fetch all nodes
    nodes_result = await db.execute(
        select(Node)
        .where(Node.mindmap_id == mindmap_id)
        .order_by(Node.depth.asc(), Node.created_at.asc())
    )
    nodes = list(nodes_result.scalars().all())

    # 3. Fetch all edges
    edges_result = await db.execute(
        select(Edge).where(Edge.mindmap_id == mindmap_id)
    )
    edges = list(edges_result.scalars().all())

    return {
        "mindmap": mindmap,
        "nodes": nodes,
        "edges": edges,
    }


@router.post(
    "/{mindmap_id}/nodes",
    response_model=NodeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a node to a mindmap",
)
async def add_node_to_mindmap(
    mindmap_id: uuid.UUID,
    node_in: NodeCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Node:
    """Add a concept node to the mindmap and automatically establish tree relations."""
    # 1. Authorize mindmap ownership
    map_result = await db.execute(
        select(Mindmap)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Mindmap.id == mindmap_id,
            Workspace.user_id == current_user.id,
        )
    )
    mindmap = map_result.scalar_one_or_none()
    if mindmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mindmap not found",
        )

    # 2. If parent_id provided, verify parent exists in this mindmap and calculate depth
    node_depth = 0
    if node_in.parent_id is not None:
        parent_result = await db.execute(
            select(Node).where(
                Node.id == node_in.parent_id,
                Node.mindmap_id == mindmap_id,
            )
        )
        parent_node = parent_result.scalar_one_or_none()
        if parent_node is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent node not found in this mindmap",
            )
        node_depth = parent_node.depth + 1
    elif node_in.depth > 0:
        node_depth = node_in.depth

    # 3. Create the Node
    new_node = Node(
        mindmap_id=mindmap_id,
        parent_id=node_in.parent_id,
        label=node_in.label,
        description=node_in.description,
        node_type=node_in.node_type,
        depth=node_depth,
        position_x=node_in.position_x,
        position_y=node_in.position_y,
        generation_status=node_in.generation_status,
        node_metadata=node_in.node_metadata,
    )
    db.add(new_node)
    await db.flush()  # Flush so new_node.id is assigned

    # 4. Set as root_node_id if this is the first root node
    if mindmap.root_node_id is None and node_in.parent_id is None:
        mindmap.root_node_id = new_node.id

    # 5. Automatically establish an Edge if parent_id was provided
    if node_in.parent_id is not None:
        edge = Edge(
            mindmap_id=mindmap_id,
            source_node_id=node_in.parent_id,
            target_node_id=new_node.id,
            relationship_type="child_of",
        )
        db.add(edge)

    await db.commit()
    await db.refresh(new_node)
    return new_node


@router.patch(
    "/{mindmap_id}/positions",
    summary="Batch update node coordinates on canvas",
)
async def update_node_positions(
    mindmap_id: uuid.UUID,
    batch: BatchPositionUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, int]:
    """Persist updated (x, y) coordinates for multiple nodes following canvas drag/layout changes."""
    # 1. Authorize mindmap ownership
    map_result = await db.execute(
        select(Mindmap)
        .join(Workspace, Mindmap.workspace_id == Workspace.id)
        .where(
            Mindmap.id == mindmap_id,
            Workspace.user_id == current_user.id,
        )
    )
    mindmap = map_result.scalar_one_or_none()
    if mindmap is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mindmap not found",
        )

    # 2. Update positions in batch
    updated_count = 0
    for item in batch.positions:
        node_result = await db.execute(
            select(Node).where(
                Node.id == item.node_id,
                Node.mindmap_id == mindmap_id,
            )
        )
        node = node_result.scalar_one_or_none()
        if node is not None:
            node.position_x = item.position_x
            node.position_y = item.position_y
            updated_count += 1

    await db.commit()
    return {"updated": updated_count}
