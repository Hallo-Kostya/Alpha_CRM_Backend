from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence
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
    async def get_list(self, **filter_attrs) -> Sequence[T] | list[T]:
        """
        Вернуть все объекты
        """
        pass
