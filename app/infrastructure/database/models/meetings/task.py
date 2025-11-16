from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel


class TaskModel(Base):
    """Модель задачи"""
    __tablename__ = "tasks"
    
    # Описание задачи
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    # Статус задачи
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Связь с задачами на встрече
    meeting_tasks: Mapped[list["MeetingTaskModel"]] = relationship(
        "MeetingTaskModel",
        back_populates="task",
        cascade="all, delete-orphan",
    )

