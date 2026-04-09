from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

from app.domain.entities.custom_types import NameField
from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.semester import Semester


class ProjectCreate(BaseModel):
    name: NameField = Field(..., examples=["Название проекта"])
    description: Optional[str] = Field(None, examples=["Описание проекта"])
    goal: Optional[str] = Field(None, examples=["Цель проекта"])
    requirements: Optional[str] = Field(None, examples=["Требования к проекту"])
    eval_criteria: Optional[str] = Field(None, examples=["Критерии оценки проекта"])
    year: int
    semester: Semester
    status: ProjectStatus = ProjectStatus.PLANNED

class ProjectCreateMinimal(BaseModel):
    name: NameField = Field(..., examples=["Название проекта"])
    # год и семестр подставляются по умолчанию, если клиент не передаёт
    year: Optional[int] = Field(
        default_factory=lambda: datetime.now().year,
        examples=["2026"],
        description="Год проведения (по умолчанию текущий)"
    )
    semester: Optional[Semester] = Field(
        default_factory=lambda: Semester.SPRING if datetime.now().month < 7 else Semester.AUTUMN,
        description="Семестр (по умолчанию определяется по текущей дате)",
    )
    status: Optional[ProjectStatus] = None

class ProjectUpdate(BaseModel):
    name: Optional[NameField] = Field(None, examples=["Название проекта"])
    description: Optional[str] = Field(None, examples=["Описание проекта"])
    goal: Optional[str] = Field(None, examples=["Цель проекта"])
    requirements: Optional[str] = Field(None, examples=["Требования к проекту"])
    eval_criteria: Optional[str] = Field(None, examples=["Критерии оценки проекта"])
    year: Optional[int] = None
    semester: Optional[Semester] = None
    status: Optional[ProjectStatus] = None


class ProjectSummary(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    teams_count: int
    members_count: int


class ProjectSummaryResponse(BaseModel):
    total: int
    projects: List[ProjectSummary]
