"""Pydantic schemas for Workspace management."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceBase(BaseModel):
    """Shared workspace properties."""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)


class WorkspaceCreate(WorkspaceBase):
    """Schema for creating a new workspace."""

    pass


class WorkspaceUpdate(BaseModel):
    """Schema for updating workspace attributes."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)


class WorkspaceRead(WorkspaceBase):
    """Public workspace response schema."""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
