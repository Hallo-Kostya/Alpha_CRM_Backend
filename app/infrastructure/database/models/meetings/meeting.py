from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base import Base
from app.domain.enums.meeting_status import MeetingStatus

if TYPE_CHECKING:
    from app.infrastructure.database.models.artifacts.artifact_link import ArtifactLinkModel
    from app.infrastructure.database.models.meetings.attendance import AttendanceModel
    from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
    from app.infrastructure.database.models.teams.team import TeamModel


class MeetingModel(Base):
    """Модель встречи"""
    __tablename__ = "meetings"

    # Название встречи
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Описание встречи
    resume: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    # Дата встречи
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Статус встречи
    status: Mapped[MeetingStatus] = mapped_column(
        SQLEnum(MeetingStatus, native_enum=False, values_callable=lambda x: [e.value for e in MeetingStatus]),
        nullable=False,
        default=MeetingStatus.SCHEDULED.value
    )
    # Предыдущая встреча
    previous_meeting_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Следующая встреча
    next_meeting_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Команда на встрече
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Связь с командой на встрече
    team: Mapped["TeamModel"] = relationship(
        "TeamModel",
        back_populates="meetings",
    )
    # Связь с предыдущей встречей
    previous: Mapped["MeetingModel | None"] = relationship(
        "MeetingModel",
        foreign_keys=[previous_meeting_id],
        remote_side=lambda: MeetingModel.id,
    )
    # Связь с следующей встречей
    next: Mapped["MeetingModel | None"] = relationship(
        "MeetingModel",
        foreign_keys=[next_meeting_id],
        remote_side=lambda: MeetingModel.id,
    )
    # Связь с посещаемостью встречи
    attendances: Mapped[list["AttendanceModel"]] = relationship(
        "AttendanceModel",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )
    # Связь с задачами на встрече
    meeting_tasks: Mapped[list["MeetingTaskModel"]] = relationship(
        "MeetingTaskModel",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )
    
    # Артефакты встречи
    artifact_links: Mapped[list["ArtifactLinkModel"]] = relationship(
        "ArtifactLinkModel",
        foreign_keys="ArtifactLinkModel.meeting_id",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )

