"""
Unit tests for ProjectService database CRUD operations.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services import ProjectService
from app.models.schemas import ProjectCreate


@pytest.mark.asyncio
async def test_project_service_create_project():
    """Verify ProjectService.create_project adds record to session and commits."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    proj_in = ProjectCreate(
        name="Dental Assistant Project",
        description="Workspace for dental AI agent",
        image_url="https://example.com/avatar.png",
    )
    created_project = await ProjectService.create_project(mock_db, proj_in)

    assert created_project.name == "Dental Assistant Project"
    assert created_project.description == "Workspace for dental AI agent"
    assert created_project.image_url == "https://example.com/avatar.png"
    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.refresh.called
