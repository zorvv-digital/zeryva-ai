import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.schemas import (
    ProjectCreate,
    ProjectResponse,
    AgentResponse,
    AgentChatRequest,
    AgentChatResponse,
    ToolCreate,
    ToolResponse,
)
from app.services.project_service import ProjectService
from app.services.agent_service import AgentService
from app.services.tool_service import ToolService

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


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    project = await ProjectService.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/agents", response_model=list[AgentResponse])
async def list_project_agents(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    project = await ProjectService.get_project(db=db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await AgentService.list_agents_by_project(db=db, project_id=project_id)


@router.post("/{project_id}/chat", response_model=AgentChatResponse)
async def chat_with_project_agent(
    project_id: uuid.UUID,
    chat_input: AgentChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes a chat message against the active agent saved for the project.
    Agno native SqliteDb handles multi-turn conversation history automatically.
    """
    return await AgentService.execute_agent_chat(
        db=db,
        project_id=project_id,
        user_message=chat_input.message,
        session_id=chat_input.session_id,
    )


# ==========================================
# Agent Tools Endpoints (Nested under Project & Agent)
# ==========================================

@router.post("/{project_id}/agents/{agent_id}/tools", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_tool(
    project_id: uuid.UUID,
    agent_id: uuid.UUID,
    tool_in: ToolCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new custom tool (e.g. text_context FAQ or policy) attached to a specific agent within a project.
    Validates that project and agent exist and that agent belongs to project.
    """
    return await ToolService.create_tool(
        db=db,
        project_id=project_id,
        agent_id=agent_id,
        tool_in=tool_in,
    )


@router.get("/{project_id}/agents/{agent_id}/tools", response_model=list[ToolResponse])
async def list_agent_tools(
    project_id: uuid.UUID,
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Lists all tools registered for a specific agent after verifying project ownership.
    """
    return await ToolService.list_agent_tools(
        db=db,
        project_id=project_id,
        agent_id=agent_id,
    )


@router.get("/{project_id}/agents/{agent_id}/tools/{tool_id}", response_model=ToolResponse)
async def get_agent_tool(
    project_id: uuid.UUID,
    agent_id: uuid.UUID,
    tool_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves details of a specific tool record after verifying project and agent ownership.
    """
    return await ToolService.get_tool(
        db=db,
        project_id=project_id,
        agent_id=agent_id,
        tool_id=tool_id,
    )


@router.delete("/{project_id}/agents/{agent_id}/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_tool(
    project_id: uuid.UUID,
    agent_id: uuid.UUID,
    tool_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Deletes a specific tool record after verifying project and agent ownership.
    """
    await ToolService.delete_tool(
        db=db,
        project_id=project_id,
        agent_id=agent_id,
        tool_id=tool_id,
    )
