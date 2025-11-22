from app.domain.interfaces import CRUDRepositoryInterface
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from collections.abc import Sequence
from typing import Generic, Type, TypeVar
from app.infrastructure.database.mappers.mapper import Mapper
from database.base import Base
from uuid import UUID

TDomain = TypeVar("TDomain")
TModel = TypeVar("TModel", bound=Base)

class CRUDRepository(CRUDRepositoryInterface[TDomain], Generic[TDomain, TModel]):
    def __init__(self, model: Type[TModel], session: AsyncSession, mapper: Mapper[TDomain, TModel]):
        self.model = model
        self.mapper = mapper
        self.session = session

    async def create(self, obj: TDomain) -> TDomain:
        orm_obj = self.mapper.to_model(obj)
        self.session.add(orm_obj)
        await self.session.commit()
        await self.session.refresh(orm_obj)
        return self.mapper.to_domain(orm_obj)
    
    async def get(self, obj_id: UUID) -> TDomain | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        model = result.scalar_one_or_none()
        return self.mapper.to_domain(model) if model else None
    
    async def update(self, obj: TDomain) -> TDomain:
        orm_obj = self.mapper.to_model(obj)
        self.session.add(orm_obj)
        await self.session.commit()
        await self.session.refresh(orm_obj)
        return self.mapper.to_domain(orm_obj)
    
    async def delete(self, obj_id: UUID) -> None:
        await self.session.execute(
            delete(self.model).where(self.model.id == obj_id)
        )
        await self.session.commit()

    async def list(self) -> Sequence[TDomain]:
        result = await self.session.execute(select(self.model))
        models = result.scalars().all()
        return [self.mapper.to_domain(m) for m in models]