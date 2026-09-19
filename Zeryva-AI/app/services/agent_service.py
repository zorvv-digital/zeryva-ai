import uuid
import asyncio
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from agno.agent import Agent
from agno.db.sqlite import SqliteDb

from app.services.base import BaseService
from app.db.models import Project, AgentModel
from app.models.schemas import BuilderInput, BuilderAgentResponse, AgentChatResponse
from app.services.agents.builder_agent.agent import synthesize_agent_config
from app.services.tool_service import ToolService
from app.services.tools import ToolFactory
from app.providers.llm import model

agno_db = SqliteDb(db_file="agno_sessions.db", session_table="agno_sessions")


class AgentService(BaseService):
    """
    Service layer for AI Agent management and creation workflow.

    Encapsulates database persistence, agent querying, default workspace resolution,
    LLM agent configuration synthesis, dynamic tool mounting, and non-blocking runtime agent chat execution.
    """

    @classmethod
    async def get_agent(cls, db: AsyncSession, agent_id: uuid.UUID) -> Optional[AgentModel]:
        """
        Retrieves a single AI Agent record from the database by its unique UUID.

        Args:
            db (AsyncSession): Active asynchronous database session.
            agent_id (uuid.UUID): Primary key UUID of the requested agent.

        Returns:
            Optional[AgentModel]: The matching database Agent record, or None if not found.
        """
        result = await db.execute(select(AgentModel).where(AgentModel.id == agent_id))
        return result.scalars().first()

    @classmethod
    async def list_agents_by_project(
        cls, db: AsyncSession, project_id: uuid.UUID
    ) -> Sequence[AgentModel]:
        """
        Retrieves all AI Agents associated with a specific workspace project ID.

        Args:
            db (AsyncSession): Active asynchronous database session.
            project_id (uuid.UUID): Foreign key UUID of the target project.

        Returns:
            Sequence[AgentModel]: List of matching Agent records, ordered by creation date descending.
        """
        result = await db.execute(
            select(AgentModel)
            .where(AgentModel.project_id == project_id)
            .order_by(AgentModel.created_at.desc())
        )
        return result.scalars().all()

    @classmethod
    async def generate_and_create_agent(
        cls, db: AsyncSession, builder_input: BuilderInput
    ) -> BuilderAgentResponse:
        """
        Full orchestration workflow for creating a production AI Agent:
        1. Invokes the Builder & Skills Extractor LLM agents to synthesize prompts and extract skills.
        2. Resolves target workspace project (uses input project_id or automatically creates a default project).
        3. Persists the generated Agent configuration into the database.
        4. Constructs and returns the final BuilderAgentResponse schema.

        Args:
            db (AsyncSession): Active asynchronous database session.
            builder_input (BuilderInput): Input payload containing business profile, collected answers, and agent setup.

        Returns:
            BuilderAgentResponse: The complete synthesized agent response containing generated agent_id, system_prompt, and skills.
        """
        # Step 1: Execute Pure AI LLM Generation Pipeline (Step 1 Builder Agent & Step 2 Skills Extractor)
        step1_data, skills = synthesize_agent_config(builder_input)
        skills_dict_list = [skill.model_dump() for skill in skills]

        # Step 2: Workspace Project Resolution
        # Determine whether to attach agent to an existing specified project or resolve a default workspace
        target_project_id: uuid.UUID
        if builder_input.project_id:
            target_project_id = builder_input.project_id
        else:
            # Query for an existing workspace project or create a "Default Workspace" if none exists
            result = await db.execute(select(Project).order_by(Project.created_at.asc()).limit(1))
            existing_project = result.scalars().first()
            if existing_project:
                target_project_id = existing_project.id
            else:
                new_project = Project(
                    name="Default Workspace",
                    description="Default project created automatically for built agents."
                )
                db.add(new_project)
                await db.flush()  # Obtain new_project.id before agent creation
                target_project_id = new_project.id

        # Step 3: Database Persistence
        # Construct and save the new Agent database record
        agent_record = AgentModel(
            project_id=target_project_id,
            agent_name=step1_data.agent_name,
            system_prompt=step1_data.system_prompt,
            greeting_message=step1_data.greeting_message,
            skills=skills_dict_list,
            is_active=True,
        )
        db.add(agent_record)
        await db.commit()
        await db.refresh(agent_record)

        # Step 4: Construct and Return API Schema Response
        return BuilderAgentResponse(
            agent_id=agent_record.id,
            project_id=target_project_id,
            agent_name=step1_data.agent_name,
            system_prompt=step1_data.system_prompt,
            greeting_message=step1_data.greeting_message,
            skills=skills,
        )

    @classmethod
    async def execute_agent_chat(
        cls,
        db: AsyncSession,
        project_id: uuid.UUID,
        user_message: str,
        session_id: Optional[str] = None,
    ) -> AgentChatResponse:
        """
        Executes a user chat message against an active saved Agent for a workspace project:
        1. Queries the latest active AgentModel for the given project_id.
        2. Fetches active custom tools registered for the agent and converts them to runtime Agno tools.
        3. Instantiates a runtime Agno Agent configured with native SqliteDb session storage and dynamic tools.
        4. Executes the message non-blockingly via asyncio threadpool.
        5. Returns the synthesized AgentChatResponse.
        """
        result = await db.execute(
            select(AgentModel)
            .where(AgentModel.project_id == project_id, AgentModel.is_active == True)
            .order_by(AgentModel.created_at.desc())
            .limit(1)
        )
        agent_record = result.scalars().first()
        if not agent_record:
            raise HTTPException(status_code=404, detail="No active agent found for this project.")

        agent_id = agent_record.id
        agent_name = agent_record.agent_name
        system_prompt = agent_record.system_prompt
        target_session_id = session_id.strip() if (session_id and session_id.strip()) else str(project_id)

        # Fetch active tools for agent and build dynamic runtime tool callables
        tool_records = await ToolService.list_active_tools_for_agent(db=db, agent_id=agent_id)
        runtime_tools = ToolFactory.create_tools(tool_records) if tool_records else None

        runtime_agent = Agent(
            name=agent_name,
            instructions=system_prompt,
            tools=runtime_tools,
            model=model,
        )

        try:
            llm_response = await asyncio.to_thread(
                runtime_agent.run,
                user_message,
                session_id=target_session_id,
            )
            response_text = str(llm_response.content) if llm_response else ""
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Agent execution failed: {exc}")

        return AgentChatResponse(
            agent_id=agent_id,
            project_id=project_id,
            session_id=target_session_id,
            agent_name=agent_name,
            user_message=user_message,
            response=response_text,
        )
