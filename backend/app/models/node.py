"""Node domain model representing graph vertices and concept nodes."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.explanation import NodeExplanation
    from app.models.mindmap import Mindmap


class Node(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Node entity representing a single knowledge concept in a mindmap."""

    __tablename__ = "nodes"

    mindmap_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mindmaps.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    node_type: Mapped[str] = mapped_column(
        String(50),
        default="default",
        nullable=False,
    )
    depth: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    position_x: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    position_y: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    generation_status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
        nullable=False,
    )
    node_metadata: Mapped[dict] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False,
    )

    mindmap: Mapped["Mindmap"] = relationship(
        back_populates="nodes",
    )
    parent: Mapped["Node | None"] = relationship(
        "Node",
        remote_side="Node.id",
        back_populates="children",
    )
    children: Mapped[list["Node"]] = relationship(
        "Node",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    explanations: Mapped[list["NodeExplanation"]] = relationship(
        "NodeExplanation",
        back_populates="node",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Node label={self.label} depth={self.depth} mindmap_id={self.mindmap_id}>"
