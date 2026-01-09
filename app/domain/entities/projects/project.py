from datetime import datetime
from pydantic import Field
from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import ProjectStatus, Semester
from app.domain.entities.custom_types import LongText, NameField, MediumText


class Project(BaseEntity):
    """Доменная модель проекта"""

    name: NameField
    description: LongText = Field(None, examples=["Описание проекта"])
    goal: MediumText = Field(None, examples=["Цель проекта"])
    requirements: LongText = Field(None, examples=["Требования к проекту"])
    eval_criteria: MediumText = Field(
        None,
        examples=["Критерии оценки проекта"]
    )
    semester: Semester
    status: ProjectStatus = ProjectStatus.PLANNED
    
    @staticmethod
    def _get_current_semester() -> Semester:
        """Определяет текущий семестр по месяцу"""
        current_month = datetime.now().month
        if 2 <= current_month <= 7:
            return Semester.SPRING
        else:
            return Semester.AUTUMN
        
    year: int = Field(
        default_factory=lambda: datetime.now().year,
        ge=2000
    )

    semester: Semester = Field(
        default_factory=_get_current_semester
    )
