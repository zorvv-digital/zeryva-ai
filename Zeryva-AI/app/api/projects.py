import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import Project, AgentModel
from app.models.schemas import ProjectCreate, ProjectResponse, AgentResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(name=project_in.name, description=project_in.description)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("", response_model=list[ProjectResponse])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Project).order_by(Project.created_at.desc()))
    return result.scalars().all()


@router.get("/{project_id}/agents", response_model=list[AgentResponse])
async def list_project_agents(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    proj_result = await db.execute(select(Project).where(Project.id == project_id))
    if not proj_result.scalars().first():
        raise HTTPException(status_code=404, detail="Project not found")

    result = await db.execute(
        select(AgentModel)
        .where(AgentModel.project_id == project_id)
        .order_by(AgentModel.created_at.desc())
    )
    return result.scalars().all()
