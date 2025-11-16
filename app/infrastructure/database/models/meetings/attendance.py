from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.meetings.meeting import MeetingModel
    from app.infrastructure.database.models.persons.curator import CuratorModel
    from app.infrastructure.database.models.persons.student import StudentModel


class AttendanceModel(Base):
    """Модель посещаемости встречи для студента или куратора"""
    __tablename__ = "attendances"
    
    # FK на встречу
    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # FK на студента (nullable)
    student_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # FK на куратора (nullable)
    curator_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("curators.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    # Флаг присутствия
    is_present: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    __table_args__ = (
        # Один из FK должен быть заполнен
        CheckConstraint(
            "(student_id IS NOT NULL AND curator_id IS NULL) OR "
            "(student_id IS NULL AND curator_id IS NOT NULL)",
            name="ck_attendances_one_fk"
        ),
        # Уникальность посещения студента на встрече
        UniqueConstraint("meeting_id", "student_id", name="uq_attendances_meeting_student"),
        # Уникальность посещения куратора на встрече
        UniqueConstraint("meeting_id", "curator_id", name="uq_attendances_meeting_curator"),
    )
    
    # Relationships
    meeting: Mapped["MeetingModel"] = relationship(
        "MeetingModel",
        back_populates="attendances",
    )
    
    student: Mapped["StudentModel | None"] = relationship(
        "StudentModel",
        foreign_keys=[student_id],
        back_populates="attendances",
    )
    
    curator: Mapped["CuratorModel | None"] = relationship(
        "CuratorModel",
        foreign_keys=[curator_id],
        back_populates="attendances",
    )

