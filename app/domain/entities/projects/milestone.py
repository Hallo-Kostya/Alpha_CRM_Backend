from pydantic import Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import MilestoneType
from app.domain.entities.custom_types import LongText


class Milestone(BaseEntity):
    """Доменная модель контрольной точки проекта"""

    project_id: UUID
    date: datetime
    title: str = Field(..., min_length=1, max_length=255)
    type: MilestoneType
    description: LongText = Field(None, examples=["Описание контрольной точки"])
