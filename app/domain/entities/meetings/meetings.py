from __future__ import annotations
from uuid import UUID
from datetime import datetime
from app.domain.entities import BaseEntity
from app.domain.enums import MeetingStatus


class Meeting(BaseEntity):
    def __init__(self, team_id: UUID, name: str, resume: str | None, 
                 date: datetime, status: MeetingStatus, 
                 previous: Meeting | None, next: Meeting | None, id: UUID | None):
        super().__init__(id)
        self.team_id = team_id
        self.name = name
        self.resume = resume
        self.date = date
        self.status = status
        self.previous = previous
        self.next = next