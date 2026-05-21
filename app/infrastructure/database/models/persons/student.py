from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database.models.persons.person import PersonModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.meetings.attendance import AttendanceModel
    from app.infrastructure.database.models.teams.team_member import TeamMemberModel


class StudentModel(PersonModel):
    """Модель студента"""

    __tablename__ = "students"

    # Связь с командой
    team_links: Mapped[list["TeamMemberModel"]] = relationship(
        "TeamMemberModel",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Посещаемость студента на встречах
    attendances: Mapped[list["AttendanceModel"]] = relationship(
        "AttendanceModel",
        foreign_keys="AttendanceModel.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )
