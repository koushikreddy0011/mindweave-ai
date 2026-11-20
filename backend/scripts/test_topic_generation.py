"""Validation script for testing live topic-to-mindmap hierarchy generation using Gemini 3.6 Flash."""

import asyncio
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ai.services import MindmapGenerationService
from app.core.config import settings
from app.schemas.ai import NodeHierarchyItem


def render_ascii_tree(
    node: NodeHierarchyItem,
    prefix: str = "",
    is_last: bool = True,
    is_root: bool = True,
) -> None:
    """Recursively render a NodeHierarchyItem tree in visual ASCII format."""
    connector = "└── " if is_last else "├── "
    badge = f"[{node.node_type.capitalize()}]"

    if is_root:
        print(f"└── {badge} {node.label}: {node.description}")
        new_prefix = "    "
    else:
        print(f"{prefix}{connector}{badge} {node.label}: {node.description}")
        new_prefix = prefix + ("    " if is_last else "│   ")

    for idx, child in enumerate(node.children):
        child_is_last = (idx == len(node.children) - 1)
        render_ascii_tree(
            child,
            prefix=new_prefix,
            is_last=child_is_last,
            is_root=False,
        )


async def run_topic_generation_test() -> int:
    """Execute live topic hierarchy generation with Gemini."""
    print("=" * 70)
    print("MindWeave AI — Live Topic-to-Mindmap Generation Verification")
    print("=" * 70)

    if not settings.GEMINI_API_KEY:
        print("\n[ERROR] GEMINI_API_KEY is not configured in backend/.env.")
        return 1

    topic = "Machine Learning"
    depth = 3
    audience = "beginner"

    print(f"\n[+] Target Topic: '{topic}'")
    print(f"[+] Configured Model: {settings.GEMINI_MODEL}")
    print(f"[+] Hierarchy Depth: {depth} levels")
    print(f"[+] Target Audience: {audience}")
    print("\n[+] Calling Gemini API with structured TopicHierarchyOutput schema...")

    service = MindmapGenerationService()

    try:
        output = await service.generate_topic_hierarchy(
            topic=topic,
            depth=depth,
            audience=audience,
        )

        print("\n[✓] Received structured output from Gemini:")
        print(f"    - Title: {output.topic}")
        print(f"    - Audience: {output.target_audience}")
        print(f"    - Summary: {output.summary}\n")

        print("-" * 70)
        print("VISUAL HIERARCHY TREE (ASCII):")
        print("-" * 70)
        render_ascii_tree(output.root)
        print("-" * 70)

        total_nodes = output.get_total_nodes()
        max_depth = output.get_max_depth()

        print(f"\n[✓] Total Nodes Generated: {total_nodes}")
        print(f"[✓] Maximum Depth Reached: {max_depth} (where root is 0)")

        # Validations & Assertions
        assert output.get_total_nodes() > 1, f"Expected more than 1 node, got {total_nodes}"
        assert topic.lower() in output.topic.lower(), f"Expected '{topic}' in title, got '{output.topic}'"
        assert len(output.root.children) > 0, "Root node must have child branches"

        print("\n" + "=" * 70)
        print("[SUCCESS] Topic-to-mindmap generation verified successfully with Gemini!")
        print("=" * 70)
        return 0

    except Exception as exc:
        print(f"\n[ERROR] Generation failed: {exc}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_topic_generation_test())
    sys.exit(exit_code)
