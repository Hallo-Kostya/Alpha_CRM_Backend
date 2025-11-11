from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.domain.entities import BaseEntity
from app.domain.enums import MeetingStatus


class Meeting(BaseEntity):
    def __init__(self, team_id: UUID, name: str, resume: str, 
                 date: datetime, status: MeetingStatus, 
                 previous: Optional[Meeting], next: Optional[Meeting], id: Optional[UUID]):
        super().__init__(id)
        self.team_id = team_id
        self.name = name
        self.resume = resume
        self.date = date
        self.status = status
        self.previous = previous
        self.next = next