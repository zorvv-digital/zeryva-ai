from fastapi import APIRouter
from app.api.profiler import router as profiler_router
from app.api.builder import router as builder_router
from app.api.projects import router as projects_router
from app.api.agents import router as agents_router

api_router = APIRouter()

api_router.include_router(profiler_router)
api_router.include_router(builder_router)
api_router.include_router(projects_router)
api_router.include_router(agents_router)


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}
