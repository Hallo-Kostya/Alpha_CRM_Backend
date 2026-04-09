from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TeamMember(BaseModel):
    """Team member model with all fields."""
    model_config = ConfigDict(from_attributes=True)
    
    team_id: UUID
    student_id: UUID
    role: Optional[str] = None
    study_group: Optional[str] = None


class TeamMemberCreate(BaseModel):
    """Добавление студента в команду"""

    student_id: UUID
    role: Optional[str] = Field(None, examples=["Роль в команде"])
    study_group: Optional[str] = Field(None, examples=["Группа студента"])


class TeamMemberUpdate(BaseModel):
    """Обновление данных связи студент-команда"""

    role: Optional[str] = Field(None, examples=["Роль в команде"])
    study_group: Optional[str] = Field(None, examples=["Группа студента"])


class TeamMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: UUID
    student_id: UUID
    role: Optional[str] = None
    study_group: Optional[str] = None


class TeamMemberWithTeamInfo(BaseModel):
    """Team member + team information."""

    team_id: UUID
    student_id: UUID
    role: Optional[str] = None
    study_group: Optional[str] = None
    team_name: str
    team_group_link: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Aliases for backward compatibility
TeamMemberRead = TeamMember
TeamMemberResponse = TeamMember
