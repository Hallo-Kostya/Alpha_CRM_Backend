from typing import Generic, TypeVar
from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from pydantic import BaseModel
from app.infrastructure.database.entity_base import BaseEntity
from uuid import UUID


TModel = TypeVar("TModel", bound=BaseEntity)
P_OUT = TypeVar("P_OUT", bound=BaseModel)


class BaseService(Generic[TModel, P_OUT]):
    orm_model: type[TModel]
    pyd_scheme: type[P_OUT]

    def __init__(
        self,
        base_repo: BaseRepository[TModel],
    ):
        self._repo = base_repo

    def _to_schema(self, orm_model: TModel) -> P_OUT:
        return self.pyd_scheme.model_validate(orm_model, from_attributes=True)

    async def delete(self, obj_id: UUID) -> bool:
        obj = await self._repo.get_by_id(obj_id)
        if not obj:
            return False
        await self._repo.delete(obj)
        return True

    async def get_list(self, **filter_attrs) -> list[P_OUT]:
        items = await self._repo.get_list(**filter_attrs)
        return [self._to_schema(item) for item in items]

    async def get_by_id(self, obj_id: UUID) -> P_OUT | None:
        obj = await self._repo.get_by_id(obj_id)
        if not obj:
            return None
        return self._to_schema(obj)
