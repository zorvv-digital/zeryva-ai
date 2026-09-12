from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.schemas import BuilderInput, BuilderAgentResponse
from app.services.agents.builder_agent.agent import generate_builder_agent_config

router = APIRouter(prefix="/builder", tags=["Builder"])


@router.post("/generate-agent", response_model=BuilderAgentResponse)
async def generate_agent(builder_input: BuilderInput, db: AsyncSession = Depends(get_db)):
    try:
        response = await generate_builder_agent_config(builder_input, db=db)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
