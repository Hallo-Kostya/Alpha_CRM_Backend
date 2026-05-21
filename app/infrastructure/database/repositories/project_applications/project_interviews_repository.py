from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import ProjectInterviewModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class ProjectInterviewRepository(BaseRepository[ProjectInterviewModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectInterviewModel, session)


def project_interview_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = ProjectInterviewRepository(session)
    return repository
