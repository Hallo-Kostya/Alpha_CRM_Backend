from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from app.domain.enums import EvaluationType


class Evaluation(BaseModel):
    """Оценка проекта куратором"""

    model_config = ConfigDict(from_attributes=True, validate_assignment=True)

    project_id: UUID
    curator_id: UUID
    type: EvaluationType
    comment: Optional[str] = Field(None, max_length=2000)
