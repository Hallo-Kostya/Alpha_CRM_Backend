from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")

class CRUDRepositoryInterface(ABC, Generic[T]):
    @abstractmethod
    def create(self, obj: T) -> T:
        """
        Сохранить объект в хранилище
        """
        pass

    @abstractmethod
    def read(self, obj_id: UUID) -> T | None:
        """
        Получить объект по ID
        """
        pass

    @abstractmethod
    def update(self, obj: T) -> T:
        """
        Обновить объект
        """
        pass

    @abstractmethod
    def delete(self, obj_id: UUID) -> None:
        """
        Удалить объект по ID
        """
        pass

    @abstractmethod
    def list(self) -> list[T]:
        """
        Вернуть все объекты
        """
        pass
