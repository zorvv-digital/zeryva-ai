"""
Unit tests for ToolService CRUD operations, ownership validation, and ToolFactory.
"""

import sys
import uuid
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import HTTPException
from app.services.tool_service import ToolService
from app.services.tools import ToolFactory
from app.models.schemas import ToolCreate, ToolType
from app.db.models import Project, AgentModel, ToolModel


@pytest.mark.asyncio
async def test_tool_service_validate_project_and_agent_success():
    """Verify validate_project_and_agent passes when agent belongs to project."""
    project_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_project = Project(id=project_id, name="Test Project")
    mock_agent = AgentModel(id=agent_id, project_id=project_id, agent_name="Test Agent", system_prompt="", greeting_message="")

    mock_db = AsyncMock()
    # First query for Project, second query for Agent
    proj_result = MagicMock()
    proj_result.scalars().first.return_value = mock_project

    agent_result = MagicMock()
    agent_result.scalars().first.return_value = mock_agent

    mock_db.execute.side_effect = [proj_result, agent_result]

    validated_agent = await ToolService.validate_project_and_agent(mock_db, project_id, agent_id)
    assert validated_agent.id == agent_id


@pytest.mark.asyncio
async def test_tool_service_validate_project_not_found():
    """Verify 404 raised when project does not exist."""
    project_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_db = AsyncMock()
    proj_result = MagicMock()
    proj_result.scalars().first.return_value = None
    mock_db.execute.return_value = proj_result

    with pytest.raises(HTTPException) as exc_info:
        await ToolService.validate_project_and_agent(mock_db, project_id, agent_id)

    assert exc_info.value.status_code == 404
    assert "Project with ID" in exc_info.value.detail


@pytest.mark.asyncio
async def test_tool_service_validate_agent_mismatch():
    """Verify 400 raised when agent belongs to a different project."""
    project_id = uuid.uuid4()
    other_project_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_project = Project(id=project_id, name="Test Project")
    mock_agent = AgentModel(id=agent_id, project_id=other_project_id, agent_name="Test Agent", system_prompt="", greeting_message="")

    mock_db = AsyncMock()
    proj_result = MagicMock()
    proj_result.scalars().first.return_value = mock_project

    agent_result = MagicMock()
    agent_result.scalars().first.return_value = mock_agent

    mock_db.execute.side_effect = [proj_result, agent_result]

    with pytest.raises(HTTPException) as exc_info:
        await ToolService.validate_project_and_agent(mock_db, project_id, agent_id)

    assert exc_info.value.status_code == 400
    assert "does not belong to Project" in exc_info.value.detail


def test_tool_factory_text_context_tool_creation():
    """Verify ToolFactory converts ToolModel to dynamic python function tool."""
    tool_model = ToolModel(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        agent_id=uuid.uuid4(),
        name="Cancellation Policy",
        description="Retrieves cancellation and refund policy text",
        tool_type="text_context",
        config={"content": "Orders can be cancelled within 24 hours for full refund."},
        is_active=True,
    )

    callable_tool = ToolFactory.create_tool(tool_model)

    assert callable(callable_tool)
    assert callable_tool.__name__ == "cancellation_policy"
    assert callable_tool.__doc__ == "Retrieves cancellation and refund policy text"
    assert callable_tool() == "Orders can be cancelled within 24 hours for full refund."
