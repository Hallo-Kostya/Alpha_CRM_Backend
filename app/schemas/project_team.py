from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.common.enums import ProjectTeamStatus, Semester


class ProjectTeam(BaseModel):
    """Project team model with all fields."""
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    
    project_id: UUID
    team_id: UUID
    assigned_at: datetime
    status: ProjectTeamStatus

    @field_validator("project_id", "team_id", mode="before")
    @classmethod
    def validate_uuid(cls, v: Any) -> UUID:
        if isinstance(v, UUID):
            return v
        try:
            return UUID(str(v))
        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(f"Invalid UUID value: {v}") from e


class ProjectTeamCreate(BaseModel):
    team_id: UUID
    status: ProjectTeamStatus = ProjectTeamStatus.ACTIVE


class ProjectTeamUpdate(BaseModel):
    status: Optional[ProjectTeamStatus] = None


class ProjectTeamResponse(BaseModel):
    project_id: UUID
    team_id: UUID
    assigned_at: datetime
    status: ProjectTeamStatus

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    @field_validator("project_id", "team_id", mode="before")
    @classmethod
    def validate_uuid(cls, v: Any) -> UUID:
        if isinstance(v, UUID):
            return v
        try:
            return UUID(str(v))
        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(f"Invalid UUID value: {v}") from e


class ProjectTeamWithInfo(BaseModel):
    project_id: UUID
    team_id: UUID
    assigned_at: datetime
    status: ProjectTeamStatus
    project_name: str
    team_name: str
    project_year: int
    project_semester: Semester

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    @field_validator("project_id", "team_id", mode="before")
    @classmethod
    def validate_uuid(cls, v: Any) -> UUID:
        if isinstance(v, UUID):
            return v
        try:
            return UUID(str(v))
        except (ValueError, TypeError, AttributeError) as e:
            raise ValueError(f"Invalid UUID value: {v}") from e

    @field_validator("project_semester", mode="before")
    @classmethod
    def validate_semester(cls, v: Any) -> Semester:
        if isinstance(v, Semester):
            return v
        if isinstance(v, str):
            try:
                return Semester(v)
            except ValueError:
                for semester in Semester:
                    if semester.value == v:
                        return semester
                raise ValueError(f"Invalid semester string: {v}")
        if isinstance(v, int):
            for semester in Semester:
                if semester.value == str(v):
                    return semester
            raise ValueError(f"Invalid semester integer: {v}")
        raise ValueError(f"Cannot convert {type(v)} to Semester")


# Aliases for backward compatibility
ProjectTeamRead = ProjectTeam
