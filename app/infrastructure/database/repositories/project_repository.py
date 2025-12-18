from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import ProjectModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class ProjectRepository(BaseRepository[ProjectModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectModel, session)


def project_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = ProjectRepository(session)
    return repository
