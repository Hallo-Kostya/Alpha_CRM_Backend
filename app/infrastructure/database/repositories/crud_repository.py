from collections.abc import Sequence
from typing import Generic, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface
from app.infrastructure.database.entity_base import BaseEntity  # или Base, как у тебя

TDomain = TypeVar("TDomain", bound=BaseModel)
TModel = TypeVar("TModel", bound=BaseEntity)


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
        data = {c.name: getattr(orm_obj, c.name) for c in orm_obj.__table__.columns}
        return self.domain_model(**data)

    async def get(self, obj_id: UUID) -> TDomain | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        orm_obj = result.scalar_one_or_none()
        if orm_obj is None:
            return None
        data = {c.name: getattr(orm_obj, c.name) for c in orm_obj.__table__.columns}
        return self.domain_model(**data)

    async def update(self, obj: TDomain) -> TDomain:
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj.id) # type: ignore
        )
        orm_obj = result.scalar_one()

        # Обновляем только те поля, которые пришли (из obj)
        update_data = obj.model_dump(exclude_unset=True, exclude={"id"})  # исключаем id
        for key, value in update_data.items():
            setattr(orm_obj, key, value)

        # Коммитим изменения
        await self.session.commit()
        await self.session.refresh(orm_obj)

        # Возвращаем доменную модель
        data = {c.name: getattr(orm_obj, c.name) for c in orm_obj.__table__.columns}
        return self.domain_model(**data)

    async def list(self) -> list[TDomain]:
        result = await self.session.execute(select(self.model))
        orm_objs = result.scalars().all()
        return [
            self.domain_model(**{c.name: getattr(o, c.name) for c in o.__table__.columns})
            for o in orm_objs
        ]
    
    async def delete(self, obj_id: UUID) -> None:
        await self.session.execute(delete(self.model).where(self.model.id == obj_id))
        await self.session.commit()