from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.schemas import BuilderInput, BuilderAgentResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/builder", tags=["Builder"])


@router.post("/generate-agent", response_model=BuilderAgentResponse)
async def generate_agent(
    builder_input: BuilderInput,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await AgentService.generate_and_create_agent(db=db, builder_input=builder_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
