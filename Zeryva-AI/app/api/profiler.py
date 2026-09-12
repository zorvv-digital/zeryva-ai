from fastapi import APIRouter, HTTPException
from app.models.schemas import BusinessProfileBase, ProfilerSchemaResponse
from app.services.agents.profiling_agent.agent import generate_profiling_schema

router = APIRouter(prefix="/profiler", tags=["Profiler"])

@router.post("/generate-questions", response_model=ProfilerSchemaResponse)
async def generate_questions(profile: BusinessProfileBase):
    try:
        profile_json = profile.model_dump_json()
        schema_response = generate_profiling_schema(profile_json)
        return schema_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
