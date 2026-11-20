"""Pydantic schemas for User entity and account operations."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Shared user properties."""

    email: EmailStr
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password must be between 8 and 128 characters",
    )


class UserLogin(BaseModel):
    """Schema for user credentials authentication."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile or password."""

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRead(UserBase):
    """Public user response schema strictly excluding sensitive credentials."""

    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
