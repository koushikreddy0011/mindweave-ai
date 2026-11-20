"""Node explanation domain model representing AI-generated knowledge breakdowns."""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.node import Node


class NodeExplanation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Detailed educational explanation for an individual concept node."""

    __tablename__ = "node_explanations"

    node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("nodes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    level: Mapped[str] = mapped_column(
        String(50),
        default="beginner",
        nullable=False,
    )
    overview: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    detailed_explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    how_it_works: Mapped[list[str]] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
    )
    key_concepts: Mapped[list[str]] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
    )
    examples: Mapped[list[str]] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
    )
    applications: Mapped[list[str]] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
    )
    related_concepts: Mapped[list[str]] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    node: Mapped["Node"] = relationship(
        back_populates="explanations",
    )

    def __repr__(self) -> str:
        return f"<NodeExplanation node_id={self.node_id} level={self.level}>"
