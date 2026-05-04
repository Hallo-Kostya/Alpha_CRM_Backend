from typing import Any, Generic, Optional, Type, TypeVar, Sequence
from uuid import UUID
from sqlalchemy import func, select
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

    async def get_by_id(
        self, obj_id: UUID, eager_loads: list[str] | None = None
    ) -> T | None:
        query = select(self.model).where(self.model.id == obj_id)
        if eager_loads:
            for load_path in eager_loads:
                parts = load_path.split(".")

                loader = selectinload(getattr(self.model, parts[0]))
                current_model = getattr(self.model, parts[0]).property.entity.class_

                if len(parts) >= 2:
                    for part in parts[1:]:
                        loader = loader.selectinload(getattr(current_model, part))
                        current_model = getattr(
                            current_model, part
                        ).property.entity.class_

            query = query.options(loader)
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

    async def get_list(
        self,
        filters: Optional[dict[str, Any]] = None,
        range_filters: Optional[dict[str, tuple[Any, Any]]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> tuple[int, Sequence[T]]:
        query = select(self.model)

        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field, None)
                if column is not None and value is not None:
                    query = query.where(column == value)

        if range_filters:
            for field, (from_val, to_val) in range_filters.items():
                column = getattr(self.model, field, None)
                if column is not None:
                    if from_val is not None:
                        query = query.where(column >= from_val)
                    if to_val is not None:
                        query = query.where(column <= to_val)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)

        if order_by:
            desc = order_by.startswith("-")
            column = getattr(self.model, order_by.lstrip("-"), None)
            if column is not None:
                query = query.order_by(column.desc() if desc else column.asc())
        else:
            query = query.order_by(self.model.created_at.asc())

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return total, result.scalars().all()
