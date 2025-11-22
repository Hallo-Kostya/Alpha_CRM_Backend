from abc import ABC, abstractmethod
from typing import TypeVar, Generic

Input = TypeVar("Input")
Output = TypeVar("Output")

class IUseCase(ABC, Generic[Input, Output]):
    @abstractmethod
    async def execute(self, data: Input) -> Output:
        pass
