"""Validation script for TreeLayoutService and 2D canvas positioning integration."""

import sys
import uuid
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ai.services import GraphNormalizer, TreeLayoutService
from app.models.node import Node
from app.schemas.ai import TopicHierarchyOutput


def build_sample_nodes() -> tuple[list[Node], Node, list[Node], list[Node]]:
    """Build a manual 3-level, 6-node tree for pure layout unit testing."""
    mindmap_id = uuid.uuid4()
    root_id = uuid.uuid4()
    branch1_id = uuid.uuid4()
    branch2_id = uuid.uuid4()
    leaf1_id = uuid.uuid4()
    leaf2_id = uuid.uuid4()
    leaf3_id = uuid.uuid4()

    root = Node(
        id=root_id,
        mindmap_id=mindmap_id,
        parent_id=None,
        label="Root Node",
        depth=0,
        node_type="root",
    )
    b1 = Node(
        id=branch1_id,
        mindmap_id=mindmap_id,
        parent_id=root_id,
        label="Branch 1",
        depth=1,
        node_type="branch",
    )
    b2 = Node(
        id=branch2_id,
        mindmap_id=mindmap_id,
        parent_id=root_id,
        label="Branch 2",
        depth=1,
        node_type="branch",
    )
    l1 = Node(
        id=leaf1_id,
        mindmap_id=mindmap_id,
        parent_id=branch1_id,
        label="Leaf 1",
        depth=2,
        node_type="leaf",
    )
    l2 = Node(
        id=leaf2_id,
        mindmap_id=mindmap_id,
        parent_id=branch1_id,
        label="Leaf 2",
        depth=2,
        node_type="leaf",
    )
    l3 = Node(
        id=leaf3_id,
        mindmap_id=mindmap_id,
        parent_id=branch2_id,
        label="Leaf 3",
        depth=2,
        node_type="leaf",
    )

    all_nodes = [root, b1, b2, l1, l2, l3]
    return all_nodes, root, [b1, b2], [l1, l2, l3]


