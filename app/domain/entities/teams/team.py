from pydantic import ConfigDict, Field, HttpUrl
from typing import Optional, TYPE_CHECKING
from app.domain.entities.base_entity import BaseEntity

class Team(BaseEntity):
    """Доменная модель команды"""
    name: str = Field(..., min_length=1, max_length=255)
    group_link: Optional[str] = Field(None, max_length=500)