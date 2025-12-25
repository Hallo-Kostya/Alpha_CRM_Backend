from uuid import UUID
from sqlalchemy import select
from typing import Sequence
from sqlalchemy.orm import selectinload
from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import CuratorModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class CuratorRepository(BaseRepository[CuratorModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(CuratorModel, session)

    async def get_by_id(self, obj_id: UUID) -> CuratorModel | None:
        result = await self.session.execute(
            select(self.model)
            .options(selectinload(CuratorModel.teams))
            .where(self.model.id == obj_id)
        )
        obj = result.scalar_one_or_none()
        return obj

    async def get_list(
        self, **filter_attrs
    ) -> Sequence[CuratorModel] | list[CuratorModel]:
        query = (
            select(self.model)
            .options(selectinload(CuratorModel.teams))
            .filter_by(**filter_attrs)
        )
        result = await self.session.scalars(query)
        return result.all()


def curator_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = CuratorRepository(session)
    return repository
