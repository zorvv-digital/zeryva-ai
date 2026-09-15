import uuid
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.base import BaseService
from app.db.models import Project
from app.models.schemas import ProjectCreate


class ProjectService(BaseService):
    """
    Service layer handling project workspace lifecycle and database operations.
    """

    @classmethod
    async def create_project(cls, db: AsyncSession, project_in: ProjectCreate) -> Project:
        """
        Creates a new workspace project record and commits it to the database.

        Args:
            db (AsyncSession): Active asynchronous database session.
            project_in (ProjectCreate): Input schema containing project name and optional description.

        Returns:
            Project: The newly created and refreshed database Project model instance.
        """
        project = Project(name=project_in.name, description=project_in.description)
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    @classmethod
    async def list_projects(cls, db: AsyncSession) -> Sequence[Project]:
        """
        Retrieves all workspace projects ordered by creation date descending.

        Args:
            db (AsyncSession): Active asynchronous database session.

        Returns:
            Sequence[Project]: List of all database Project records.
        """
        result = await db.execute(select(Project).order_by(Project.created_at.desc()))
        return result.scalars().all()

    @classmethod
    async def get_project(cls, db: AsyncSession, project_id: uuid.UUID) -> Optional[Project]:
        """
        Fetches a single workspace project record by its primary key UUID.

        Args:
            db (AsyncSession): Active asynchronous database session.
            project_id (uuid.UUID): Primary key UUID of the project.

        Returns:
            Optional[Project]: The matching database Project record, or None if not found.
        """
        result = await db.execute(select(Project).where(Project.id == project_id))
        return result.scalars().first()
