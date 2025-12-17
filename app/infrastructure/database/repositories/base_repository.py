from typing import Generic, Type, TypeVar, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces.repositories.repository_interface import (
    RepositoryInterface,
)
from app.infrastructure.database.entity_base import BaseEntity

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

    async def get_by_id(self, obj_id: UUID) -> T | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        obj = result.scalar_one_or_none()
        return obj

    async def update(self, obj: T, new_data: dict) -> T:
        for key, value in new_data.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def get_list(self, **filter_attrs) -> Sequence[T] | list[T]:
        query = select(self.model).filter_by(**filter_attrs)
        result = await self.session.scalars(query)
        return result.all()

    async def delete(self, obj: T) -> None:
        await self.session.delete(obj)
        await self.session.commit()
