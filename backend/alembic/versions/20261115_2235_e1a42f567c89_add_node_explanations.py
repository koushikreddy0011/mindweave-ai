"""add_node_explanations_table

Revision ID: e1a42f567c89
Revises: 8e4507432d9e
Create Date: 2026-11-15 22:35:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e1a42f567c89"
down_revision: str | None = "8e4507432d9e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "node_explanations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("node_id", sa.Uuid(), nullable=False),
        sa.Column("level", sa.String(length=50), server_default="beginner", nullable=False),
        sa.Column("overview", sa.Text(), nullable=False),
        sa.Column("detailed_explanation", sa.Text(), nullable=False),
        sa.Column("how_it_works", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("key_concepts", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("examples", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("applications", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("related_concepts", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["node_id"], ["nodes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_node_explanations_node_id"), "node_explanations", ["node_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_node_explanations_node_id"), table_name="node_explanations")
    op.drop_table("node_explanations")
