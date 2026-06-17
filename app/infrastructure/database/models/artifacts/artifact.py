from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Index, String, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.models.entity_base import BaseEntity
from app.common.enums import ArtifactType

if TYPE_CHECKING:
    from app.infrastructure.database.models.artifacts.artifact_link import (
        ArtifactLinkModel,
    )


class ArtifactModel(BaseEntity):
    """Модель артефакта"""

    __tablename__ = "artifacts"

    # Название артефакта
    name: Mapped[str] = mapped_column(String(1000), nullable=False)
    # Описание артефакта
    description: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    # Тип артефакта
    type: Mapped[ArtifactType] = mapped_column(
        SQLEnum(
            ArtifactType,
            native_enum=False,
            values_callable=lambda x: [e.value for e in ArtifactType],
        ),
        nullable=False,
    )
    checksum: Mapped[str] = mapped_column(String, index=True, nullable=False)
    size: Mapped[str] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    s3_key: Mapped[str] = mapped_column(String, nullable=False)
    UniqueConstraint("artifact_id", "entity_type", "entity_id", name="uq_artifact_link")
    Index("ix_artifact_entity", "entity_type", "entity_id")
    artifact_links: Mapped[list["ArtifactLinkModel"]] = relationship(
        "ArtifactLinkModel",
        back_populates="artifact",
        cascade="all, delete-orphan",
    )
