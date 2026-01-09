from pydantic import ConfigDict, Field, HttpUrl
from typing import Optional, TYPE_CHECKING
from app.domain.entities.base_entity import BaseEntity
from app.domain.entities.custom_types import NameField

class Team(BaseEntity):
    """Доменная модель команды"""
    name: NameField = Field(..., examples=["Название команды"])
    group_link: Optional[str] = Field(None, max_length=500)