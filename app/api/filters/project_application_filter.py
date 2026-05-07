import uuid

from pydantic import BaseModel
from app.common.enums import ProjectApplicationStatus


class ProjectApplicationFilter(BaseModel):
    id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    team_id: uuid.UUID | None = None
    vk_sender_id: int | None = None
    status: ProjectApplicationStatus | None = None
    last_project_score: float | None = None
    meeting_id: uuid.UUID | None = None