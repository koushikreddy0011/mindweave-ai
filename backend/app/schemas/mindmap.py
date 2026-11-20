"""Pydantic schemas for Mindmap management."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MindmapBase(BaseModel):
    """Shared mindmap properties."""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    input_type: str = Field(default="topic", max_length=50)
    input_prompt: str | None = None


class MindmapCreate(MindmapBase):
    """Schema for creating a new mindmap in a workspace."""

    workspace_id: uuid.UUID


class MindmapUpdate(BaseModel):
    """Schema for updating mindmap attributes."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    status: str | None = Field(default=None, max_length=50)
    root_node_id: uuid.UUID | None = None


class MindmapRead(MindmapBase):
    """Public mindmap response schema."""

    id: uuid.UUID
    workspace_id: uuid.UUID
    status: str
    root_node_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
