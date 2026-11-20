"""Pydantic schemas for Mindmap Node management and canvas positioning."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NodeBase(BaseModel):
    """Shared properties for mindmap concept nodes."""

    label: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    node_type: str = Field(default="default", max_length=50)
    depth: int = 0
    position_x: float = 0.0
    position_y: float = 0.0
    generation_status: str = Field(default="completed", max_length=50)
    node_metadata: dict = Field(default_factory=dict)


class NodeCreate(NodeBase):
    """Schema for adding a node to a mindmap."""

    parent_id: uuid.UUID | None = None


class NodeUpdate(BaseModel):
    """Schema for updating node attributes."""

    label: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=5000)
    node_type: str | None = Field(default=None, max_length=50)
    position_x: float | None = None
    position_y: float | None = None
    node_metadata: dict | None = None


class NodePositionItem(BaseModel):
    """Single node coordinate update for drag-and-drop canvas layout."""

    node_id: uuid.UUID
    position_x: float
    position_y: float


class BatchPositionUpdate(BaseModel):
    """Batch position payload for canvas state persistence."""

    positions: list[NodePositionItem]


class NodeRead(NodeBase):
    """Public node response schema."""

    id: uuid.UUID
    mindmap_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
