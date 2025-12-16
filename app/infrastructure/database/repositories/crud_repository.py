from collections.abc import Sequence
from typing import Generic, Type, TypeVar
from uuid import UUID
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface
from app.infrastructure.database.entity_base import BaseEntity

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

        # Явно загружаем связи, чтобы Pydantic не вызывал lazy-loading
        await self.session.refresh(orm_obj)
        await self.session.refresh(orm_obj, attribute_names=[
            attr.key for attr in orm_obj.__mapper__.relationships
        ])

        return self.domain_model.model_validate(
            orm_obj, from_attributes=True
        )

    async def get(self, obj_id: UUID) -> TDomain | None:
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
            .options(selectinload("*"))  # загружает все связи
        )
        model = result.scalar_one_or_none()
        return self.domain_model.model_validate(model, from_attributes=True) if model else None

    async def list(self) -> list[TDomain]:
        result = await self.session.execute(
            select(self.model).options(selectinload("*"))
        )
        models = result.scalars().all()
        return [self.domain_model.model_validate(m, from_attributes=True) for m in models]