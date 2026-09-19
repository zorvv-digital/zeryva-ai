import uuid
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator
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
    offerings: list[str] = Field(default_factory=list)
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

    @field_validator("project_id", mode="before")
    @classmethod
    def parse_empty_project_id(cls, value: Any) -> Any:
        if isinstance(value, str) and not value.strip():
            return None
        return value


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


class AgentChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class AgentChatResponse(BaseModel):
    agent_id: uuid.UUID
    project_id: uuid.UUID
    session_id: str
    agent_name: str
    user_message: str
    response: str


# ==========================================
# Tool Schemas
# ==========================================

class ToolType(str, Enum):
    TEXT_CONTEXT = "text_context"
    AGENTIC_RAG = "agentic_rag"
    SQL_QUERY = "sql_query"
    WEB_SEARCH = "web_search"
    GOOGLE_SHEETS = "google_sheets"
    HTTP_REQUEST = "http_request"


class TextContextConfig(BaseModel):
    content: str = Field(..., min_length=1, description="Raw text context or document content for the tool")


class ToolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Unique identifier name for the tool")
    description: str = Field(..., min_length=1, description="Description explaining to the LLM when to invoke this tool")
    tool_type: ToolType = Field(default=ToolType.TEXT_CONTEXT, description="Type of tool configuration")
    config: dict[str, Any] = Field(default_factory=dict, description="Type-specific tool parameters JSON")

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: dict[str, Any], info) -> dict[str, Any]:
        tool_type = info.data.get("tool_type")
        if tool_type == ToolType.TEXT_CONTEXT or tool_type == "text_context":
            if "content" not in v or not str(v.get("content", "")).strip():
                raise ValueError("Config for 'text_context' tool must contain a non-empty 'content' string field")
        return v


class ToolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class ToolResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    agent_id: uuid.UUID
    name: str
    description: str
    tool_type: str
    config: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
