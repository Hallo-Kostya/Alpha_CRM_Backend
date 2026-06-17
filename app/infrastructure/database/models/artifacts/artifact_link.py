from typing import TYPE_CHECKING
import uuid
from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.meetings.meeting import MeetingModel
    from app.infrastructure.database.models.artifacts.artifact import ArtifactModel
    from app.infrastructure.database.models.projects.project import ProjectModel


class ArtifactLinkModel(Base):
    __tablename__ = "artifact_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    artifact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    entity_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        UniqueConstraint(
            "artifact_id",
            "entity_type",
            "entity_id",
            name="uq_artifact_link_unique",
        ),
    )

    artifact: Mapped["ArtifactModel"] = relationship(
        "ArtifactModel",
        back_populates="artifact_links",
    )