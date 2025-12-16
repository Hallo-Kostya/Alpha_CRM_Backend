from pydantic import Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import MeetingStatus


class Meeting(BaseEntity):
    """Доменная модель встречи"""
    
    team_id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    resume: Optional[str] = Field(None, max_length=5000)
    date: datetime
    status: MeetingStatus = MeetingStatus.SCHEDULED
    previous: Optional['Meeting'] = None
    next: Optional['Meeting'] = None