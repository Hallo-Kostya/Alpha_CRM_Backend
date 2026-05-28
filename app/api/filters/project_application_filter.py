from datetime import datetime
import uuid

from pydantic import BaseModel
from app.common.enums import ProjectApplicationStatus, ProjectInterviewStatus, Semester


class ProjectApplicationFilter(BaseModel):
    id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    vk_sender_id: int | None = None
    status: ProjectApplicationStatus | None = None
    mean_project_score: float | None = None
    project_name: str | None = None
    year: int | None = None
    semester: Semester | None = None


class ProjectInterviewFilter(BaseModel):
    id: uuid.UUID | None = None
    project_application_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    vk_sender_id: int | None = None
    project_name: str | None = None
    year: int | None = None
    semester: Semester | None = None
    date: datetime | None = None
    curators_rate: int | None = None
    interview_status: list[ProjectInterviewStatus] | None = None
