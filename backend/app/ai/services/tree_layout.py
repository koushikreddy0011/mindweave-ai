"""Service for calculating non-overlapping 2D canvas coordinates for tree mindmaps."""

from collections import defaultdict
import uuid

from app.models.node import Node

HORIZONTAL_SPACING: float = 320.0
VERTICAL_SPACING: float = 120.0


class TreeLayoutService:
    """Calculates 2D canvas coordinates for hierarchical tree nodes for React Flow rendering."""

    def __init__(
        self,
        horizontal_spacing: float = HORIZONTAL_SPACING,
        vertical_spacing: float = VERTICAL_SPACING,
    ) -> None:
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing

    def apply_layout(self, nodes: list[Node]) -> list[Node]:
        """Compute and assign position_x and position_y for all nodes in the hierarchy."""
        if not nodes:
            return nodes

        if len(nodes) == 1:
            nodes[0].position_x = 0.0
            nodes[0].position_y = 0.0
            return nodes

        # Reconstruct tree hierarchy in-memory
        children_map: dict[uuid.UUID, list[Node]] = defaultdict(list)
        root_node: Node | None = None

        for node in nodes:
            if node.parent_id is None:
                root_node = node
            else:
                children_map[node.parent_id].append(node)

        if root_node is None:
            # Fallback: pick the first node with lowest depth
            root_node = min(nodes, key=lambda n: n.depth)

        current_y: float = 0.0

        def _position_subtree(node: Node) -> float:
            nonlocal current_y

            # Horizontal coordinate is determined by depth
            node.position_x = float(node.depth * self.horizontal_spacing)

            children = children_map.get(node.id, [])
            if not children:
                # Leaf node: assign next available vertical slot
                node.position_y = float(current_y)
                current_y += self.vertical_spacing
                return node.position_y

            # Internal branch or root node: recursively layout children
            child_y_positions = [_position_subtree(child) for child in children]

            # Center parent at midpoint between first and last child
            node.position_y = float((child_y_positions[0] + child_y_positions[-1]) / 2.0)
            return node.position_y

        _position_subtree(root_node)
        return nodes
