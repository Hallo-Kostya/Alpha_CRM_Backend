from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base_association import BaseAssociation

if TYPE_CHECKING:
    from app.infrastructure.database.models.projects.project import ProjectModel
    from app.infrastructure.database.models.teams.team import TeamModel


class ProjectTeamModel(BaseAssociation):
    """Модель связи проекта и команды (many-to-many)"""
    __tablename__ = "project_teams"
    
    # ID проекта
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # ID команды
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True,
    )
    
    __table_args__ = (
        UniqueConstraint("project_id", "team_id", name="uq_project_teams_project_team"),
    )
    
    # Связь с проектом
    project: Mapped["ProjectModel"] = relationship(
        "ProjectModel",
        back_populates="project_teams",
    )
    
    # Связь с командой
    team: Mapped["TeamModel"] = relationship(
        "TeamModel",
        back_populates="project_teams",
    )
