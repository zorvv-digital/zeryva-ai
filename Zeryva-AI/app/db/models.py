import uuid
from typing import Optional, Any
from datetime import datetime
from sqlalchemy import DateTime, String, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.session import Base

class BaseModelMixin(Base):
    """
    Abstract Base Model Mixin providing UUID primary key, created_at, and updated_at timestamps.
    """
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Project(BaseModelMixin):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    agents: Mapped[list["AgentModel"]] = relationship("AgentModel", back_populates="project", cascade="all, delete-orphan")

class AgentModel(BaseModelMixin):
    __tablename__ = "agents"

    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    greeting_message: Mapped[str] = mapped_column(Text, nullable=False)
    skills: Mapped[Any] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    project: Mapped["Project"] = relationship("Project", back_populates="agents")

