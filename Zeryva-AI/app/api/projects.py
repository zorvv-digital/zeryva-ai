import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.schemas import ProjectCreate, ProjectResponse, AgentResponse
from app.services.project_service import ProjectService
from app.services.agent_service import AgentService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    return await ProjectService.create_project(db=db, project_in=project_in)


@router.get("", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    return await ProjectService.list_projects(db=db)


@router.get("/{project_id}/agents", response_model=list[AgentResponse])
async def list_project_agents(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    project = await ProjectService.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await AgentService.list_agents_by_project(db=db, project_id=project_id)
