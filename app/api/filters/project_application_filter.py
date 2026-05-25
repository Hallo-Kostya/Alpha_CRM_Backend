import uuid

from pydantic import BaseModel
from app.common.enums import ProjectApplicationStatus, Semester


class ProjectApplicationFilter(BaseModel):
    id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    vk_sender_id: int | None = None
    status: ProjectApplicationStatus | None = None
    mean_project_score: float | None = None
    project_name: str | None = None
    year: int | None = None
    semester: Semester | None = None
