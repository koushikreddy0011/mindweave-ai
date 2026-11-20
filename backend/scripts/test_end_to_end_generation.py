"""End-to-end integration test validating master topic generation, graph layout, and explanations."""

import asyncio
import sys
import uuid
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import httpx
from httpx import ASGITransport
from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.user import User


async def run_e2e_generation_tests() -> int:
    """Run master end-to-end integration test for AI mindmap generation."""
    print("=" * 70)
    print("MindWeave AI — End-to-End Mindmap Generation Verification")
    print("=" * 70)

    user_a_id = None
    user_b_id = None
    suffix_a = uuid.uuid4().hex[:6]
    suffix_b = uuid.uuid4().hex[:6]
    user_a_email = f"e2e_user_a_{suffix_a}@example.com"
    user_b_email = f"e2e_user_b_{suffix_b}@example.com"
    password = "StrongPassword123!"

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            # 1. Register User A and User B
            print("\n[1] Registering test accounts...")
            resp_a = await client.post(
                "/api/v1/auth/register",
                json={"email": user_a_email, "password": password, "full_name": "E2E User A"},
            )
            assert resp_a.status_code == 201
            user_a_id = uuid.UUID(resp_a.json()["id"])

            resp_b = await client.post(
                "/api/v1/auth/register",
                json={"email": user_b_email, "password": password, "full_name": "E2E User B"},
            )
            assert resp_b.status_code == 201
            user_b_id = uuid.UUID(resp_b.json()["id"])

            # Login both users
            token_a = (
                await client.post(
                    "/api/v1/auth/login",
                    data={"username": user_a_email, "password": password},
                )
            ).json()["access_token"]
            headers_a = {"Authorization": f"Bearer {token_a}"}

            token_b = (
                await client.post(
                    "/api/v1/auth/login",
                    data={"username": user_b_email, "password": password},
                )
            ).json()["access_token"]
            headers_b = {"Authorization": f"Bearer {token_b}"}

            # Fetch User A's default workspace
            ws_resp = await client.get("/api/v1/workspaces", headers=headers_a)
            assert ws_resp.status_code == 200
            workspaces = ws_resp.json()
            assert len(workspaces) > 0
            workspace_a_id = workspaces[0]["id"]
            print(f"  [✓] User A registered with workspace {workspace_a_id}")

            # 2. Master Topic-to-Mindmap Generation
            print("\n[2] Triggering POST /api/v1/generations/topic for 'Artificial Intelligence'...")
            gen_payload = {
                "topic": "Artificial Intelligence",
                "workspace_id": workspace_a_id,
                "depth": 3,
                "audience": "beginner",
                "language": "English",
            }

            gen_resp = await client.post(
                "/api/v1/generations/topic",
                json=gen_payload,
                headers=headers_a,
                timeout=60.0,
            )
            assert gen_resp.status_code == 201, f"Expected 201, got {gen_resp.status_code}: {gen_resp.text}"
            graph_data = gen_resp.json()

            mindmap = graph_data["mindmap"]
            nodes = graph_data["nodes"]
            edges = graph_data["edges"]

            # Assertions on generated graph structure
            assert mindmap["status"] == "completed"
            assert mindmap["title"] == "Artificial Intelligence"
            assert mindmap["root_node_id"] is not None
            assert len(mindmap["description"]) > 10

            assert len(nodes) >= 6, f"Expected at least 6 nodes, got {len(nodes)}"
            assert len(edges) == len(nodes) - 1, (
                f"Invariant |E| = |V| - 1 violated: {len(edges)} edges vs {len(nodes)} nodes"
            )

            # Assertions on 2D coordinates
            root_node = next(n for n in nodes if n["id"] == mindmap["root_node_id"])
            assert root_node["position_x"] == 0.0
            for node in nodes:
                assert "position_x" in node and "position_y" in node
                assert node["depth"] >= 0

            print(f"  [✓] Master generation succeeded:")
            print(f"      - Mindmap ID: {mindmap['id']}")
            print(f"      - Status: {mindmap['status']}")
            print(f"      - Total Nodes: {len(nodes)}")
            print(f"      - Total Edges: {len(edges)} (|E| = |V| - 1 verified)")
            print(f"      - Summary: {mindmap['description'][:80]}...")

            # 3. Verify Graph Persistence via GET /api/v1/mindmaps/{id}/graph
            print("\n[3] Testing persistence retrieval via GET /api/v1/mindmaps/{id}/graph...")
            get_graph_resp = await client.get(
                f"/api/v1/mindmaps/{mindmap['id']}/graph",
                headers=headers_a,
            )
            assert get_graph_resp.status_code == 200
            retrieved_graph = get_graph_resp.json()
            assert len(retrieved_graph["nodes"]) == len(nodes)
            assert len(retrieved_graph["edges"]) == len(edges)
            assert retrieved_graph["mindmap"]["id"] == mindmap["id"]
            print(f"  [✓] Successfully retrieved full persisted graph from PostgreSQL")

            # 4. Progressive Node Explanation Generation
            print("\n[4] Testing progressive explanation for a generated child node...")
            # Pick a non-root child node
            child_node = next(n for n in nodes if n["depth"] == 1)
            child_node_id = child_node["id"]
            print(f"      - Selected Node: '{child_node['label']}' ({child_node_id})")

            expl_resp = await client.post(
                f"/api/v1/nodes/{child_node_id}/explain?level=beginner",
                headers=headers_a,
                timeout=30.0,
            )
            assert expl_resp.status_code == 200, f"Expected 200, got {expl_resp.status_code}: {expl_resp.text}"
            explanation = expl_resp.json()
            assert explanation["node_id"] == child_node_id
            assert len(explanation["overview"]) > 10
            assert len(explanation["how_it_works"]) >= 1
            print(f"  [✓] Contextual explanation generated successfully:")
            print(f"      - Overview: {explanation['overview'][:80]}...")

            # 5. Cross-Tenant IDOR Security Check
            print("\n[5] Testing Cross-Tenant Security Isolation (User B cannot access User A)...")
            idor_gen_resp = await client.post(
                "/api/v1/generations/topic",
                json={
                    "topic": "Malicious Probe",
                    "workspace_id": workspace_a_id,  # User A's workspace
                    "depth": 2,
                },
                headers=headers_b,  # User B attempting access
            )
            assert idor_gen_resp.status_code == 404, (
                f"Expected 404 for unauthorized workspace, got {idor_gen_resp.status_code}"
            )
            print("  [✓] User B blocked from generating inside User A's workspace (HTTP 404)")

            idor_graph_resp = await client.get(
                f"/api/v1/mindmaps/{mindmap['id']}/graph",
                headers=headers_b,
            )
            assert idor_graph_resp.status_code == 404
            print("  [✓] User B blocked from reading User A's generated mindmap graph (HTTP 404)")

            print("\n" + "=" * 70)
            print("[SUCCESS] All End-to-End Mindmap Generation tests passed!")
            print("=" * 70)
            return 0

        finally:
            print("\n[+] Cleaning up test users and relational cascade data...")
            async with AsyncSessionLocal() as session:
                for uid in (user_a_id, user_b_id):
                    if uid:
                        await session.execute(delete(User).where(User.id == uid))
                await session.commit()
                print("  [✓] Cleanup complete.")


if __name__ == "__main__":
    exit_code = asyncio.run(run_e2e_generation_tests())
    sys.exit(exit_code)
