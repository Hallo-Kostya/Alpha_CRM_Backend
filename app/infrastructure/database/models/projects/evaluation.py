from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.entity_base import BaseEntity
from app.domain.enums.evaluation_type import EvaluationType

if TYPE_CHECKING:
    from app.infrastructure.database.models.persons.curator import CuratorModel
    from app.infrastructure.database.models.projects.project import ProjectModel


class EvaluationModel(BaseEntity):
    """Модель оценки проекта куратором"""
    __tablename__ = "evaluations"
    
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    curator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("curators.id", ondelete="CASCADE"),
        primary_key=True,
    )
    type: Mapped[EvaluationType] = mapped_column(
        SQLEnum(EvaluationType, native_enum=False, values_callable=lambda x: [e.value for e in EvaluationType]),
        primary_key=True,
    )
    comment: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    
    __table_args__ = (
        UniqueConstraint("project_id", "curator_id", "type", name="uq_evaluations_project_curator_type"),
    )
    
    # Relationships
    project: Mapped["ProjectModel"] = relationship(
        "ProjectModel",
        back_populates="evaluations",
    )
    
    curator: Mapped["CuratorModel"] = relationship(
        "CuratorModel",
        back_populates="evaluations",
    )

