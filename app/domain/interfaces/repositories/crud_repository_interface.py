from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")

class CRUDRepositoryInterface(ABC, Generic[T]):
    @abstractmethod
    async def create(self, obj: T) -> T:
        """
        Сохранить объект в хранилище
        """
        pass

    @abstractmethod
    async def get(self, obj_id: UUID) -> T | None:
        """
        Получить объект по ID
        """
        pass

    @abstractmethod
    async def update(self, obj: T) -> T:
        """
        Обновить объект
        """
        pass

    @abstractmethod
    async def delete(self, obj_id: UUID) -> None:
        """
        Удалить объект по ID
        """
        pass

    @abstractmethod
    async def list(self) -> list[T]:
        """
        Вернуть все объекты
        """
        pass
