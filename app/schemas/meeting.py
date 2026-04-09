"""Meeting schema models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import MeetingStatus
from app.common.fields import NameField


class Meeting(BaseModel):
    """Meeting full model with all fields."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    resume: Optional[str] = None
    date: datetime
    status: MeetingStatus
    team_id: UUID
    previous_meeting_id: Optional[UUID] = None
    next_meeting_id: Optional[UUID] = None


class MeetingCreate(BaseModel):
    """Create meeting."""
    name: NameField = Field(..., examples=["Название встречи"])
    resume: Optional[str] = Field(None, examples=["Описание встречи"])
    date: datetime
    team_id: UUID
    status: MeetingStatus = MeetingStatus.SCHEDULED
    previous_meeting_id: Optional[UUID] = None


class MeetingUpdate(BaseModel):
    """Update meeting."""
    name: Optional[NameField] = Field(None, examples=["Название встречи"])
    resume: Optional[str] = Field(None, examples=["Описание встречи"])
    date: Optional[datetime] = None
    status: Optional[MeetingStatus] = None
    previous_meeting_id: Optional[UUID] = None
    next_meeting_id: Optional[UUID] = None


# Aliases for backward compatibility
MeetingRead = Meeting
MeetingResponse = Meeting
