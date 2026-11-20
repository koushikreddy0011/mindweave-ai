"""Integration test script validating NodeExplanationService, caching latency, and API endpoints."""

import asyncio
import sys
import time
import uuid
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import httpx
from httpx import ASGITransport
from sqlalchemy import delete, select

from app.ai.services import NodeExplanationService
from app.core.database import AsyncSessionLocal, engine
from app.main import app
from app.models.base import Base
from app.models.explanation import NodeExplanation
from app.models.mindmap import Mindmap
from app.models.node import Node
from app.models.user import User
from app.models.workspace import Workspace


async def run_explanation_tests() -> int:
    """Run full integration test for node explanations, cache latency, and API endpoints."""
    print("=" * 70)
    print("MindWeave AI — Node Explanation Generation & Caching Verification")
    print("=" * 70)

    # Ensure tables are present in DB
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()
    workspace_id = uuid.uuid4()
    mindmap_id = uuid.uuid4()
    node_id = uuid.uuid4()

    user_a_email = f"expl_user_a_{uuid.uuid4().hex[:6]}@example.com"
    user_b_email = f"expl_user_b_{uuid.uuid4().hex[:6]}@example.com"
    password = "StrongPassword123!"

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        try:
            # 1. Register User A and User B
            resp_a = await client.post(
                "/api/v1/auth/register",
                json={"email": user_a_email, "password": password, "full_name": "Explainer Alpha"},
            )
            assert resp_a.status_code == 201
            user_a_id = uuid.UUID(resp_a.json()["id"])

            resp_b = await client.post(
                "/api/v1/auth/register",
                json={"email": user_b_email, "password": password, "full_name": "Explainer Beta"},
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

            # 2. Seed a workspace, mindmap, and concept node for User A
            async with AsyncSessionLocal() as session:
                workspace = Workspace(
                    id=workspace_id,
                    user_id=user_a_id,
                    name="AI Learning Workspace",
                )
                mindmap = Mindmap(
                    id=mindmap_id,
                    workspace_id=workspace_id,
                    title="Machine Learning Foundations",
                    input_type="topic",
                    status="draft",
                )
                node = Node(
                    id=node_id,
                    mindmap_id=mindmap_id,
                    parent_id=None,
                    label="Supervised Learning",
                    description="Training mathematical models using labeled input-output example pairs.",
                    node_type="branch",
                    depth=1,
                    position_x=320.0,
                    position_y=60.0,
                    generation_status="completed",
                )
                session.add_all([workspace, mindmap, node])
                await session.commit()
            print("  [✓] Test setup: Created User A workspace, mindmap, and 'Supervised Learning' node")

            # 3. Test Service: Live generation via Gemini 3.6 Flash
            print("\n[1] Testing Live Explanation Generation with Gemini 3.6 Flash...")
            service = NodeExplanationService()
            async with AsyncSessionLocal() as session:
                gen_start = time.perf_counter()
                explanation = await service.get_or_generate_explanation(session, node_id, level="beginner")
                gen_duration = (time.perf_counter() - gen_start) * 1000

                # Validate populated fields
                assert explanation.node_id == node_id
                assert explanation.level == "beginner"
                assert len(explanation.overview) >= 10
                assert len(explanation.detailed_explanation) >= 20
                assert len(explanation.how_it_works) >= 1
                assert len(explanation.key_concepts) >= 1
                assert len(explanation.examples) >= 1
                assert len(explanation.applications) >= 1
                assert len(explanation.related_concepts) >= 1

                print(f"  [✓] Live generation succeeded in {gen_duration:.1f}ms")
                print(f"      - Overview: {explanation.overview[:90]}...")
                print(f"      - How it works steps: {len(explanation.how_it_works)}")
                print(f"      - Key concepts: {', '.join(explanation.key_concepts[:3])}")
                print(f"      - Real-world examples: {len(explanation.examples)}")

            # 4. Test Service: Cache-first hit latency (< 50ms)
            print("\n[2] Testing Cache Performance on repeated request...")
            async with AsyncSessionLocal() as session:
                cache_start = time.perf_counter()
                cached = await service.get_or_generate_explanation(session, node_id, level="beginner")
                cache_latency_ms = (time.perf_counter() - cache_start) * 1000

                assert cached.id == explanation.id, "Expected same cached record"
                assert cache_latency_ms < 50.0, f"Expected cache hit < 50ms, got {cache_latency_ms:.2f}ms"
                print(f"  [✓] Cache hit verified: returned in {cache_latency_ms:.2f}ms (< 50ms threshold)")

            # 5. Test REST API: POST /{node_id}/explain
            print("\n[3] Testing REST API POST /api/v1/nodes/{id}/explain...")
            api_post_resp = await client.post(
                f"/api/v1/nodes/{node_id}/explain?level=beginner",
                headers=headers_a,
            )
            assert api_post_resp.status_code == 200
            post_data = api_post_resp.json()
            assert post_data["id"] == str(explanation.id)
            assert post_data["level"] == "beginner"
            assert "detailed_explanation" in post_data
            print("  [✓] POST /api/v1/nodes/{id}/explain returned 200 OK with full explanation payload")

            # 6. Test REST API: GET /{node_id}/explanation
            print("\n[4] Testing REST API GET /api/v1/nodes/{id}/explanation...")
            api_get_resp = await client.get(
                f"/api/v1/nodes/{node_id}/explanation?level=beginner",
                headers=headers_a,
            )
            assert api_get_resp.status_code == 200
            get_data = api_get_resp.json()
            assert get_data["id"] == str(explanation.id)
            print("  [✓] GET /api/v1/nodes/{id}/explanation returned 200 OK for cached explanation")

            # Uncached level returns 404
            missing_resp = await client.get(
                f"/api/v1/nodes/{node_id}/explanation?level=advanced",
                headers=headers_a,
            )
            assert missing_resp.status_code == 404
            print("  [✓] GET for un-generated level 'advanced' correctly returned 404 Not Found")

            # 7. Test Multi-Tenant IDOR Protection
            print("\n[5] Testing Cross-Tenant IDOR Security Isolation...")
            idor_post = await client.post(
                f"/api/v1/nodes/{node_id}/explain?level=beginner",
                headers=headers_b,
            )
            assert idor_post.status_code == 404, f"Expected 404 for User B, got {idor_post.status_code}"

            idor_get = await client.get(
                f"/api/v1/nodes/{node_id}/explanation?level=beginner",
                headers=headers_b,
            )
            assert idor_get.status_code == 404, f"Expected 404 for User B, got {idor_get.status_code}"
            print("  [✓] User B rejected with 404 Not Found when accessing User A's node explanations")

            print("\n" + "=" * 70)
            print("[SUCCESS] All NodeExplanation service, caching, and API tests passed!")
            print("=" * 70)
            return 0

        finally:
            async with AsyncSessionLocal() as session:
                for uid in (user_a_id, user_b_id):
                    if uid:
                        await session.execute(delete(User).where(User.id == uid))
                await session.commit()
                print("[+] Cleanup: Successfully removed test user records and cascaded data from DB.")


if __name__ == "__main__":
    exit_code = asyncio.run(run_explanation_tests())
    sys.exit(exit_code)
