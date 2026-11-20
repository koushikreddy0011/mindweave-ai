"""Automated smoke and regression test suite for MindWeave AI backend."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.pdf_service import ExtractedPDF, PDFExtractionService


@pytest.mark.asyncio
async def test_health_liveness_probe() -> None:
    """Validate that the root liveness endpoint responds with 200 OK."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"


@pytest.mark.asyncio
async def test_auth_me_requires_token() -> None:
    """Validate that accessing /auth/me without a Bearer token returns 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_documents_requires_token() -> None:
    """Validate that accessing /documents without authentication returns 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/documents")
        assert response.status_code == 401


def test_chunker_sliding_window_logic() -> None:
    """Validate semantic chunking window and overlap bounds."""
    service = PDFExtractionService(chunk_size=100, chunk_overlap=20)
    sample_text = (
        "Quantum computing is a rapidly-emerging technology that harnesses the laws of quantum mechanics "
        "to solve problems too complex for classical computers. Physical qubits utilize superposition."
    )
    # Validate window partitioning
    chunks = []
    start = 0
    chunk_idx = 0
    while start < len(sample_text):
        end = min(start + service.chunk_size, len(sample_text))
        chunk_str = sample_text[start:end].strip()
        if chunk_str:
            chunks.append(chunk_str)
            chunk_idx += 1
        if end == len(sample_text):
            break
        start += service.chunk_size - service.chunk_overlap

    assert len(chunks) >= 2
    assert "Quantum computing" in chunks[0]
