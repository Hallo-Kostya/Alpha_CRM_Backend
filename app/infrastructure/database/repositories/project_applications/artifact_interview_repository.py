from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import ArtifactInterviewModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class ArtifactInterviewRepository(BaseRepository[ArtifactInterviewModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ArtifactInterviewModel, session)


def artifact_interview_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = ArtifactInterviewRepository(session)
    return repository
