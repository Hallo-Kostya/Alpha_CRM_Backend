# app/schemas/artifact.py
from __future__ import annotations

from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.common.enums import ArtifactType


class ArtifactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["Дизайн-макет"])
    description: Optional[str] = Field(None, max_length=2000, examples=["Описание артефакта"])
    type: ArtifactType = Field(..., examples=["FILE"])
    url: Optional[str] = Field(None, examples=["https://s3.example.com/bucket/file.pdf"])


class ArtifactCreate(ArtifactBase):
    """Создание артефакта (ссылка или с последующей загрузкой файла)"""
    project_id: Optional[UUID] = Field(None, description="ID проекта для привязки")
    meeting_id: Optional[UUID] = Field(None, description="ID встречи для привязки")
    
    model_config = ConfigDict(extra="forbid")


class ArtifactFileUpload(BaseModel):
    """Загрузка файла — используется как FormData вместе с файлом"""
    name: Optional[str] = Field(None, max_length=255, description="Если не указано — имя файла")
    description: Optional[str] = Field(None, max_length=2000)
    project_id: Optional[UUID] = None
    meeting_id: Optional[UUID] = None


class ArtifactUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    
    model_config = ConfigDict(extra="forbid")


class ArtifactResponse(ArtifactBase):
    """Полный ответ с артефактом"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class ArtifactWithContext(ArtifactResponse):
    """Артефакт с информацией о привязке"""
    project_id: Optional[UUID] = None
    meeting_id: Optional[UUID] = None


class ArtifactListResponse(BaseModel):
    total: int
    items: List[ArtifactResponse]