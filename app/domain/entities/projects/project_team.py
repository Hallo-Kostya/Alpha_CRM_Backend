from datetime import datetime, timezone
from uuid import UUID

from pydantic import ConfigDict, Field
from app.domain.entities.base_entity import BaseEntity
from app.domain.entities.projects.project import Project
from app.domain.entities.teams.team import Team
from app.domain.enums.project_team_status import ProjectTeamStatus


class ProjectTeam(BaseEntity):
    """Доменная модель связи проекта и команды"""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )

    project_id: UUID
    team_id: UUID
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: ProjectTeamStatus = ProjectTeamStatus.ACTIVE
    role_in_project: str | None = Field(None, max_length=100)
