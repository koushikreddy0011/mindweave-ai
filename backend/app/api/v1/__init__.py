"""API v1 router registry."""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.generations import router as generations_router
from app.api.v1.health import router as health_router
from app.api.v1.mindmaps import router as mindmaps_router
from app.api.v1.nodes import router as nodes_router
from app.api.v1.workspaces import router as workspaces_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(workspaces_router)
api_router.include_router(mindmaps_router)
api_router.include_router(nodes_router)
api_router.include_router(generations_router)
api_router.include_router(documents_router)

__all__ = ["api_router"]
