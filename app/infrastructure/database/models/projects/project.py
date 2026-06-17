from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import ProjectStatus, Semester
from app.infrastructure.database.models.entity_base import BaseEntity

if TYPE_CHECKING:
    from app.infrastructure.database.models.projects.evaluation import EvaluationModel
    from app.infrastructure.database.models.projects.milestone import MilestoneModel
    from app.infrastructure.database.models.projects.project_team import (
        ProjectTeamModel,
    )
    from app.infrastructure.database.models.teams.team import TeamModel
    from app.infrastructure.database.models.projects.project_application import (
        ProjectApplicationModel,
    )


class ProjectModel(BaseEntity):
    """Модель проекта"""

    __tablename__ = "projects"

    # Название проекта
    name: Mapped[str] = mapped_column(String(1000), nullable=False)
    # Описание проекта
    description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    # Цель проекта
    goal: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    # Требования к проекту
    requirements: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    # Критерии оценки проекта
    eval_criteria: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    # Год проведения проекта
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    # Семестр
    semester: Mapped[Semester] = mapped_column(
        SQLEnum(
            Semester,
            native_enum=False,
            values_callable=lambda x: [e.value for e in Semester],
        ),
        nullable=False,
    )
    # Статус проекта
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(
            ProjectStatus,
            native_enum=False,
            values_callable=lambda x: [e.value for e in ProjectStatus],
        ),
        nullable=False,
    )

    # Вехи проекта
    milestones: Mapped[list["MilestoneModel"]] = relationship(
        "MilestoneModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Оценки проекта
    evaluations: Mapped[list["EvaluationModel"]] = relationship(
        "EvaluationModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Связи проекта с командами (многие ко многим)
    project_teams: Mapped[list["ProjectTeamModel"]] = relationship(
        "ProjectTeamModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    # Команды, участвующие в проекте
    teams: Mapped[list["TeamModel"]] = relationship(
        "TeamModel",
        secondary="project_teams",
        back_populates="projects",
        viewonly=True,
    )
    # Заявки на проект
    project_applications: Mapped[list["ProjectApplicationModel"]] = relationship(
        "ProjectApplicationModel",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return f"{self.id}: {self.name} - {self.year} - {self.semester}"
