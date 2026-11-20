"""Pydantic composite schemas for full graph payloads."""

from pydantic import BaseModel

from app.schemas.edge import EdgeRead
from app.schemas.mindmap import MindmapRead
from app.schemas.node import NodeRead


class MindmapGraphRead(BaseModel):
    """Complete graph visualization payload containing mindmap metadata, nodes, and edges."""

    mindmap: MindmapRead
    nodes: list[NodeRead]
    edges: list[EdgeRead]
