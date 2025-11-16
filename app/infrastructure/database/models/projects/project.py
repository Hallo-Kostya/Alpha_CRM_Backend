from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base
from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.semester import Semester

if TYPE_CHECKING:
    from app.infrastructure.database.models.artifacts.artifact_link import ArtifactLinkModel
    from app.infrastructure.database.models.projects.evaluation import EvaluationModel
    from app.infrastructure.database.models.projects.milestone import MilestoneModel
    from app.infrastructure.database.models.projects.project_team import ProjectTeamModel
    from app.infrastructure.database.models.teams.team import TeamModel


class ProjectModel(Base):
    """Модель проекта"""
    __tablename__ = "projects"
    
    # Название проекта
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Описание проекта
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    # Цель проекта
    goal: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # Требования к проекту
    requirements: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    # Критерии оценки проекта
    eval_criteria: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # Год проведения проекта
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    # Семестр
    semester: Mapped[Semester] = mapped_column(
        SQLEnum(Semester, native_enum=False, values_callable=lambda x: [e.value for e in Semester]),
        nullable=False,
    )
    # Статус проекта
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus, native_enum=False, values_callable=lambda x: [e.value for e in ProjectStatus]),
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
    
    # Артефакты проекта
    artifact_links: Mapped[list["ArtifactLinkModel"]] = relationship(
        "ArtifactLinkModel",
        foreign_keys="ArtifactLinkModel.project_id",
        back_populates="project",
        cascade="all, delete-orphan",
    )

