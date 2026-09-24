from fastapi import APIRouter
from app.api.routes import health, analyses

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["Analyses"])