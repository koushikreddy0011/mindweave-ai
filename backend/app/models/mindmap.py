"""Mindmap domain model."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.edge import Edge
    from app.models.node import Node
    from app.models.workspace import Workspace


class Mindmap(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Mindmap entity representing an AI-generated or custom knowledge graph."""

    __tablename__ = "mindmaps"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    input_type: Mapped[str] = mapped_column(
        String(50),
        default="topic",
        nullable=False,
    )
    input_prompt: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )
    root_node_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        nullable=True,
    )

    workspace: Mapped["Workspace"] = relationship(
        back_populates="mindmaps",
    )
    nodes: Mapped[list["Node"]] = relationship(
        back_populates="mindmap",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    edges: Mapped[list["Edge"]] = relationship(
        back_populates="mindmap",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Mindmap title={self.title} status={self.status}>"
