from fastapi import APIRouter, HTTPException
from app.models.schemas import BusinessProfileBase, ProfilerSchemaResponse
from app.services.profiler_service import ProfilerService

router = APIRouter(prefix="/profiler", tags=["Profiler"])


@router.post("/generate-questions", response_model=ProfilerSchemaResponse)
async def generate_questions(profile: BusinessProfileBase):
    try:
        return ProfilerService.generate_questions(profile=profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
