from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLEnum

from app.infrastructure.database.entity_base import BaseEntity
from app.domain.enums.project_team_status import ProjectTeamStatus

if TYPE_CHECKING:
    from app.infrastructure.database.models.projects.project import ProjectModel
    from app.infrastructure.database.models.teams.team import TeamModel


class ProjectTeamModel(BaseEntity):
    """Модель связи проекта и команды (many-to-many)"""
    __tablename__ = "project_teams"
    
    # ID проекта
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,  # NOT NULL вместо primary_key
    )
    # ID команды
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,  # NOT NULL вместо primary_key
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    status: Mapped[ProjectTeamStatus] = mapped_column(
        SQLEnum(  # Используем SQLEnum вместо StrEnum
            ProjectTeamStatus, 
            native_enum=False, 
            values_callable=lambda x: [e.value for e in ProjectTeamStatus]
        ),
        nullable=False,
        default=ProjectTeamStatus.ACTIVE
    )
    
    __table_args__ = (
        UniqueConstraint("project_id", "team_id", name="uq_project_teams_project_team"),
        # Обеспечиваем уникальность пары project_id + team_id
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