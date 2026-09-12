import json
import uuid
from pathlib import Path
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from agno.agent import Agent
from app.providers.llm import model
from app.db.models import Project, AgentModel
from app.models.schemas import (
    BuilderInput,
    Step1PromptResponse,
    SkillsExtractionResponse,
    BuilderAgentResponse,
    AgentSkill,
)

# Load Step 1 Builder Agent Prompt
prompt_path = Path(__file__).parent / "prompt.md"
system_prompt = prompt_path.read_text(encoding="utf-8")

builder_agent = Agent(
    name="Builder Agent",
    model=model,
    description="Synthesizes business profiling and onboarding data into a WhatsApp AI agent system prompt.",
    instructions=system_prompt,
    output_schema=Step1PromptResponse,
)

# Define Step 2 Knowledge Search Skills Extractor Agent
skills_instructions = """You are a Knowledge & Text Search Skill Extractor for AI Agents.
Your job is to analyze the provided business agent system prompt and business context.

CRITICAL RULE:
You MUST ONLY extract Knowledge Retrieval and Text Search skills (e.g., `faq_knowledge_search`, `document_text_search`, `catalog_price_search`, `policy_lookup`).
Do NOT generate transactional action tools (e.g. appointment booking, order processing, payment handling).

For each knowledge search skill identified:
- `skill_name`: Unique snake_case identifier (e.g., `faq_knowledge_search`)
- `description`: Clear summary of what text/document knowledge this skill retrieves
- `is_required`: boolean flag
"""

skills_agent = Agent(
    name="Skills Extractor Agent",
    model=model,
    description="Extracts knowledge retrieval and text search skills for the agent.",
    instructions=skills_instructions,
    output_schema=SkillsExtractionResponse,
)


async def generate_builder_agent_config(
    builder_input: BuilderInput,
    db: Optional[AsyncSession] = None
) -> BuilderAgentResponse:
    input_json = builder_input.model_dump_json()

    # Step 1: Generate System Prompt & Flag Knowledge Search Need
    step1_result = builder_agent.run(input_json)
    step1_data: Step1PromptResponse = step1_result.content

    skills: list[AgentSkill] = []

    # Step 2: Conditional execution for Knowledge Search Skills extraction
    if step1_data.requires_knowledge_search:
        context_payload = {
            "agent_name": step1_data.agent_name,
            "system_prompt": step1_data.system_prompt,
            "business_profile": builder_input.business_profile.model_dump(),
            "collected_answers": builder_input.collected_answers,
        }
        step2_result = skills_agent.run(json.dumps(context_payload))
        step2_data: SkillsExtractionResponse = step2_result.content
        skills = step2_data.skills

    skills_dict_list = [skill.model_dump() for skill in skills]

    target_project_id: uuid.UUID
    agent_id: uuid.UUID

    if db is not None:
        if builder_input.project_id:
            target_project_id = builder_input.project_id
        else:
            # Look for an existing default project or create one
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
                await db.flush()
                target_project_id = new_project.id

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
        agent_id = agent_record.id
    else:
        target_project_id = builder_input.project_id or uuid.uuid4()
        agent_id = uuid.uuid4()

    return BuilderAgentResponse(
        agent_id=agent_id,
        project_id=target_project_id,
        agent_name=step1_data.agent_name,
        system_prompt=step1_data.system_prompt,
        greeting_message=step1_data.greeting_message,
        skills=skills,
    )
