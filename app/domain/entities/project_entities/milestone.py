from datetime import datetime
from typing import Optional
from uuid import UUID
from app.domain.entities import BaseEntity
from app.domain.enums import MilestoneType


class Milestone(BaseEntity):
    def __init__(self, project_id: UUID, date: datetime, title: str, type: MilestoneType, desription: str, id: Optional[UUID]):
        super().__init__(id)
        self.project_id = project_id
        self.date = date
        self.title = title
        self.type = type
        self.description = desription