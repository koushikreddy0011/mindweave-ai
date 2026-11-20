"""Integration test script validating Graph hierarchy, canvas positioning, and Node endpoints."""

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


async def run_graph_tests() -> int:
    """Run full integration test for graph endpoints, node creation, positioning, and IDOR."""
    print("=" * 60)
    print("MindWeave AI — Graph Hierarchy & Node Management Verification")
    print("=" * 60)

    suffix_a = uuid.uuid4().hex[:6]
    suffix_b = uuid.uuid4().hex[:6]
    user_a_email = f"graph_user_a_{suffix_a}@example.com"
    user_b_email = f"graph_user_b_{suffix_b}@example.com"
    password = "StrongPassword123!"

    user_a_id = None
    user_b_id = None

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            # 1. Register User A and User B
            resp_a = await client.post(
                "/api/v1/auth/register",
                json={"email": user_a_email, "password": password, "full_name": "Graph Alpha"},
            )
            assert resp_a.status_code == 201
            user_a_id = uuid.UUID(resp_a.json()["id"])

            resp_b = await client.post(
                "/api/v1/auth/register",
                json={"email": user_b_email, "password": password, "full_name": "Graph Beta"},
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
            print(f"  [✓] Test 1: Created and authenticated User A ({user_a_id}) and User B ({user_b_id}).")

            # Fetch User A's workspace and create a mindmap
            ws_resp = await client.get("/api/v1/workspaces", headers=headers_a)
            ws_id = ws_resp.json()[0]["id"]

            create_map_resp = await client.post(
                "/api/v1/mindmaps",
                json={"workspace_id": ws_id, "title": "Deep Learning Fundamentals"},
                headers=headers_a,
            )
            assert create_map_resp.status_code == 201
            mindmap_id = create_map_resp.json()["id"]

            # 2. Add Root Node
            root_payload = {
                "label": "Deep Learning",
                "description": "Root concept covering neural networks.",
                "node_type": "root",
                "position_x": 0.0,
                "position_y": 0.0,
            }
            root_resp = await client.post(
                f"/api/v1/mindmaps/{mindmap_id}/nodes",
                json=root_payload,
                headers=headers_a,
            )
            assert root_resp.status_code == 201, f"Add root node failed: {root_resp.text}"
            root_node = root_resp.json()
            root_node_id = root_node["id"]
            assert root_node["depth"] == 0
            assert root_node["parent_id"] is None

            # Verify mindmap.root_node_id was updated
            map_check = await client.get(f"/api/v1/mindmaps/{mindmap_id}", headers=headers_a)
            assert map_check.json()["root_node_id"] == root_node_id
            print(f"  [✓] Test 2: Added root node '{root_node['label']}' ({root_node_id}), mindmap root updated.")

            # 3. Add Child Node pointing to Root Node
            child_payload = {
                "parent_id": root_node_id,
                "label": "Convolutional Neural Networks",
                "description": "Grid-structured spatial processing for images.",
                "node_type": "branch",
                "position_x": 150.0,
                "position_y": 100.0,
            }
            child_resp = await client.post(
                f"/api/v1/mindmaps/{mindmap_id}/nodes",
                json=child_payload,
                headers=headers_a,
            )
            assert child_resp.status_code == 201, f"Add child node failed: {child_resp.text}"
            child_node = child_resp.json()
            child_node_id = child_node["id"]
            assert child_node["depth"] == 1
            assert child_node["parent_id"] == root_node_id
            print(f"  [✓] Test 3: Added child node '{child_node['label']}' (depth=1), edge auto-created.")

            # 4. Fetch complete graph payload
            graph_resp = await client.get(f"/api/v1/mindmaps/{mindmap_id}/graph", headers=headers_a)
            assert graph_resp.status_code == 200
            graph_data = graph_resp.json()
            assert len(graph_data["nodes"]) == 2
            assert len(graph_data["edges"]) == 1
            assert graph_data["edges"][0]["source_node_id"] == root_node_id
            assert graph_data["edges"][0]["target_node_id"] == child_node_id
            print("  [✓] Test 4: GET /graph returned full payload (2 nodes, 1 edge) for React Flow canvas.")

            # 5. Batch update node coordinates on canvas
            pos_payload = {
                "positions": [
                    {"node_id": root_node_id, "position_x": 50.0, "position_y": 50.0},
                    {"node_id": child_node_id, "position_x": 250.0, "position_y": 180.0},
                ]
            }
            pos_resp = await client.patch(
                f"/api/v1/mindmaps/{mindmap_id}/positions",
                json=pos_payload,
                headers=headers_a,
            )
            assert pos_resp.status_code == 200
            assert pos_resp.json()["updated"] == 2

            # Verify positions applied
            graph_after_pos = (await client.get(f"/api/v1/mindmaps/{mindmap_id}/graph", headers=headers_a)).json()
            node_map = {n["id"]: n for n in graph_after_pos["nodes"]}
            assert node_map[root_node_id]["position_x"] == 50.0
            assert node_map[child_node_id]["position_x"] == 250.0
            print("  [✓] Test 5: PATCH /positions batch updated canvas coordinates successfully.")

            # 6. Update single node details
            patch_node_resp = await client.patch(
                f"/api/v1/nodes/{child_node_id}",
                json={"label": "CNNs & Vision Transformers"},
                headers=headers_a,
            )
            assert patch_node_resp.status_code == 200
            assert patch_node_resp.json()["label"] == "CNNs & Vision Transformers"
            print("  [✓] Test 6: PATCH /nodes/{id} updated node label.")

            # 7. IDOR checks: User B cannot access User A's graph or nodes
            idor_graph = await client.get(f"/api/v1/mindmaps/{mindmap_id}/graph", headers=headers_b)
            assert idor_graph.status_code == 404
            idor_patch = await client.patch(
                f"/api/v1/nodes/{child_node_id}",
                json={"label": "Hacked"},
                headers=headers_b,
            )
            assert idor_patch.status_code == 404
            idor_del = await client.delete(f"/api/v1/nodes/{child_node_id}", headers=headers_b)
            assert idor_del.status_code == 404
            print("  [✓] Test 7 (Security): User B denied access to User A's graph, nodes, and mutations (HTTP 404).")

            # 8. Delete child node
            del_resp = await client.delete(f"/api/v1/nodes/{child_node_id}", headers=headers_a)
            assert del_resp.status_code == 204

            # Verify graph now has 1 node and 0 edges
            graph_after_del = (await client.get(f"/api/v1/mindmaps/{mindmap_id}/graph", headers=headers_a)).json()
            assert len(graph_after_del["nodes"]) == 1
            assert len(graph_after_del["edges"]) == 0
            print("  [✓] Test 8: DELETE /nodes/{id} removed child node and cascaded deletion to connected edge.")

            print("\n" + "=" * 60)
            print("[SUCCESS] All Graph Hierarchy & Node API tests passed!")
            print("=" * 60)
            return 0

        finally:
            async with AsyncSessionLocal() as session:
                for uid in (user_a_id, user_b_id):
                    if uid:
                        await session.execute(delete(User).where(User.id == uid))
                await session.commit()
                print("\n[+] Cleanup: Test accounts and cascaded graph data deleted from DB.")


if __name__ == "__main__":
    exit_code = asyncio.run(run_graph_tests())
    sys.exit(exit_code)
