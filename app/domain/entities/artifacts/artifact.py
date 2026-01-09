from pydantic import Field, HttpUrl
from typing import Optional
from app.domain.entities.base_entity import BaseEntity
from app.domain.entities.custom_types import MediumText, NameField
from app.domain.enums import ArtifactType


class Artifact(BaseEntity):
    """Доменная модель артефакта (файл, видео, ссылка)"""
    
    name: NameField = Field(..., examples=["Название артефакта"])
    description: MediumText = Field(None, examples=["Описание артефакта"])
    type: ArtifactType
    url: str = Field(..., min_length=1, max_length=2000)