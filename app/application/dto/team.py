from typing import Optional
from pydantic import BaseModel, Field

from app.domain.entities.custom_types import NameField


class TeamCreate(BaseModel):
    name: NameField = Field(..., examples=["Название команды"])
    group_link: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[NameField] = Field(None, examples=["Название команды"])
    group_link: Optional[str] = None


class TeamMemberSummary(BaseModel):
    id: str  # UUID as str
    full_name: str


class TeamSummary(BaseModel):
    id: str  # UUID as str
    name: str
    members_count: int
    members: list[TeamMemberSummary]


class TeamSummaryResponse(BaseModel):
    total: int
    teams: list[TeamSummary]