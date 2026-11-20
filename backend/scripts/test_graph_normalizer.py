"""Validation script for GraphNormalizer service (in-memory & PostgreSQL persistence)."""

import asyncio
import sys
import uuid
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import delete, select

from app.ai.services import GraphNormalizer
from app.core.database import AsyncSessionLocal
from app.models.edge import Edge
from app.models.mindmap import Mindmap
from app.models.node import Node
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.ai import TopicHierarchyOutput


def build_sample_hierarchy() -> TopicHierarchyOutput:
    """Build a standard 3-level, 6-node hierarchy for testing."""
    sample_data = {
        "topic": "Machine Learning",
        "summary": "Core foundational pillars of machine learning and artificial intelligence.",
        "target_audience": "beginner",
        "root": {
            "label": "Machine Learning",
            "description": "Core discipline of statistical computing and AI.",
            "node_type": "root",
            "children": [
                {
                    "label": "Supervised Learning",
                    "description": "Learning from labeled training data.",
                    "node_type": "branch",
                    "children": [
                        {
                            "label": "Linear Regression",
                            "description": "Predicting continuous outcomes.",
                            "node_type": "leaf",
                            "children": [],
                        },
                        {
                            "label": "Classification",
                            "description": "Predicting categorical classes.",
                            "node_type": "leaf",
                            "children": [],
                        },
                    ],
                },
                {
                    "label": "Unsupervised Learning",
                    "description": "Finding hidden structure in unlabeled data.",
                    "node_type": "branch",
                    "children": [
                        {
                            "label": "Clustering",
                            "description": "Grouping observations into clusters.",
                            "node_type": "leaf",
                            "children": [],
                        }
                    ],
                },
            ],
        },
    }
    return TopicHierarchyOutput.model_validate(sample_data)


async def run_tests() -> int:
    """Execute in-memory and database persistence tests for GraphNormalizer."""
    print("=" * 65)
    print("MindWeave AI — GraphNormalizer Service Verification")
    print("=" * 65)

    normalizer = GraphNormalizer()
    hierarchy = build_sample_hierarchy()
    mindmap_id = uuid.uuid4()

    # -------------------------------------------------------------
    # 1. In-Memory Normalization Tests
    # -------------------------------------------------------------
    print("\n[1] Testing in-memory tree flattening and normalization...")
    normalized = normalizer.normalize(hierarchy, mindmap_id)

    # Asserts
    assert len(normalized.nodes) == 6, f"Expected 6 nodes, got {len(normalized.nodes)}"
    assert len(normalized.edges) == 5, f"Expected 5 edges, got {len(normalized.edges)}"
    assert normalized.total_nodes == 6
    assert normalized.total_edges == 5
    print("  [✓] Verified 6 nodes and 5 edges created (|E| = |V| - 1 edge invariant enforced)")

    # Find root node
    root_node = next((n for n in normalized.nodes if n.id == normalized.root_node_id), None)
    assert root_node is not None, "Root node not found in normalized nodes"
    assert root_node.parent_id is None, "Root node must have parent_id = None"
    assert root_node.depth == 0, f"Root depth must be 0, got {root_node.depth}"
    assert root_node.label == "Machine Learning"
    assert root_node.mindmap_id == mindmap_id
    print("  [✓] Verified root node properties (parent_id=None, depth=0, matching mindmap_id)")

    # Verify branch and leaf nodes
    branches = [n for n in normalized.nodes if n.depth == 1]
    leaves = [n for n in normalized.nodes if n.depth == 2]
    assert len(branches) == 2, f"Expected 2 branches, got {len(branches)}"
    assert len(leaves) == 3, f"Expected 3 leaves, got {len(leaves)}"

    for b in branches:
        assert b.parent_id == root_node.id, "Branch parent must be root node"

    branch_ids = {b.id for b in branches}
    for leaf in leaves:
        assert leaf.parent_id in branch_ids, "Leaf parent must be one of the branches"
        assert leaf.node_type == "leaf"

    # Verify edge wiring
    node_id_map = {n.id: n for n in normalized.nodes}
    for edge in normalized.edges:
        assert edge.mindmap_id == mindmap_id
        assert edge.source_node_id in node_id_map
        assert edge.target_node_id in node_id_map
        target = node_id_map[edge.target_node_id]
        assert target.parent_id == edge.source_node_id
        assert edge.relationship_type == "child_of"

    print("  [✓] Verified tree wiring (correct parent UUIDs, depth levels, and edge relations)")

    # -------------------------------------------------------------
    # 2. Live Database Persistence Tests
    # -------------------------------------------------------------
    print("\n[2] Testing atomic database persistence in PostgreSQL...")
    test_user_id = uuid.uuid4()
    test_workspace_id = uuid.uuid4()
    real_mindmap_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        try:
            # Create user, workspace, and mindmap
            test_user = User(
                id=test_user_id,
                email=f"normalizer_test_{uuid.uuid4().hex[:6]}@example.com",
                hashed_password="TestPassword123#Hashed",
                full_name="Normalizer Tester",
            )
            test_workspace = Workspace(
                id=test_workspace_id,
                user_id=test_user_id,
                name="Normalizer Workspace",
            )
            test_mindmap = Mindmap(
                id=real_mindmap_id,
                workspace_id=test_workspace_id,
                title="Machine Learning AI Map",
                input_type="topic",
                status="draft",
            )
            session.add_all([test_user, test_workspace, test_mindmap])
            await session.commit()
            print("  [✓] Created test User, Workspace, and Mindmap in PostgreSQL")

            # Normalize for real mindmap ID and persist
            db_normalized = normalizer.normalize(hierarchy, real_mindmap_id)
            await normalizer.persist_to_db(session, real_mindmap_id, db_normalized)
            print("  [✓] Successfully executed normalizer.persist_to_db()")

            # Verify persisted data in database
            db_nodes_res = await session.execute(
                select(Node).where(Node.mindmap_id == real_mindmap_id)
            )
            persisted_nodes = db_nodes_res.scalars().all()
            assert len(persisted_nodes) == 6, f"Expected 6 persisted nodes, got {len(persisted_nodes)}"

            db_edges_res = await session.execute(
                select(Edge).where(Edge.mindmap_id == real_mindmap_id)
            )
            persisted_edges = db_edges_res.scalars().all()
            assert len(persisted_edges) == 5, f"Expected 5 persisted edges, got {len(persisted_edges)}"

            # Verify mindmap root_node_id
            mindmap_res = await session.execute(
                select(Mindmap).where(Mindmap.id == real_mindmap_id)
            )
            refreshed_mindmap = mindmap_res.scalar_one()
            assert refreshed_mindmap.root_node_id == db_normalized.root_node_id
            print(f"  [✓] Verified Mindmap.root_node_id ({refreshed_mindmap.root_node_id}) matches Root Node")
            print(f"  [✓] Verified 6 Nodes and 5 Edges cleanly persisted with foreign keys")

        finally:
            # Cleanup test user (cascades delete across workspace, mindmap, nodes, edges)
            await session.execute(delete(User).where(User.id == test_user_id))
            await session.commit()
            print("  [✓] Cleanup: Successfully deleted test user and cascaded relational records")

    print("\n" + "=" * 65)
    print("[SUCCESS] All GraphNormalizer in-memory and database tests passed!")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)
