from collections.abc import Sequence
from typing import Generic, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface
from app.infrastructure.database.base import Base

TDomain = TypeVar("TDomain", bound=BaseModel)
TModel = TypeVar("TModel", bound=Base)


class CRUDRepository(CRUDRepositoryInterface[TDomain], Generic[TDomain, TModel]):
    def __init__(
        self,
        model: Type[TModel],
        domain_model: Type[TDomain],
        session: AsyncSession,
    ) -> None:
        self.model = model
        self.domain_model = domain_model
        self.session = session

    async def create(self, obj: TDomain) -> TDomain:
        orm_obj = self.model(**obj.model_dump(exclude_unset=True))
        self.session.add(orm_obj)
        await self.session.commit()
        await self.session.refresh(orm_obj)
        return self.domain_model.model_validate(orm_obj)

    async def get(self, obj_id: UUID) -> TDomain | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        model = result.scalar_one_or_none()
        return self.domain_model.model_validate(model) if model else None

    async def update(self, obj: TDomain) -> TDomain:
        orm_obj = self.model(**obj.model_dump(exclude_unset=True))
        self.session.add(orm_obj)
        await self.session.commit()
        await self.session.refresh(orm_obj)
        return self.domain_model.model_validate(orm_obj)

    async def delete(self, obj_id: UUID) -> None:
        await self.session.execute(
            delete(self.model).where(self.model.id == obj_id)
        )
        await self.session.commit()

    async def list(self) -> list[TDomain]:
        result = await self.session.execute(select(self.model))
        models = result.scalars().all()
        return [self.domain_model.model_validate(m) for m in models]