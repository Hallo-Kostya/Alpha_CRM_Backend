from uuid import UUID
from sqlalchemy import select
from typing import Sequence
from sqlalchemy.orm import selectinload
from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import CuratorModel
from app.infrastructure.database.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class CuratorRepository(BaseRepository[CuratorModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(CuratorModel, session)


def curator_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = CuratorRepository(session)
    return repository
