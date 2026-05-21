from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import ProjectApplicationMemberModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class ProjectApplicationMemberRepository(BaseRepository[ProjectApplicationMemberModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectApplicationMemberModel, session)


def project_application_members_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = ProjectApplicationMemberRepository(session)
    return repository
