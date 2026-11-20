"""Edge domain model representing directional relations between mindmap nodes."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.mindmap import Mindmap
    from app.models.node import Node


class Edge(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Edge entity representing a link connecting two nodes in a knowledge graph."""

    __tablename__ = "edges"

    mindmap_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mindmaps.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    relationship_type: Mapped[str] = mapped_column(
        String(50),
        default="child_of",
        nullable=False,
    )
    label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    mindmap: Mapped["Mindmap"] = relationship(
        back_populates="edges",
    )
    source_node: Mapped["Node"] = relationship(
        "Node",
        foreign_keys=[source_node_id],
    )
    target_node: Mapped["Node"] = relationship(
        "Node",
        foreign_keys=[target_node_id],
    )

    def __repr__(self) -> str:
        return f"<Edge source={self.source_node_id} target={self.target_node_id} type={self.relationship_type}>"
