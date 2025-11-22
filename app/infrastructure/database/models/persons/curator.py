from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.persons.person import PersonModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.meetings.attendance import AttendanceModel
    from app.infrastructure.database.models.projects.evaluation import EvaluationModel
    from app.infrastructure.database.models.teams.curator_team import CuratorTeamModel
    from app.infrastructure.database.models.teams.team import TeamModel


class CuratorModel(PersonModel):
    """Модель куратора"""
    __tablename__ = "curators"
    
    #Токены
    refresh_token :Mapped[str] = mapped_column(String(512),nullable=False,unique=True,index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False,index=True)
    is_revoked: Mapped[bool] = mapped_column(nullable=False,default=False,index=True)

    # Outlook-аккаунт куратора (уникальный) 
    outlook_email: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    outlook_access_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    outlook_refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    outlook_token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # Google
    google_id: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    google_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_access_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    google_refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    google_token_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

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

