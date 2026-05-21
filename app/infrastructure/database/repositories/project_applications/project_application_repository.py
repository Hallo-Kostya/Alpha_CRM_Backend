from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import ProjectApplicationModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class ProjectApplicationRepository(BaseRepository[ProjectApplicationModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectApplicationModel, session)


def project_applications_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = ProjectApplicationRepository(session)
    return repository
