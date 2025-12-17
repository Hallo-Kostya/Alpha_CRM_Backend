from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import TeamModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class TeamRepository(BaseRepository[TeamModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(TeamModel, session)


def team_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = TeamRepository(session)
    return repository
