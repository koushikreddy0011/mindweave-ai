"""Integration test script validating Mindmap CRUD and relational cross-tenant authorization."""

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


async def run_mindmap_tests() -> int:
    """Run full integration test for mindmap CRUD, workspace filtering, and relational IDOR protection."""
    print("=" * 60)
    print("MindWeave AI — Mindmap CRUD & Relational Authorization")
    print("=" * 60)

    suffix_a = uuid.uuid4().hex[:6]
    suffix_b = uuid.uuid4().hex[:6]
    user_a_email = f"mindmap_user_a_{suffix_a}@example.com"
    user_b_email = f"mindmap_user_b_{suffix_b}@example.com"
    password = "StrongPassword123!"

    user_a_id = None
    user_b_id = None

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            # 1. Register User A and User B
            resp_a = await client.post(
                "/api/v1/auth/register",
                json={"email": user_a_email, "password": password, "full_name": "User Alpha"},
            )
            assert resp_a.status_code == 201, f"User A registration failed: {resp_a.text}"
            user_a_id = uuid.UUID(resp_a.json()["id"])

            resp_b = await client.post(
                "/api/v1/auth/register",
                json={"email": user_b_email, "password": password, "full_name": "User Beta"},
            )
            assert resp_b.status_code == 201, f"User B registration failed: {resp_b.text}"
            user_b_id = uuid.UUID(resp_b.json()["id"])
            print(f"  [✓] Test 1: Created User A ({user_a_id}) and User B ({user_b_id}).")

            # Authenticate User A
            login_a = await client.post(
                "/api/v1/auth/login",
                data={"username": user_a_email, "password": password},
            )
            assert login_a.status_code == 200
            token_a = login_a.json()["access_token"]
            headers_a = {"Authorization": f"Bearer {token_a}"}

            # Authenticate User B
            login_b = await client.post(
                "/api/v1/auth/login",
                data={"username": user_b_email, "password": password},
            )
            assert login_b.status_code == 200
            token_b = login_b.json()["access_token"]
            headers_b = {"Authorization": f"Bearer {token_b}"}

            # Fetch User A's default workspace
            ws_resp_a = await client.get("/api/v1/workspaces", headers=headers_a)
            assert ws_resp_a.status_code == 200
            user_a_workspace_id = ws_resp_a.json()[0]["id"]

            # 2. User A creates a mindmap
            create_payload = {
                "workspace_id": user_a_workspace_id,
                "title": "Transformers & LLMs",
                "description": "Comprehensive map of modern transformer architectures and attention mechanisms.",
                "input_type": "topic",
                "input_prompt": "Explain Transformer neural networks in detail.",
            }
            create_resp = await client.post(
                "/api/v1/mindmaps",
                json=create_payload,
                headers=headers_a,
            )
            assert create_resp.status_code == 201, f"Create mindmap failed: {create_resp.text}"
            created_map = create_resp.json()
            mindmap_id = created_map["id"]
            assert created_map["title"] == "Transformers & LLMs"
            assert created_map["status"] == "draft"
            assert created_map["workspace_id"] == user_a_workspace_id
            print(f"  [✓] Test 2: User A created mindmap '{created_map['title']}' ({mindmap_id}).")

            # 3. User A lists mindmaps
            list_resp = await client.get("/api/v1/mindmaps", headers=headers_a)
            assert list_resp.status_code == 200
            maps_a = list_resp.json()
            assert any(m["id"] == mindmap_id for m in maps_a)
            print("  [✓] Test 3: User A listed mindmaps, created map found.")

            # 4. User A filters mindmaps by workspace_id
            filter_resp = await client.get(
                f"/api/v1/mindmaps?workspace_id={user_a_workspace_id}",
                headers=headers_a,
            )
            assert filter_resp.status_code == 200
            filtered_maps = filter_resp.json()
            assert all(m["workspace_id"] == user_a_workspace_id for m in filtered_maps)
            print("  [✓] Test 4: Workspace query filtering verified.")

            # 5. User A partially updates mindmap
            patch_payload = {
                "title": "Transformers & LLM Foundations",
                "status": "completed",
            }
            patch_resp = await client.patch(
                f"/api/v1/mindmaps/{mindmap_id}",
                json=patch_payload,
                headers=headers_a,
            )
            assert patch_resp.status_code == 200
            assert patch_resp.json()["title"] == patch_payload["title"]
            assert patch_resp.json()["status"] == "completed"
            print("  [✓] Test 5: User A updated title and status to 'completed' via PATCH.")

            # 6. Cross-Tenant Injection Test: User B attempts to create mindmap inside User A's workspace
            malicious_payload = {
                "workspace_id": user_a_workspace_id,
                "title": "Malicious Injected Map",
            }
            inject_resp = await client.post(
                "/api/v1/mindmaps",
                json=malicious_payload,
                headers=headers_b,
            )
            assert inject_resp.status_code == 404, f"Security issue! User B injected mindmap into User A's workspace: {inject_resp.status_code}"
            print("  [✓] Test 6 (Security): User B denied creating mindmap in User A's workspace (HTTP 404).")

            # 7. IDOR Test: User B attempts to GET User A's mindmap
            idor_get = await client.get(
                f"/api/v1/mindmaps/{mindmap_id}",
                headers=headers_b,
            )
            assert idor_get.status_code == 404, f"IDOR vulnerability! User B accessed User A's mindmap: {idor_get.status_code}"
            print("  [✓] Test 7 (Security): User B denied GET access to User A's mindmap (HTTP 404).")

            # 8. IDOR Test: User B attempts to DELETE User A's mindmap
            idor_del = await client.delete(
                f"/api/v1/mindmaps/{mindmap_id}",
                headers=headers_b,
            )
            assert idor_del.status_code == 404, f"IDOR vulnerability! User B deleted User A's mindmap: {idor_del.status_code}"
            print("  [✓] Test 8 (Security): User B denied DELETE access to User A's mindmap (HTTP 404).")

            # 9. Legitimate Deletion: User A deletes their mindmap
            del_resp = await client.delete(
                f"/api/v1/mindmaps/{mindmap_id}",
                headers=headers_a,
            )
            assert del_resp.status_code == 204, f"Delete failed: {del_resp.status_code}"
            print("  [✓] Test 9: User A successfully deleted mindmap (HTTP 204).")

            # 10. Subsequent GET confirms deletion
            get_again = await client.get(
                f"/api/v1/mindmaps/{mindmap_id}",
                headers=headers_a,
            )
            assert get_again.status_code == 404
            print("  [✓] Test 10: Subsequent GET confirmed mindmap is completely removed (HTTP 404).")

            print("\n" + "=" * 60)
            print("[SUCCESS] All Mindmap CRUD & Relational Authorization tests passed!")
            print("=" * 60)
            return 0

        finally:
            # Clean up test users (cascades to workspaces, mindmaps, nodes, edges)
            async with AsyncSessionLocal() as session:
                for uid in (user_a_id, user_b_id):
                    if uid:
                        await session.execute(delete(User).where(User.id == uid))
                await session.commit()
                print("\n[+] Cleanup: Test accounts and cascaded records deleted from DB.")


if __name__ == "__main__":
    exit_code = asyncio.run(run_mindmap_tests())
    sys.exit(exit_code)
