from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.persons.auth_refresh_token import AuthRefreshTokenModel
from app.infrastructure.database.models.persons.person import PersonModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.meetings.attendance import AttendanceModel
    from app.infrastructure.database.models.projects.evaluation import EvaluationModel
    from app.infrastructure.database.models.teams.curator_team import CuratorTeamModel
    from app.infrastructure.database.models.teams.team import TeamModel
    from app.infrastructure.database.models.persons.oauth_token import OAuthTokenModel


class CuratorModel(PersonModel):
    """Модель куратора"""
    __tablename__ = "curators"
    
    password_hash = mapped_column(String(255), nullable=False)
    last_login_at = mapped_column(DateTime(timezone=True))
    
    auth_tokens: Mapped[list["AuthRefreshTokenModel"]] = relationship(
        "AuthRefreshTokenModel",
        back_populates="curator",
        cascade="all, delete-orphan",
    )

    oauthtokens: Mapped[list["OAuthTokenModel"]] = relationship(
        "OAuthTokenModel",
        back_populates="curator",
        cascade="all, delete-orphan",
    )

    # Основные команды (через curator_id в TeamModel, один основной куратор)
    teams: Mapped[list["TeamModel"]] = relationship(
        "TeamModel",
        foreign_keys="TeamModel.curator_id",
        back_populates="curator",
    )
    # Many-to-many связь через curator_teams
    curator_team_links: Mapped[list["CuratorTeamModel"]] = relationship(  
        "CuratorTeamModel",
        back_populates="curator",
        cascade="all, delete-orphan",
    )
    # Команды, для которых является куратором (M2M)
    teams_m2m: Mapped[list["TeamModel"]] = relationship(  
        "TeamModel",
        secondary="curator_teams",
        back_populates="curators_m2m",
        viewonly=True,
    )
    # Оценки от куратора
    evaluations: Mapped[list["EvaluationModel"]] = relationship(  
        "EvaluationModel",
        back_populates="curator",
    )
    
    # Посещаемость куратора на встречах
    attendances: Mapped[list["AttendanceModel"]] = relationship(
        "AttendanceModel",
        foreign_keys="AttendanceModel.curator_id",
        back_populates="curator",
        cascade="all, delete-orphan",
    )

