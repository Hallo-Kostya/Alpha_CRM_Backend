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

    @classmethod
    def compute_status(cls, year: int, semester: Semester) -> ProjectStatus:
        """Вычисляет статус проекта по году/семестру относительно текущей даты."""
        now = datetime.now()
        current_year = now.year
        current_semester = cls._get_current_semester()

        if year > current_year:
            return ProjectStatus.PLANNED
        elif year < current_year:
            return ProjectStatus.COMPLETED
        else:  # равный год
            if semester == current_semester:
                return ProjectStatus.IN_PROGRESS
            else:
                return ProjectStatus.COMPLETED
