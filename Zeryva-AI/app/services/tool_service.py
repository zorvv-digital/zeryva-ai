import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.services.base import BaseService
from app.db.models import Project, AgentModel, ToolModel
from app.models.schemas import ToolCreate, ToolUpdate


class ToolService(BaseService):
    """
    Service layer for custom AI Agent tools lifecycle and project-level authorization validation.
    """

    @classmethod
    async def validate_project_and_agent(
        cls, db: AsyncSession, project_id: uuid.UUID, agent_id: uuid.UUID
    ) -> AgentModel:
        """
        Verifies that:
        1. Target Project exists in the database.
        2. Target Agent exists in the database.
        3. Target Agent belongs to the specified Project.

        Raises:
            HTTPException: 404 if project or agent is not found.
            HTTPException: 400 if agent does not belong to the project.
        """
        # 1. Verify Project existence
        project_result = await db.execute(select(Project).where(Project.id == project_id))
        project = project_result.scalars().first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID '{project_id}' not found."
            )

        # 2. Verify Agent existence
        agent_result = await db.execute(select(AgentModel).where(AgentModel.id == agent_id))
        agent = agent_result.scalars().first()
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID '{agent_id}' not found."
            )

        # 3. Verify Ownership Relationship
        if agent.project_id != project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent with ID '{agent_id}' does not belong to Project '{project_id}'."
            )

        return agent

    @classmethod
    async def create_tool(
        cls,
        db: AsyncSession,
        project_id: uuid.UUID,
        agent_id: uuid.UUID,
        tool_in: ToolCreate,
    ) -> ToolModel:
        """
        Validates ownership and creates a new Tool database record attached to an Agent.
        """
        await cls.validate_project_and_agent(db=db, project_id=project_id, agent_id=agent_id)

        tool_record = ToolModel(
            project_id=project_id,
            agent_id=agent_id,
            name=tool_in.name.strip(),
            description=tool_in.description.strip(),
            tool_type=tool_in.tool_type.value if hasattr(tool_in.tool_type, "value") else str(tool_in.tool_type),
            config=tool_in.config,
            is_active=True,
        )
        db.add(tool_record)
        await db.commit()
        await db.refresh(tool_record)
        return tool_record

    @classmethod
    async def list_agent_tools(
        cls, db: AsyncSession, project_id: uuid.UUID, agent_id: uuid.UUID
    ) -> Sequence[ToolModel]:
        """
        Lists all tools registered for a specific agent after verifying ownership.
        """
        await cls.validate_project_and_agent(db=db, project_id=project_id, agent_id=agent_id)

        result = await db.execute(
            select(ToolModel)
            .where(ToolModel.agent_id == agent_id)
            .order_by(ToolModel.created_at.desc())
        )
        return result.scalars().all()

    @classmethod
    async def get_tool(
        cls, db: AsyncSession, project_id: uuid.UUID, agent_id: uuid.UUID, tool_id: uuid.UUID
    ) -> ToolModel:
        """
        Retrieves a single tool record after verifying project and agent ownership.
        """
        await cls.validate_project_and_agent(db=db, project_id=project_id, agent_id=agent_id)

        result = await db.execute(
            select(ToolModel).where(ToolModel.id == tool_id, ToolModel.agent_id == agent_id)
        )
        tool = result.scalars().first()
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool with ID '{tool_id}' not found for Agent '{agent_id}'."
            )
        return tool

    @classmethod
    async def delete_tool(
        cls, db: AsyncSession, project_id: uuid.UUID, agent_id: uuid.UUID, tool_id: uuid.UUID
    ) -> None:
        """
        Deletes a tool record from the database after verifying ownership.
        """
        tool = await cls.get_tool(db=db, project_id=project_id, agent_id=agent_id, tool_id=tool_id)
        await db.delete(tool)
        await db.commit()

    @classmethod
    async def list_active_tools_for_agent(
        cls, db: AsyncSession, agent_id: uuid.UUID
    ) -> Sequence[ToolModel]:
        """
        Helper query for runtime agent chat execution: fetches all active tools for an agent.
        """
        result = await db.execute(
            select(ToolModel).where(ToolModel.agent_id == agent_id, ToolModel.is_active == True)
        )
        return result.scalars().all()
