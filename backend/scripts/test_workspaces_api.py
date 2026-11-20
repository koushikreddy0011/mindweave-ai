"""Integration test script validating Workspace CRUD and cross-tenant IDOR protection."""

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


async def run_workspace_tests() -> int:
    """Run full integration test for workspace CRUD and IDOR boundary enforcement."""
    print("=" * 60)
    print("MindWeave AI — Workspace CRUD & Multi-Tenant Authorization")
    print("=" * 60)

    suffix_a = uuid.uuid4().hex[:6]
    suffix_b = uuid.uuid4().hex[:6]
    user_a_email = f"user_a_{suffix_a}@example.com"
    user_b_email = f"user_b_{suffix_b}@example.com"
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

            # 2. Verify User A has their default "Personal" workspace
            list_resp = await client.get("/api/v1/workspaces", headers=headers_a)
            assert list_resp.status_code == 200
            workspaces_a = list_resp.json()
            assert len(workspaces_a) >= 1
            assert workspaces_a[0]["name"] == "Personal"
            print("  [✓] Test 2: User A lists workspaces, default 'Personal' present.")

            # 3. User A creates a new workspace
            create_payload = {
                "name": "Machine Learning Research",
                "description": "Exploration of deep learning architectures and knowledge graphs.",
            }
            create_resp = await client.post(
                "/api/v1/workspaces",
                json=create_payload,
                headers=headers_a,
            )
            assert create_resp.status_code == 201, f"Create workspace failed: {create_resp.text}"
            created_ws = create_resp.json()
            ws_id = created_ws["id"]
            assert created_ws["name"] == "Machine Learning Research"
            assert created_ws["user_id"] == str(user_a_id)
            print(f"  [✓] Test 3: User A created custom workspace '{created_ws['name']}' ({ws_id}).")

            # 4. User A partially updates the workspace
            patch_payload = {
                "description": "Updated description with new focus on agentic reasoning.",
            }
            patch_resp = await client.patch(
                f"/api/v1/workspaces/{ws_id}",
                json=patch_payload,
                headers=headers_a,
            )
            assert patch_resp.status_code == 200
            assert patch_resp.json()["description"] == patch_payload["description"]
            assert patch_resp.json()["name"] == "Machine Learning Research"
            print("  [✓] Test 4: User A updated workspace description via PATCH.")

            # 5. IDOR Test: User B attempts to GET User A's workspace
            idor_get = await client.get(
                f"/api/v1/workspaces/{ws_id}",
                headers=headers_b,
            )
            assert idor_get.status_code == 404, f"IDOR vulnerability! User B got User A's workspace: {idor_get.status_code}"
            print("  [✓] Test 5 (Security): User B denied GET access to User A's workspace (HTTP 404).")

            # 6. IDOR Test: User B attempts to DELETE User A's workspace
            idor_del = await client.delete(
                f"/api/v1/workspaces/{ws_id}",
                headers=headers_b,
            )
            assert idor_del.status_code == 404, f"IDOR vulnerability! User B deleted User A's workspace: {idor_del.status_code}"
            print("  [✓] Test 6 (Security): User B denied DELETE access to User A's workspace (HTTP 404).")

            # 7. Legitimate Deletion: User A deletes their workspace
            del_resp = await client.delete(
                f"/api/v1/workspaces/{ws_id}",
                headers=headers_a,
            )
            assert del_resp.status_code == 204, f"Delete failed: {del_resp.status_code}"
            print("  [✓] Test 7: User A successfully deleted workspace (HTTP 204).")

            # 8. Verify workspace is gone
            get_again = await client.get(
                f"/api/v1/workspaces/{ws_id}",
                headers=headers_a,
            )
            assert get_again.status_code == 404
            print("  [✓] Test 8: Subsequent GET confirmed workspace is completely removed (HTTP 404).")

            print("\n" + "=" * 60)
            print("[SUCCESS] All Workspace CRUD & IDOR multi-tenant security tests passed!")
            print("=" * 60)
            return 0

        finally:
            # Clean up test users
            async with AsyncSessionLocal() as session:
                for uid in (user_a_id, user_b_id):
                    if uid:
                        await session.execute(delete(User).where(User.id == uid))
                await session.commit()
                print("\n[+] Cleanup: Test users and associated workspaces removed from DB.")


if __name__ == "__main__":
    exit_code = asyncio.run(run_workspace_tests())
    sys.exit(exit_code)
