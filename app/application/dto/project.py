from typing import Optional
from pydantic import BaseModel, Field

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


class ProjectUpdate(BaseModel):
    name: Optional[NameField] = Field(None, examples=["Название проекта"])
    description: Optional[str] = Field(None, examples=["Описание проекта"])
    goal: Optional[str] = Field(None, examples=["Цель проекта"])
    requirements: Optional[str] = Field(None, examples=["Требования к проекту"])
    eval_criteria: Optional[str] = Field(None, examples=["Критерии оценки проекта"])
    year: Optional[int] = None
    semester: Optional[Semester] = None
    status: Optional[ProjectStatus] = None
