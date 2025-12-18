from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID, uuid4


class BaseEntity(BaseModel):
    """Базовая сущность с автогенерацией UUID"""
    
    model_config = ConfigDict(
        from_attributes=True,  # Позволяет создавать из ORM моделей
        validate_assignment=True,  # Валидация при изменении полей
        arbitrary_types_allowed=True  # Для работы с custom типами
    )
    
    id: Optional[UUID] = Field(default_factory=uuid4)