from pydantic import Field
from app.domain.entities.base_entity import BaseEntity


class Task(BaseEntity):
    """Доменная модель задачи"""
    
    description: str = Field(..., min_length=1, max_length=2000, alias='desription')
    is_completed: bool = False