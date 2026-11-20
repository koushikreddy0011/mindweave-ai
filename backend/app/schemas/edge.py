"""Pydantic schemas for Mindmap Edge connections."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EdgeBase(BaseModel):
    """Shared properties for directed graph edges."""

    relationship_type: str = Field(default="child_of", max_length=50)
    label: str | None = Field(default=None, max_length=100)


class EdgeRead(EdgeBase):
    """Public edge response schema."""

    id: uuid.UUID
    mindmap_id: uuid.UUID
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
