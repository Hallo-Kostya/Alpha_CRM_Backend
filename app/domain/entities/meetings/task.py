from pydantic import Field
from app.domain.entities.base_entity import BaseEntity
from app.domain.entities.custom_types import MediumText


class Task(BaseEntity):
    """Доменная модель задачи"""
    
    description: MediumText = Field(..., examples=["Описание задачи"])
    is_completed: bool = False