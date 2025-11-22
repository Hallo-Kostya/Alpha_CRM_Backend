from app.domain.interfaces import CRUDRepositoryInterface
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from collections.abc import Sequence
from typing import Type, TypeVar
from database.base import Base
from uuid import UUID

T = TypeVar("T", bound=Base)

class CRUDRepository(CRUDRepositoryInterface[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def read(self, obj_id: UUID) -> T | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def delete(self, obj_id: UUID) -> None:
        await self.session.execute(
            delete(self.model).where(self.model.id == obj_id)
        )
        await self.session.commit()

    async def list(self) -> Sequence[T]: 
        result = await self.session.execute(select(self.model))
        return result.scalars().all()