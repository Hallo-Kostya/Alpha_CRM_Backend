from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.persons import StudentModel
    from app.infrastructure.database.models.teams.team import TeamModel


class TeamMemberModel(Base):
    """Модель связи студента с командой"""
    __tablename__ = "team_members"
    
    # FK на команду (team)
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # FK на студента (student)
    student_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # Роль студента в команде
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Учебная группа студента на момент участия
    study_group: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("team_id", "student_id", name="uq_team_members_team_student"),
    )
    
    # Отношение к команде
    team: Mapped["TeamModel"] = relationship(
        "TeamModel",
        back_populates="members",
    )
    # Отношение к студенту
    student: Mapped["StudentModel"] = relationship(
        "StudentModel",
        back_populates="team_links",
    )
