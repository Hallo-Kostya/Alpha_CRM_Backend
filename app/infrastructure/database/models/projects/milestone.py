from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.entity_base import BaseEntity
from app.domain.enums.milestone_type import MilestoneType

if TYPE_CHECKING:
    from app.infrastructure.database.models.projects.project import ProjectModel


class MilestoneModel(BaseEntity):
    """Модель вехи проекта"""
    __tablename__ = "milestones"
    
    # ID проекта
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    # Дата вехи
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Название вехи
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    # Тип вехи
    type: Mapped[MilestoneType] = mapped_column(
        SQLEnum(MilestoneType, native_enum=False, values_callable=lambda x: [e.value for e in MilestoneType]),
        nullable=False,
    )
    # Описание вехи
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    
    # Связь с проектом
    project: Mapped["ProjectModel"] = relationship(
        "ProjectModel",
        back_populates="milestones",
    )

