"""Service for normalizing hierarchical AI outputs into relational graph models."""

from dataclasses import dataclass
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.services.tree_layout import TreeLayoutService
from app.models.edge import Edge
from app.models.mindmap import Mindmap
from app.models.node import Node
from app.schemas.ai import NodeHierarchyItem, TopicHierarchyOutput


@dataclass
class NormalizedGraph:
    """Container holding normalized relational nodes and edges for a mindmap."""

    root_node_id: uuid.UUID
    nodes: list[Node]
    edges: list[Edge]

    @property
    def total_nodes(self) -> int:
        """Return the total number of normalized nodes."""
        return len(self.nodes)

    @property
    def total_edges(self) -> int:
        """Return the total number of normalized edges."""
        return len(self.edges)


class GraphNormalizer:
    """Flattens hierarchical AI mindmap output trees into relational database entities."""

    def __init__(self, layout_service: TreeLayoutService | None = None) -> None:
        self.layout_service = layout_service or TreeLayoutService()

    def normalize(
        self,
        hierarchy: TopicHierarchyOutput,
        mindmap_id: uuid.UUID,
    ) -> NormalizedGraph:
        """Recursively traverse TopicHierarchyOutput and convert into flat Node and Edge models."""
        flat_nodes: list[Node] = []
        flat_edges: list[Edge] = []

        def _traverse(
            item: NodeHierarchyItem,
            parent_id: uuid.UUID | None = None,
            depth: int = 0,
        ) -> uuid.UUID:
            node_id = uuid.uuid4()

            node = Node(
                id=node_id,
                mindmap_id=mindmap_id,
                parent_id=parent_id,
                label=item.label,
                description=item.description,
                node_type=item.node_type,
                depth=depth,
                position_x=0.0,
                position_y=0.0,
                generation_status="completed",
                node_metadata={},
            )
            flat_nodes.append(node)

            if parent_id is not None:
                edge = Edge(
                    id=uuid.uuid4(),
                    mindmap_id=mindmap_id,
                    source_node_id=parent_id,
                    target_node_id=node_id,
                    relationship_type="child_of",
                )
                flat_edges.append(edge)

            for child in item.children:
                _traverse(child, parent_id=node_id, depth=depth + 1)

            return node_id

        root_id = _traverse(hierarchy.root, parent_id=None, depth=0)

        # Enforce N - 1 edge invariant for tree hierarchies
        if len(flat_nodes) > 0 and len(flat_edges) != len(flat_nodes) - 1:
            raise ValueError(
                f"Tree invariant violated: expected {len(flat_nodes) - 1} edges for "
                f"{len(flat_nodes)} nodes, but got {len(flat_edges)} edges."
            )

        # Calculate 2D canvas coordinates for React Flow
        self.layout_service.apply_layout(flat_nodes)

        return NormalizedGraph(
            root_node_id=root_id,
            nodes=flat_nodes,
            edges=flat_edges,
        )

    async def persist_to_db(
        self,
        db: AsyncSession,
        mindmap_id: uuid.UUID,
        normalized: NormalizedGraph,
    ) -> None:
        """Atomically persist normalized nodes and edges and associate the root node to the mindmap."""
        result = await db.execute(select(Mindmap).where(Mindmap.id == mindmap_id))
        mindmap = result.scalar_one_or_none()
        if mindmap is None:
            raise ValueError(f"Mindmap with id '{mindmap_id}' not found")

        mindmap.root_node_id = normalized.root_node_id
        db.add_all(normalized.nodes)
        db.add_all(normalized.edges)
        await db.commit()
        await db.refresh(mindmap)
