from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, field_validator

from app.domain.enums.meeting_status import MeetingStatus


class MeetingCreate(BaseModel):
    """DTO для создания встречи"""
    name: str
    resume: Optional[str] = None
    date: datetime
    team_id: UUID
    status: MeetingStatus = MeetingStatus.SCHEDULED
    previous_meeting_id: Optional[UUID] = None


class MeetingUpdate(BaseModel):
    """DTO для обновления встречи"""
    name: Optional[str] = None
    resume: Optional[str] = None
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
    
    class Config:
        from_attributes = True