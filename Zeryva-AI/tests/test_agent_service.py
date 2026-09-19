"""
Unit tests for AgentService execution & chat workflow.
"""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services.agent_service import AgentService
from app.db.models import AgentModel


@pytest.mark.asyncio
async def test_execute_agent_chat_success():
    """Verify execute_agent_chat loads agent from DB and executes message."""
    mock_db = AsyncMock()
    fake_project_id = uuid.uuid4()
    fake_agent_id = uuid.uuid4()

    fake_agent_record = AgentModel(
        id=fake_agent_id,
        project_id=fake_project_id,
        agent_name="Zera",
        system_prompt="You are Zera",
        greeting_message="Hello",
        is_active=True,
    )

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = fake_agent_record
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    fake_llm_response = MagicMock()
    fake_llm_response.content = "We are open 9am-7pm"

    with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
        mock_to_thread.return_value = fake_llm_response

        res = await AgentService.execute_agent_chat(
            db=mock_db,
            project_id=fake_project_id,
            user_message="What are your hours?",
            session_id="session-1",
        )

        assert res.agent_name == "Zera"
        assert res.user_message == "What are your hours?"
        assert res.response == "We are open 9am-7pm"
        assert res.session_id == "session-1"


@pytest.mark.asyncio
async def test_execute_agent_chat_not_found():
    """Verify execute_agent_chat raises 404 when no active agent exists."""
    mock_db = AsyncMock()
    fake_project_id = uuid.uuid4()

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc_info:
        await AgentService.execute_agent_chat(
            db=mock_db,
            project_id=fake_project_id,
            user_message="Hi",
        )

    assert exc_info.value.status_code == 404
