from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.semester import Semester


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    goal: Optional[str] = None
    requirements: Optional[str] = None
    eval_criteria: Optional[str] = None
    year: int
    semester: Semester
    status: ProjectStatus = ProjectStatus.PLANNED


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    requirements: Optional[str] = None
    eval_criteria: Optional[str] = None
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
