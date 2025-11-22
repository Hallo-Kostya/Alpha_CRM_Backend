from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TDomain = TypeVar("TDomain")
TModel = TypeVar("TModel")

class Mapper(ABC, Generic[TDomain, TModel]):
    @abstractmethod
    def to_domain(self, model: TModel) -> TDomain:
        pass

    @abstractmethod
    def to_model(self, entity: TDomain) -> TModel:
        pass