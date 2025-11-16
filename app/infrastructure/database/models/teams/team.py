from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.meetings.meeting import MeetingModel
    from app.infrastructure.database.models.persons.curator import CuratorModel
    from app.infrastructure.database.models.projects.project import ProjectModel
    from app.infrastructure.database.models.projects.project_team import ProjectTeamModel
    from app.infrastructure.database.models.teams.curator_team import CuratorTeamModel
    from app.infrastructure.database.models.teams.team_member import TeamMemberModel


class TeamModel(Base):
    """Модель команды"""
    __tablename__ = "teams"
    
    # Название команды
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Ссылка на группу (например, чат команды)
    group_link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    
    # FK на куратора команды (один куратор, опционально)
    curator_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("curators.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Отношение к куратору (один куратор)
    curator: Mapped["CuratorModel | None"] = relationship(
        "CuratorModel",
        back_populates="teams",
    )
    
    # Участники команды (связующая таблица team_members)
    members: Mapped[list["TeamMemberModel"]] = relationship(
        "TeamMemberModel",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    
    # Собрания, связанные с командой
    meetings: Mapped[list["MeetingModel"]] = relationship(
        "MeetingModel",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    
    # Связи с проектами через таблицу project_teams (M2M)
    project_teams: Mapped[list["ProjectTeamModel"]] = relationship(
        "ProjectTeamModel",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    
    # Проекты команды (через вторичную таблицу project_teams, только просмотр)
    projects: Mapped[list["ProjectModel"]] = relationship(
        "ProjectModel",
        secondary="project_teams",
        back_populates="teams",
        viewonly=True,
    )
    
    # Связи с кураторами через промежуточную таблицу curator_teams (M2M, модель связей)
    curator_team_links: Mapped[list["CuratorTeamModel"]] = relationship(
        "CuratorTeamModel",
        back_populates="team",
        cascade="all, delete-orphan",
    )
    
    # Кураторы команды по M2M, только просмотр (через curator_teams)
    curators_m2m: Mapped[list["CuratorModel"]] = relationship(
        "CuratorModel",
        secondary="curator_teams",
        back_populates="teams_m2m",
        viewonly=True,
    )

