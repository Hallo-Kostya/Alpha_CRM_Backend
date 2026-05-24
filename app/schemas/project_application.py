from __future__ import annotations
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.common.enums import ProjectApplicationStatus, MeetingStatus
from app.schemas.project import ProjectRead


class ProjectInterviewPOST(BaseModel):
    name: str
    date: datetime
    resume: str | None = None
    status: MeetingStatus | None = None


class ProjectInterviewPATCH(BaseModel):
    name: str | None = None
    date: datetime | None = None
    resume: str | None = None
    status: MeetingStatus | None = None


class ProjectInterviewGET(BaseModel):
    id: UUID
    name: str
    date: datetime
    status: MeetingStatus
    resume: str | None = None


class ProjectApplicationPATCH(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    team_members: list[TeamMemberPATCH] | None = None
    team_name: str | None = None
    status: ProjectApplicationStatus | None = None


class ProjectApplicationGET(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: UUID
    mean_project_score: float
    project: ProjectRead
    team_name: str
    status: ProjectApplicationStatus
    description: str | None = None
    team_members: list[TeamMemberGET] = Field(default_factory=list)
    interview: ProjectInterviewGET | None = None
    vk_sender_id: int | None = None


class ProjectApplicationGETLimited(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: UUID
    mean_project_score: float
    project_id: UUID
    team_name: str
    status: ProjectApplicationStatus
    team_members: list[TeamMemberGET] = Field(default_factory=list)
    description: str | None = None
    interview_id: UUID | None = None
    vk_sender_id: int | None = None


class TeamMemberPOST(BaseModel):
    fullname: str
    role: str
    study_group: str


class TeamMemberGET(BaseModel):
    id: UUID
    fullname: str
    role: str
    study_group: str


class TeamMemberPATCH(BaseModel):
    id: UUID
    fullname: str | None = None
    role: str | None = None
    study_group: str | None = None


class ProjectApplicationPOST(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    project_id: UUID
    vk_sender_id: int
    team_name: str
    team_members: list[TeamMemberPOST]
    description: str | None = None
    mean_project_score: float | None = None
    status: ProjectApplicationStatus | None = None
