from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base_association import BaseAssociation

if TYPE_CHECKING:
    from app.infrastructure.database.models.meetings.meeting import MeetingModel
    from app.infrastructure.database.models.meetings.task import TaskModel


class MeetingTaskModel(BaseAssociation):
    """Модель связи встречи и задачи (many-to-many)"""
    __tablename__ = "meeting_tasks"
    
    # Идентификатор встречи
    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # Идентификатор задачи
    task_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # Уникальный индекс для связи встречи и задачи
    __table_args__ = (
        UniqueConstraint("meeting_id", "task_id", name="uq_meeting_tasks_meeting_task"),
    )
    # Связь с встречей
    meeting: Mapped["MeetingModel"] = relationship(
        "MeetingModel",
        back_populates="meeting_tasks",
    )
    # Связь с задачей
    task: Mapped["TaskModel"] = relationship(
        "TaskModel",
        back_populates="meeting_tasks",
    )

