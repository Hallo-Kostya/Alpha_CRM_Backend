from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.common.fields import NameField
from app.schemas.team_member import TeamMember, TeamMemberDetail


class CuratorShort(BaseModel):
    """Краткая информация о кураторе для отображения в команде."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str


class Team(BaseModel):
    """Team model with all fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    members: list[TeamMember] = Field(default_factory=list)
    group_link: Optional[str] = None
    curators: list[CuratorShort] = Field(default_factory=list)


class TeamDetail(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    members: list[TeamMemberDetail] = Field(default_factory=list)
    group_link: Optional[str] = None
    curators: list[CuratorShort] = Field(default_factory=list)


class TeamCreate(BaseModel):
    name: NameField = Field(..., examples=["Название команды"])
    group_link: Optional[str] = None
    curator_id: Optional[UUID] = Field(
        None, description="ID куратора для привязки при создании (опционально)"
    )


class TeamUpdate(BaseModel):
    name: Optional[NameField] = Field(None, examples=["Название команды"])
    group_link: Optional[str] = None


class TeamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    group_link: Optional[str] = None


class TeamMemberSummary(BaseModel):
    id: UUID
    full_name: str


class TeamSummary(BaseModel):
    id: UUID
    name: str
    members_count: int
    members: list[TeamMemberSummary] = Field(default_factory=list)


class TeamSummaryResponse(BaseModel):
    total: int
    teams: list[TeamSummary]


# Aliases for backward compatibility
TeamResponse = TeamRead