def run_tests() -> int:
    """Execute layout calculation tests."""
    print("=" * 65)
    print("MindWeave AI — TreeLayoutService Verification")
    print("=" * 65)

    layout_service = TreeLayoutService()

    # 1. Single-node tree test
    print("\n[1] Testing single-node tree placement...")
    single_node = Node(
        id=uuid.uuid4(),
        mindmap_id=uuid.uuid4(),
        parent_id=None,
        label="Solo Concept",
        depth=0,
        node_type="root",
        position_x=999.0,
        position_y=999.0,
    )
    layout_service.apply_layout([single_node])
    assert single_node.position_x == 0.0, f"Expected x=0.0, got {single_node.position_x}"
    assert single_node.position_y == 0.0, f"Expected y=0.0, got {single_node.position_y}"
    print("  [✓] Single-node tree correctly positioned at (0.0, 0.0)")

    # 2. Multi-level hierarchy geometry tests
    print("\n[2] Testing 3-level tree layout geometry (6 nodes)...")
    nodes, root, branches, leaves = build_sample_nodes()
    layout_service.apply_layout(nodes)

    # Asserts on X coordinates (depth based)
    assert root.position_x == 0.0, f"Expected root x=0.0, got {root.position_x}"
    for b in branches:
        assert b.position_x == 320.0, f"Expected branch x=320.0, got {b.position_x}"
    for leaf in leaves:
        assert leaf.position_x == 640.0, f"Expected leaf x=640.0, got {leaf.position_x}"
    print("  [✓] Verified X coordinates by depth: root=0.0, branches=320.0, leaves=640.0")

    # Asserts on Leaf Y coordinates (strictly increasing)
    l1, l2, l3 = leaves
    assert l1.position_y < l2.position_y < l3.position_y, (
        f"Leaves must have increasing Y coordinates: l1={l1.position_y}, l2={l2.position_y}, l3={l3.position_y}"
    )
    assert l1.position_y == 0.0
    assert l2.position_y == 120.0
    assert l3.position_y == 240.0
    print(f"  [✓] Leaf Y positions strictly increasing: [{l1.position_y}, {l2.position_y}, {l3.position_y}]")

    # Asserts on Branch midpoints
    b1, b2 = branches
    # b1 has children l1 (0.0) and l2 (120.0) -> midpoint is 60.0
    assert b1.position_y == (l1.position_y + l2.position_y) / 2.0
    assert b1.position_y == 60.0, f"Expected Branch 1 y=60.0, got {b1.position_y}"

    # b2 has single child l3 (240.0) -> midpoint is 240.0
    assert b2.position_y == l3.position_y
    assert b2.position_y == 240.0, f"Expected Branch 2 y=240.0, got {b2.position_y}"
    print(f"  [✓] Branch 1 centered at y={b1.position_y} between children ({l1.position_y}, {l2.position_y})")
    print(f"  [✓] Branch 2 aligned at y={b2.position_y} matching child ({l3.position_y})")

    # Asserts on Root midpoint between branches (b1=60.0, b2=240.0) -> 150.0
    expected_root_y = (b1.position_y + b2.position_y) / 2.0
    assert root.position_y == expected_root_y
    assert root.position_y == 150.0, f"Expected root y=150.0, got {root.position_y}"
    print(f"  [✓] Root node centered at y={root.position_y} between branches ({b1.position_y}, {b2.position_y})")

    # Collision test: all (x, y) coordinates must be unique
    coordinates = [(n.position_x, n.position_y) for n in nodes]
    unique_coords = set(coordinates)
    assert len(unique_coords) == len(nodes), (
        f"Detected overlapping coordinates! Total: {len(nodes)}, Unique: {len(unique_coords)}"
    )
    print(f"  [✓] Collision test passed: all {len(nodes)} nodes occupy distinct (x, y) coordinates")

    # 3. Integration with GraphNormalizer
    print("\n[3] Testing GraphNormalizer integration with automatic layout...")
    sample_hierarchy = {
        "topic": "Machine Learning",
        "summary": "Core foundational pillars of machine learning.",
        "target_audience": "beginner",
        "root": {
            "label": "Machine Learning",
            "description": "Core discipline.",
            "node_type": "root",
            "children": [
                {
                    "label": "Supervised Learning",
                    "description": "Learning from labels.",
                    "node_type": "branch",
                    "children": [
                        {
                            "label": "Linear Regression",
                            "description": "Continuous prediction.",
                            "node_type": "leaf",
                            "children": [],
                        },
                        {
                            "label": "Classification",
                            "description": "Categorical prediction.",
                            "node_type": "leaf",
                            "children": [],
                        },
                    ],
                },
                {
                    "label": "Unsupervised Learning",
                    "description": "Finding hidden patterns.",
                    "node_type": "branch",
                    "children": [
                        {
                            "label": "Clustering",
                            "description": "Grouping data points.",
                            "node_type": "leaf",
                            "children": [],
                        }
                    ],
                },
            ],
        },
    }
    hierarchy = TopicHierarchyOutput.model_validate(sample_hierarchy)
    normalizer = GraphNormalizer()
    normalized = normalizer.normalize(hierarchy, uuid.uuid4())

    # Check that positions are populated and non-zero (except root x)
    norm_root = next(n for n in normalized.nodes if n.id == normalized.root_node_id)
    assert norm_root.position_x == 0.0
    assert norm_root.position_y > 0.0  # Centered at 150.0

    leaf_nodes = [n for n in normalized.nodes if n.depth == 2]
    for leaf in leaf_nodes:
        assert leaf.position_x == 640.0
        assert leaf.position_y >= 0.0

    print("  [✓] GraphNormalizer.normalize() automatically calculated valid 2D coordinates:")
    for n in sorted(normalized.nodes, key=lambda node: (node.depth, node.position_y)):
        print(f"      - [{n.depth}] {n.label[:22]:<22} -> (x={n.position_x:5.1f}, y={n.position_y:5.1f})")

    print("\n" + "=" * 65)
    print("[SUCCESS] All TreeLayoutService and GraphNormalizer tests passed!")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
