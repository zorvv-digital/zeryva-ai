import uuid
from typing import Optional, Any
from datetime import datetime
from sqlalchemy import DateTime, String, Text, Boolean, ForeignKey, Uuid, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class BaseModelMixin(Base):
    """
    Abstract Base Model Mixin providing UUID primary key, created_at, and updated_at timestamps.
    """
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Project(BaseModelMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    agents: Mapped[list["AgentModel"]] = relationship("AgentModel", back_populates="project", cascade="all, delete-orphan")
    tools: Mapped[list["ToolModel"]] = relationship("ToolModel", back_populates="project", cascade="all, delete-orphan")


class AgentModel(BaseModelMixin):
    __tablename__ = "agents"

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    greeting_message: Mapped[str] = mapped_column(Text, nullable=False)
    skills: Mapped[Any] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    project: Mapped["Project"] = relationship("Project", back_populates="agents")
    tools: Mapped[list["ToolModel"]] = relationship("ToolModel", back_populates="agent", cascade="all, delete-orphan")


class ToolModel(BaseModelMixin):
    """
    Database model for dynamic AI Agent tools with polymorphic configuration payload.
    """
    __tablename__ = "tools"

    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    agent_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tool_type: Mapped[str] = mapped_column(String(50), nullable=False, default="text_context")
    config: Mapped[Any] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    project: Mapped["Project"] = relationship("Project", back_populates="tools")
    agent: Mapped["AgentModel"] = relationship("AgentModel", back_populates="tools")
