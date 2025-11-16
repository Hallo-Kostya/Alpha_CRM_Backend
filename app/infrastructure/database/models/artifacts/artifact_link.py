from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.meetings.meeting import MeetingModel
    from app.infrastructure.database.models.artifacts.artifact import ArtifactModel
    from app.infrastructure.database.models.projects.project import ProjectModel


class ArtifactLinkModel(Base): 
    """Модель связи артефакта с проектом или встречей"""
    __tablename__ = "artifact_links" 
    
    # FK на артефакт
    artifact_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # FK на проект (nullable)
    project_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    # FK на встречу (nullable)
    meeting_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    
    __table_args__ = (
        # Один из FK должен быть заполнен
        CheckConstraint(
            "(project_id IS NOT NULL AND meeting_id IS NULL) OR "
            "(project_id IS NULL AND meeting_id IS NOT NULL)",
            name="ck_artifact_links_one_fk"
        ),
        # Составной PK для связи с проектом
        UniqueConstraint("artifact_id", "project_id", name="uq_artifact_links_artifact_project"),
        # Составной PK для связи со встречей
        UniqueConstraint("artifact_id", "meeting_id", name="uq_artifact_links_artifact_meeting"),
    )
    
    # Связи
    artifact: Mapped["ArtifactModel"] = relationship("ArtifactModel",back_populates="artifact_links",)
    project: Mapped["ProjectModel | None"] = relationship("ProjectModel",foreign_keys=[project_id],back_populates="artifact_links",)
    meeting: Mapped["MeetingModel | None"] = relationship("MeetingModel",foreign_keys=[meeting_id],back_populates="artifact_links",)
