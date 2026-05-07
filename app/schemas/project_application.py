from __future__ import annotations
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.common.enums import ProjectApplicationStatus
from app.schemas.team import Team
from app.schemas.project import ProjectRead
from app.schemas.meeting import MeetingRead


class ProjectApplicationPOST(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    project_id: UUID
    team_id: UUID
    mean_project_score: float | None = None
    vk_sender_id: int | None = None
    status: ProjectApplicationStatus | None = None
    meeting_id: UUID | None = None


class ProjectApplicationPATCH(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    mean_project_score: float | None = None
    project_id: UUID | None = None
    team_id: UUID | None = None
    vk_sender_id: int | None = None
    status: ProjectApplicationStatus | None = None
    meeting_id: UUID | None = None


class ProjectApplicationGET(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    mean_project_score: float
    project: ProjectRead
    team: Team
    status: ProjectApplicationStatus
    meeting: MeetingRead | None = None
    vk_sender_id: int | None = None
    