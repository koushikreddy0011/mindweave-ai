"""Validation script for AI generation Pydantic schemas and tree traversal methods."""

import sys
import uuid
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from pydantic import ValidationError

from app.schemas.ai import (
    NodeHierarchyItem,
    TopicGenerationRequest,
    TopicHierarchyOutput,
)


def run_tests() -> int:
    """Execute validation suite for AI schemas and recursive calculations."""
    print("=" * 65)
    print("MindWeave AI — AI Generation Schemas Verification")
    print("=" * 65)

    # 1. Valid nested 3-level tree parses into TopicHierarchyOutput
    print("\n[1] Testing nested 3-level tree parsing...")
    sample_tree = {
        "topic": "Machine Learning",
        "summary": "A foundational branch of AI focused on learning from data to make predictions.",
        "target_audience": "beginner",
        "root": {
            "label": "Machine Learning",
            "description": "Core discipline of training computers using statistical algorithms.",
            "node_type": "root",
            "children": [
                {
                    "label": "Supervised Learning",
                    "description": "Learning mapping functions from labeled input-output pairs.",
                    "node_type": "branch",
                    "children": [
                        {
                            "label": "Linear Regression",
                            "description": "Predicting continuous numeric outputs via linear models.",
                            "node_type": "leaf",
                            "children": [],
                        },
                        {
                            "label": "Classification",
                            "description": "Categorizing inputs into distinct discrete class buckets.",
                            "node_type": "leaf",
                            "children": [],
                        },
                    ],
                },
                {
                    "label": "Unsupervised Learning",
                    "description": "Discovering hidden representations and structures in unlabeled data.",
                    "node_type": "branch",
                    "children": [
                        {
                            "label": "Clustering",
                            "description": "Grouping unlabeled data points into clusters based on similarity.",
                            "node_type": "leaf",
                            "children": [],
                        }
                    ],
                },
            ],
        },
    }

    output = TopicHierarchyOutput.model_validate(sample_tree)
    assert output.topic == "Machine Learning"
    assert output.root.label == "Machine Learning"
    assert len(output.root.children) == 2
    print("  [✓] Successfully parsed 3-level tree into TopicHierarchyOutput")

    # 2. get_total_nodes() verification
    print("\n[2] Testing recursive get_total_nodes()...")
    total_nodes = output.get_total_nodes()
    assert total_nodes == 6, f"Expected 6 total nodes, got {total_nodes}"
    print(f"  [✓] get_total_nodes() correctly returned {total_nodes} nodes (1 root + 2 branches + 3 leaves)")

    # 3. get_max_depth() verification
    print("\n[3] Testing recursive get_max_depth()...")
    max_depth = output.get_max_depth()
    assert max_depth == 2, f"Expected max depth 2 (root is 0), got {max_depth}"
    print(f"  [✓] get_max_depth() correctly returned {max_depth} (depths 0 -> 1 -> 2)")

    # Single-node tree depth verification
    single_node_output = TopicHierarchyOutput(
        topic="Single Node",
        summary="Minimal valid topic summary string with sufficient length.",
        target_audience="beginner",
        root=NodeHierarchyItem(
            label="Root Only",
            description="Root concept with no children attached.",
            node_type="root",
        ),
    )
    assert single_node_output.get_total_nodes() == 1
    assert single_node_output.get_max_depth() == 0
    print("  [✓] get_max_depth() correctly returns 0 for a root-only tree")

    # 4. TopicGenerationRequest validation
    print("\n[4] Testing TopicGenerationRequest validations...")
    valid_workspace_id = uuid.uuid4()

    # Valid request
    valid_request = TopicGenerationRequest(
        topic="Quantum Computing",
        workspace_id=valid_workspace_id,
        depth=3,
        audience="intermediate",
        language="English",
    )
    assert valid_request.depth == 3
    assert valid_request.audience == "intermediate"
    print("  [✓] Valid TopicGenerationRequest created successfully")

    # Invalid: depth > 5
    try:
        TopicGenerationRequest(
            topic="Quantum Computing",
            workspace_id=valid_workspace_id,
            depth=6,
        )
        raise AssertionError("Failed to reject depth > 5")
    except ValidationError:
        print("  [✓] Correctly rejected depth > 5 (le=5)")

    # Invalid: depth < 2
    try:
        TopicGenerationRequest(
            topic="Quantum Computing",
            workspace_id=valid_workspace_id,
            depth=1,
        )
        raise AssertionError("Failed to reject depth < 2")
    except ValidationError:
        print("  [✓] Correctly rejected depth < 2 (ge=2)")

    # Invalid: audience pattern
    try:
        TopicGenerationRequest(
            topic="Quantum Computing",
            workspace_id=valid_workspace_id,
            audience="expert",
        )
        raise AssertionError("Failed to reject audience='expert'")
    except ValidationError:
        print("  [✓] Correctly rejected invalid audience value")

    # Invalid: topic too short (< 2 chars)
    try:
        TopicGenerationRequest(
            topic="Q",
            workspace_id=valid_workspace_id,
        )
        raise AssertionError("Failed to reject topic with length < 2")
    except ValidationError:
        print("  [✓] Correctly rejected topic with length < 2")

    # 5. NodeHierarchyItem invalid field validations
    print("\n[5] Testing NodeHierarchyItem validations...")

    # Invalid: empty label
    try:
        NodeHierarchyItem(
            label="",
            description="Valid description with enough length.",
        )
        raise AssertionError("Failed to reject empty label")
    except ValidationError:
        print("  [✓] Correctly rejected empty node label (min_length=1)")

    # Invalid: description too short (< 5 chars)
    try:
        NodeHierarchyItem(
            label="Valid Label",
            description="Tiny",
        )
        raise AssertionError("Failed to reject description < 5 chars")
    except ValidationError:
        print("  [✓] Correctly rejected short node description (min_length=5)")

    print("\n" + "=" * 65)
    print("[SUCCESS] All AI schema validations and tree traversal tests passed!")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
