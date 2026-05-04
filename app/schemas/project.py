from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import ProjectStatus, Semester
from app.common.fields import NameField
from app.schemas.project_team import ProjectTeam


class Project(BaseModel):
    """Project read/response model with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    goal: Optional[str] = None
    requirements: Optional[str] = None
    eval_criteria: Optional[str] = None
    year: int
    semester: Semester
    status: ProjectStatus
    project_teams: list[ProjectTeam]

    @staticmethod
    def get_current_semester() -> Semester:
        """Determine current semester by month."""
        current_month = datetime.now().month
        if 2 <= current_month <= 7:
            return Semester.SPRING
        else:
            return Semester.AUTUMN

    @classmethod
    def compute_status(cls, year: int, semester: Semester) -> ProjectStatus:
        """Compute project status based on year/semester relative to current date."""
        now = datetime.now()
        current_year = now.year
        current_semester = cls.get_current_semester()

        if year > current_year:
            return ProjectStatus.PLANNED
        elif year < current_year:
            return ProjectStatus.COMPLETED
        else:  # same year
            if semester == current_semester:
                return ProjectStatus.IN_PROGRESS
            else:
                return ProjectStatus.COMPLETED


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
    description: Optional[str] = Field(None, examples=["Описание проекта"])
    year: Optional[int] = Field(
        default_factory=lambda: datetime.now().year,
        examples=["2026"],
        description="Год проведения (по умолчанию текущий)",
    )
    semester: Optional[Semester] = Field(
        default_factory=lambda: Semester.SPRING
        if datetime.now().month < 7
        else Semester.AUTUMN,
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


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    goal: Optional[str] = None
    requirements: Optional[str] = None
    eval_criteria: Optional[str] = None
    year: int
    semester: Semester
    status: ProjectStatus


class ProjectSummary(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    teams_count: int
    members_count: int


class ProjectSummaryResponse(BaseModel):
    total: int
    projects: List[ProjectSummary]


# Aliases for backward compatibility with services
ProjectResponse = ProjectRead
