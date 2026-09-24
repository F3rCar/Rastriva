from app.api.routes import analyses, health
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["Analyses"])