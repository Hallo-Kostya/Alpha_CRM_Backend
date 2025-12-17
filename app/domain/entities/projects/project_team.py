from datetime import datetime
from uuid import UUID
from app.domain.entities.base_entity import BaseEntity
from app.domain.entities.projects.project import Project
from app.domain.entities.teams.team import Team

class ProjectTeam(BaseEntity):
    project_id: UUID
    team_id: UUID

    project: Project
    team: Team
