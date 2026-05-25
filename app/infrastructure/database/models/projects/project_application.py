from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLEnum
from app.common.enums import ProjectApplicationStatus
from app.infrastructure.database.models.entity_base import BaseEntity
from app.infrastructure.database.models.meetings.meeting import BaseMeetingModel

if TYPE_CHECKING:
    from app.infrastructure.database.models.projects.project import ProjectModel


class ProjectApplicationMemberModel(BaseEntity):
    __tablename__ = "project_application_members"

    project_application_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_applications.id", ondelete="CASCADE"),
        nullable=False,
    )
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    study_group: Mapped[str | None] = mapped_column(String(100), nullable=True)

    project_application: Mapped["ProjectApplicationModel"] = relationship(
        "ProjectApplicationModel",
        back_populates="members",
    )

    def __str__(self) -> str:
        return f"{self.fullname}, {self.role}, {self.study_group}, Заявка #{self.project_application_id}"


class ProjectInterviewModel(BaseMeetingModel):
    __tablename__ = "project_interviews"

    # FK на заявку
    project_application_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_applications.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Связь с заявкой
    project_application: Mapped["ProjectApplicationModel"] = relationship(
        "ProjectApplicationModel",
        back_populates="interview",
    )


class ProjectApplicationModel(BaseEntity):
    """Модель заявки на исполнение проекта"""

    __tablename__ = "project_applications"

    # ID проекта
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Описание заявки
    description: Mapped[str] = mapped_column(String(2000), nullable=True)

    # Название команды
    team_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Участники команды
    members: Mapped[list["ProjectApplicationMemberModel"]] = relationship(
        "ProjectApplicationMemberModel",
        back_populates="project_application",
        cascade="all, delete-orphan",
    )

    # ID отправителя заявки из вк
    vk_sender_id: Mapped[int | None] = mapped_column(
        Integer, default=None, nullable=True
    )

    # Статус заявки
    status: Mapped[ProjectApplicationStatus] = mapped_column(
        SQLEnum(  # Используем SQLEnum вместо StrEnum
            ProjectApplicationStatus,
            native_enum=False,
            values_callable=lambda x: [e.value for e in ProjectApplicationStatus],
        ),
        nullable=False,
        default=ProjectApplicationStatus.NEW,
    )

    # Связь с проектом
    project: Mapped["ProjectModel"] = relationship(
        "ProjectModel",
        back_populates="project_applications",
    )

    # Связь с интервью
    interview: Mapped["ProjectInterviewModel"] = relationship(
        "ProjectInterviewModel",
        back_populates="project_application",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    # последний результат команды
    mean_project_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )

    def __str__(self) -> str:
        return f"Команда: {self.team_name}, проект: {self.project_id}"
