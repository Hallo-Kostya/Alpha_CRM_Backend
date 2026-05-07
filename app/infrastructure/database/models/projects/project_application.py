from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLEnum

from app.common.enums import ProjectApplicationStatus
from app.infrastructure.database.models.entity_base import BaseEntity


if TYPE_CHECKING:
    from app.infrastructure.database.models.projects.project import ProjectModel
    from app.infrastructure.database.models.teams.team import TeamModel
    from app.infrastructure.database.models.meetings import MeetingModel


class ProjectApplicationModel(BaseEntity):
    """Модель заявки на исполнение проекта"""
    __tablename__ = "project_applications"
    
    # ID проекта
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,  # NOT NULL вместо primary_key
    )
    # ID команды
    team_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,  # NOT NULL вместо primary_key
    )
    # ID встречи (интервью)
    meeting_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=True,
        default=None
    )
    
    # ID отправителя заявки из вк
    vk_sender_id: Mapped[int | None] = mapped_column(Integer, default=None, nullable=True)

    status: Mapped[ProjectApplicationStatus] = mapped_column(
        SQLEnum(  # Используем SQLEnum вместо StrEnum
            ProjectApplicationStatus, 
            native_enum=False, 
            values_callable=lambda x: [e.value for e in ProjectApplicationStatus]
        ),
        nullable=False,
        default=ProjectApplicationStatus.NEW
    )
    
    __table_args__ = (
        UniqueConstraint("project_id", "team_id", name="uq_project_applications_team"),
        # Обеспечиваем уникальность пары project_id + team_id
    )
    
    # Связь с проектом
    project: Mapped["ProjectModel"] = relationship(
        "ProjectModel",
        back_populates="project_applications",
    )
    
    # Связь с командой
    team: Mapped["TeamModel"] = relationship(
        "TeamModel",
        back_populates="team_applications",
    )

    # Связь с интервью 
    meeting: Mapped["MeetingModel"] = relationship(
        "MeetingModel"
    )

    # последний результат команды
    mean_project_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    def __str__(self) -> str:
        return f"{self.id}: Заявка на {self.project_id} от {self.team_id}, отправитель из вк: {self.vk_sender_id}"