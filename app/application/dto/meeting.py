from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.entities.custom_types import NameField
from app.domain.enums.meeting_status import MeetingStatus


class MeetingCreate(BaseModel):
    """DTO для создания встречи"""
    name: NameField = Field(..., examples=["Название встречи"])
    resume: Optional[str] = Field(..., examples=["Описание встречи"])
    date: datetime
    team_id: UUID
    status: MeetingStatus = MeetingStatus.SCHEDULED
    previous_meeting_id: Optional[UUID] = None


class MeetingUpdate(BaseModel):
    """DTO для обновления встречи"""
    name: Optional[NameField] = Field(None, examples=["Название встречи"])
    resume: Optional[str] = Field(None, examples=["Описание встречи"])
    date: Optional[datetime] = None
    status: Optional[MeetingStatus] = None
    previous_meeting_id: Optional[UUID] = None
    next_meeting_id: Optional[UUID] = None


class MeetingResponse(BaseModel):
    """DTO для ответа с информацией о встрече"""
    id: UUID
    name: str
    resume: Optional[str] = None
    date: datetime
    status: MeetingStatus
    team_id: UUID
    previous_meeting_id: Optional[UUID] = None
    next_meeting_id: Optional[UUID] = None
    model_config = ConfigDict(from_attributes=True)