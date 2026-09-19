import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.schemas import AgentResponse, BuilderInput, BuilderAgentResponse
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    agent = await AgentService.get_agent(db=db, agent_id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/builder/generate", response_model=BuilderAgentResponse)
async def generate_agent_endpoint(
    builder_input: BuilderInput,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await AgentService.generate_and_create_agent(db=db, builder_input=builder_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
