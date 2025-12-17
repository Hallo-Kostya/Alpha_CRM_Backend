from pydantic import ConfigDict, Field, HttpUrl
from typing import Optional, TYPE_CHECKING
from app.domain.entities.base_entity import BaseEntity

if TYPE_CHECKING:
    from app.domain.entities.persons.curator import Curator
    from app.domain.entities.projects.project import Project


class Team(BaseEntity):
    """Доменная модель команды"""
    name: str = Field(..., min_length=1, max_length=255)
    curator: Optional['Curator'] = None
    group_link: Optional[str] = Field(None, max_length=500)
    projects: list['Project'] = Field(default_factory=list, exclude=True)