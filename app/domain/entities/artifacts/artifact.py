from pydantic import Field, HttpUrl
from typing import Optional
from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import ArtifactType


class Artifact(BaseEntity):
    """Доменная модель артефакта (файл, видео, ссылка)"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000, alias='desription')
    type: ArtifactType
    url: str = Field(..., min_length=1, max_length=2000)