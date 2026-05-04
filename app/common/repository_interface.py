from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar, Sequence
from uuid import UUID

T = TypeVar("T")


class RepositoryInterface(ABC, Generic[T]):
    @abstractmethod
    async def create(self, obj: T) -> T:
        """
        Сохранить объект в бд
        """
        pass

    @abstractmethod
    async def get_by_id(self, obj_id: UUID) -> T | None:
        """
        Получить объект по ID
        """
        pass

    @abstractmethod
    async def update(self, obj: T, new_data: dict) -> T:
        """
        Обновить объект
        """
        pass

    @abstractmethod
    async def delete(self, obj: T) -> None:
        """
        Удалить объект из бд
        """
        pass

    @abstractmethod
    async def get_list(
        self,
        filters: Optional[dict[str, Any]] = None,
        range_filters: Optional[dict[str, tuple[Any, Any]]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> tuple[int, Sequence[T]]:
        """Получить список объектов с фильтрами и пагинацией."""
        pass
