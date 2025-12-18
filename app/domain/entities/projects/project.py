from datetime import datetime
from pydantic import Field
from app.domain.entities.base_entity import BaseEntity
from app.domain.enums import ProjectStatus, Semester


class Project(BaseEntity):
    """Доменная модель проекта"""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000, alias="desсription")
    goal: str | None = Field(None, max_length=1000)
    requirements: str | None = Field(None, max_length=2000)
    eval_criteria: str | None = Field(None, max_length=2000)
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
