from typing import Generic, TypeVar
from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from pydantic import BaseModel
from app.infrastructure.database.entity_base import BaseEntity
from uuid import UUID


TModel = TypeVar("TModel", bound=BaseEntity)
P_OUT = TypeVar("P_OUT", bound=BaseModel)
T_IN = TypeVar("T_IN", bound=BaseModel)


class BaseService(Generic[TModel, P_OUT]):
    orm_model: type[TModel]
    pyd_scheme: type[P_OUT]
    eager_loads: list[str] = []

    def __init__(
        self,
        base_repo: BaseRepository[TModel],
    ):
        self._repo = base_repo

    def _to_orm(self, scheme) -> TModel:
        return self.orm_model(**scheme.model_dump(exclude_unset=True))
    
    def _to_schema(self, orm_model: TModel) -> P_OUT:
     return self.pyd_scheme.model_validate(orm_model, from_attributes=True)

    async def _validate_exists(self, obj_id: UUID, error_msg: str = "Object not found") -> TModel:
        obj = await self._repo.get_by_id(obj_id, eager_loads=self.eager_loads)
        if not obj:
            raise ValueError(error_msg)
        return obj

    async def create(self, data: T_IN) -> P_OUT:
        orm_obj = self._to_orm(data)
        created = await self._repo.create(orm_obj)
        if self.eager_loads:
            # Reload with eager loads
            created = await self._repo.get_by_id(created.id, eager_loads=self.eager_loads)
        return self._to_schema(created)

    async def update(self, obj_id: UUID, data: T_IN) -> P_OUT | None:
        obj = await self._repo.get_by_id(obj_id, eager_loads=self.eager_loads)
        if not obj:
            return None
        updated = await self._repo.update(obj, data.model_dump(exclude_unset=True))
        return self._to_schema(updated)

    async def delete(self, obj_id: UUID) -> bool:
        obj = await self._repo.get_by_id(obj_id, eager_loads=self.eager_loads)
        if not obj:
            return False
        await self._repo.delete(obj)
        return True

    async def get_list(self, **filter_attrs) -> list[P_OUT]:
        items = await self._repo.get_list(eager_loads=self.eager_loads, **filter_attrs)
        return [self._to_schema(item) for item in items]

    async def get_by_id(self, obj_id: UUID) -> P_OUT | None:
        obj = await self._repo.get_by_id(obj_id, eager_loads=self.eager_loads)
        if not obj:
            return None
        return self._to_schema(obj)
