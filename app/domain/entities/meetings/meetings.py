from pydantic import Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import MeetingStatus
from app.domain.entities.custom_types import NameField, LongText


class Meeting(BaseEntity):
    """Доменная модель встречи"""
    
    team_id: UUID
    name: NameField = Field(..., examples=["Название встречи"])
    resume: LongText = Field(None, examples=["Описание встречи"])
    date: datetime
    status: MeetingStatus = MeetingStatus.SCHEDULED
    previous: Optional['Meeting'] = None
    next: Optional['Meeting'] = None