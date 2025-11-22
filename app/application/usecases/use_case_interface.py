from abc import ABC, abstractmethod

class IUseCase(ABC):
    @abstractmethod
    async def execute(self, data):
        pass
