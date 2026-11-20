"""Integration test script validating authentication endpoints and workspace provisioning."""

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
from sqlalchemy import delete, select

from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.user import User
from app.models.workspace import Workspace


async def run_auth_tests() -> int:
    """Run full integration test for registration, login, profile, and workspace provisioning."""
    print("=" * 60)
    print("MindWeave AI — Authentication & Provisioning Verification")
    print("=" * 60)

    unique_suffix = uuid.uuid4().hex[:8]
    test_email = f"authtest_{unique_suffix}@example.com"
    test_password = "SecurePassword123!"
    test_name = "Auth Test User"
    created_user_id = None

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            # 1. Test registration
            reg_payload = {
                "email": test_email,
                "password": test_password,
                "full_name": test_name,
            }
            reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
            assert reg_resp.status_code == 201, f"Expected 201, got {reg_resp.status_code}: {reg_resp.text}"
            reg_data = reg_resp.json()
            assert reg_data["email"] == test_email.lower()
            assert reg_data["full_name"] == test_name
            assert reg_data["is_active"] is True
            assert "hashed_password" not in reg_data
            created_user_id = uuid.UUID(reg_data["id"])
            print(f"  [✓] Test 1: User registered successfully (ID: {created_user_id}).")

            # Verify default workspace was automatically provisioned
            async with AsyncSessionLocal() as session:
                ws_result = await session.execute(
                    select(Workspace).where(Workspace.user_id == created_user_id)
                )
                workspace = ws_result.scalar_one_or_none()
                assert workspace is not None, "Default workspace was not provisioned"
                assert workspace.name == "Personal", f"Expected 'Personal', got {workspace.name}"
                print("  [✓] Test 1b: Default 'Personal' workspace provisioned automatically.")

            # 2. Test duplicate registration rejection
            dup_resp = await client.post("/api/v1/auth/register", json=reg_payload)
            assert dup_resp.status_code == 409, f"Expected 409, got {dup_resp.status_code}"
            print("  [✓] Test 2: Duplicate email registration correctly rejected with HTTP 409.")

            # 3. Test login with correct credentials
            login_data = {
                "username": test_email,
                "password": test_password,
            }
            login_resp = await client.post("/api/v1/auth/login", data=login_data)
            assert login_resp.status_code == 200, f"Expected 200, got {login_resp.status_code}: {login_resp.text}"
            token_data = login_resp.json()
            assert "access_token" in token_data
            assert token_data["token_type"] == "bearer"
            access_token = token_data["access_token"]
            print("  [✓] Test 3: Login successful, issued valid JWT access token.")

            # 4. Test login with wrong password
            bad_login = await client.post(
                "/api/v1/auth/login",
                data={"username": test_email, "password": "WrongPassword123!"},
            )
            assert bad_login.status_code == 401, f"Expected 401, got {bad_login.status_code}"
            print("  [✓] Test 4: Invalid password login correctly rejected with HTTP 401.")

            # 5. Test protected /me endpoint with valid Bearer token
            auth_headers = {"Authorization": f"Bearer {access_token}"}
            me_resp = await client.get("/api/v1/auth/me", headers=auth_headers)
            assert me_resp.status_code == 200, f"Expected 200, got {me_resp.status_code}: {me_resp.text}"
            me_data = me_resp.json()
            assert me_data["id"] == str(created_user_id)
            assert me_data["email"] == test_email.lower()
            print("  [✓] Test 5: Protected GET /me returned authenticated user profile.")

            # 6. Test protected /me endpoint without token
            unauth_resp = await client.get("/api/v1/auth/me")
            assert unauth_resp.status_code == 401, f"Expected 401, got {unauth_resp.status_code}"
            print("  [✓] Test 6: Request to /me without token correctly rejected with HTTP 401.")

            print("\n" + "=" * 60)
            print("[SUCCESS] All authentication & workspace provisioning tests passed!")
            print("=" * 60)
            return 0

        finally:
            # Clean up the test user from database (cascades to workspace)
            if created_user_id:
                async with AsyncSessionLocal() as session:
                    await session.execute(delete(User).where(User.id == created_user_id))
                    await session.commit()
                    print(f"\n[+] Cleanup: Test user {created_user_id} and related data deleted.")


if __name__ == "__main__":
    exit_code = asyncio.run(run_auth_tests())
    sys.exit(exit_code)
