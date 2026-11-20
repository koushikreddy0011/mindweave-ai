"""Health and readiness monitoring endpoints."""

import time
from typing import Any

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine

router = APIRouter(prefix="/health", tags=["Health & Monitoring"])


@router.api_route("", methods=["GET", "HEAD"], summary="Liveness Probe")
@router.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
async def liveness() -> dict[str, str]:
    """Liveness check confirming the application server process is running."""
    return {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@router.api_route("/ready", methods=["GET", "HEAD"], summary="Readiness Probe")
async def readiness() -> Any:
    """Readiness check validating live database pool connectivity and latency."""
    start_time = time.perf_counter()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        dialect_driver = f"{engine.dialect.name}+{engine.dialect.driver}"

        return {
            "status": "ready",
            "database": {
                "status": "connected",
                "latency_ms": latency_ms,
                "dialect": dialect_driver,
            },
            "app": settings.PROJECT_NAME,
            "environment": settings.ENVIRONMENT,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": {
                    "status": "disconnected",
                    "error": str(exc),
                },
            },
        )
