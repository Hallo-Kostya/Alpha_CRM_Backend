from typing import Generic, Type, TypeVar, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.common.repository_interface import (
    RepositoryInterface,
)
from app.infrastructure.database.models.entity_base import BaseEntity

T = TypeVar("T", bound=BaseEntity)


class BaseRepository(RepositoryInterface[T], Generic[T]):
    def __init__(
        self,
        model: Type[T],
        session: AsyncSession,
    ):
        self.model = model
        self.session = session

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, obj_id: UUID, eager_loads: list[str] = None) -> T | None:
        query = select(self.model).where(self.model.id == obj_id)
        if eager_loads:
            for load in eager_loads:
                query = query.options(selectinload(getattr(self.model, load)))
        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()
        return obj

    async def update(self, obj: T, new_data: dict) -> T:
        for key, value in new_data.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        await self.session.delete(obj)
        await self.session.commit()
