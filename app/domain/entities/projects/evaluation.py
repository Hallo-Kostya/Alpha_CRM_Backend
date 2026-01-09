from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from app.domain.enums import EvaluationType
from app.domain.entities.custom_types import LongText


class Evaluation(BaseModel):
    """Оценка проекта куратором"""

    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    project_id: UUID
    curator_id: UUID
    type: EvaluationType
    comment: LongText = Field(None, examples=["Комментарий к оценке"])
