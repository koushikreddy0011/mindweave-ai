"""AI generation Pydantic schemas for mindmaps."""

from __future__ import annotations

import uuid
from pydantic import AliasChoices, BaseModel, Field


class TopicGenerationRequest(BaseModel):
    """Schema for topic-to-mindmap generation requests with dual-contract alias support."""

    topic: str = Field(
        min_length=2,
        max_length=200,
        description="The topic to generate a mindmap for",
    )
    workspace_id: uuid.UUID
    depth: int = Field(
        default=3,
        ge=2,
        le=5,
        validation_alias=AliasChoices("depth", "max_depth"),
        description="Depth of mindmap hierarchy (2 to 5 levels)",
    )
    audience: str = Field(
        default="beginner",
        pattern="^(beginner|intermediate|advanced)$",
        validation_alias=AliasChoices("audience", "explanation_level"),
        description="Target audience knowledge level",
    )
    language: str = Field(
        default="English",
        max_length=50,
        description="Language of generated content",
    )
    include_examples: bool = Field(
        default=True,
        description="Whether to include examples in explanations",
    )


class NodeHierarchyItem(BaseModel):
    """Recursive node hierarchy item representing a concept node."""

    label: str = Field(
        min_length=1,
        max_length=255,
        description="Clear concise title of the concept",
    )
    description: str = Field(
        min_length=5,
        max_length=1000,
        description="1-2 sentence overview of what this concept is",
    )
    node_type: str = Field(
        default="branch",
        description="'root', 'branch', or 'leaf'",
    )
    children: list[NodeHierarchyItem] = Field(
        default_factory=list,
        description="Child sub-concepts",
    )

    def get_total_nodes(self) -> int:
        """Recursively calculate the total number of nodes in this subtree including self."""
        return 1 + sum(child.get_total_nodes() for child in self.children)

    def get_max_depth(self) -> int:
        """Recursively calculate the maximum depth of this subtree (self is depth 0)."""
        if not self.children:
            return 0
        return 1 + max(child.get_max_depth() for child in self.children)


class TopicHierarchyOutput(BaseModel):
    """Complete structured output schema for topic-based mindmap generation."""

    topic: str = Field(
        min_length=1,
        max_length=255,
        description="Core topic title",
    )
    summary: str = Field(
        min_length=10,
        max_length=2000,
        description="High level domain summary",
    )
    target_audience: str = Field(
        default="beginner",
        description="Target audience of the mindmap",
    )
    root: NodeHierarchyItem = Field(
        description="The root node of the mindmap hierarchy",
    )

    def get_total_nodes(self) -> int:
        """Recursively calculate total node count across all nested branches."""
        return self.root.get_total_nodes()

    def get_max_depth(self) -> int:
        """Recursively calculate maximum depth starting from root (root is depth 0)."""
        return self.root.get_max_depth()


class AsyncGenerationResponse(BaseModel):
    """Immediate response payload returned upon queuing background mindmap generation."""

    mindmap_id: uuid.UUID
    status: str = "processing"
    message: str = "Mindmap generation started in the background"


class DocumentGenerationRequest(BaseModel):
    """Schema for document-grounded mindmap generation requests."""

    document_id: uuid.UUID
    workspace_id: uuid.UUID
    depth: int = Field(
        default=3,
        ge=2,
        le=5,
        validation_alias=AliasChoices("depth", "max_depth"),
        description="Depth of mindmap hierarchy (2 to 5 levels)",
    )
    audience: str = Field(
        default="intermediate",
        pattern="^(beginner|intermediate|advanced)$",
        validation_alias=AliasChoices("audience", "explanation_level"),
        description="Target audience knowledge level",
    )
    language: str = Field(
        default="English",
        max_length=50,
        description="Language of generated content",
    )
    include_examples: bool = Field(
        default=True,
        description="Whether to include examples in explanations",
    )

