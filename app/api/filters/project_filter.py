import uuid

from pydantic import BaseModel
from app.common.enums import Semester, ProjectStatus


class ProjectFilter(BaseModel):
    id: uuid.UUID | None = None
    name: str | None = None
    year: int | None = None
    semester: Semester | None = None
    status: ProjectStatus | None = None
    team_id: uuid.UUID | None = None
