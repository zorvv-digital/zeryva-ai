import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str

class GenericResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    model_config = ConfigDict(from_attributes=True)

class BusinessProfileBase(BaseModel):
    business_name: str
    business_type: str
    location: Optional[str] = None
    offerings: list[str]
    working_hours: Optional[str] = None

class DynamicUIField(BaseModel):
    field_id: str
    question_text: str
    ui_type: str
    options: Optional[list[str]] = None
    is_required: bool

class ProfilerSchemaResponse(BaseModel):
    fields: list[DynamicUIField]

class AgentSetup(BaseModel):
    agent_name: Optional[str] = None
    personality: Optional[str] = None
    business_objective: Optional[str] = None
    rules: Optional[list[str]] = None

class BuilderInput(BaseModel):
    project_id: Optional[uuid.UUID] = None
    business_profile: BusinessProfileBase
    collected_answers: Optional[dict[str, Any]] = None
    agent_setup: Optional[AgentSetup] = None

class AgentSkill(BaseModel):
    skill_name: str
    description: str
    is_required: bool

class Step1PromptResponse(BaseModel):
    agent_name: str
    system_prompt: str
    greeting_message: str
    requires_knowledge_search: bool

class SkillsExtractionResponse(BaseModel):
    skills: list[AgentSkill]

class BuilderAgentResponse(BaseModel):
    agent_id: uuid.UUID
    project_id: uuid.UUID
    agent_name: str
    system_prompt: str
    greeting_message: str
    skills: list[AgentSkill] = []

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AgentResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    agent_name: str
    system_prompt: str
    greeting_message: str
    skills: list[Any] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


