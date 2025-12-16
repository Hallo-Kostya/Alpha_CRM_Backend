from typing import TYPE_CHECKING
from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.entity_base import BaseEntity
from app.domain.enums.artifact_type import ArtifactType

if TYPE_CHECKING:
    from app.infrastructure.database.models.artifacts.artifact_link import ArtifactLinkModel


class ArtifactModel(BaseEntity):
    """Модель артефакта"""
    __tablename__ = "artifacts"
    
    # Название артефакта
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Описание артефакта
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    # Тип артефакта
    type: Mapped[ArtifactType] = mapped_column(
        SQLEnum(ArtifactType, native_enum=False, 
        values_callable=lambda x: [e.value for e in ArtifactType]),
        nullable=False,
    )
    # URL артефакта
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    # Связь с ссылкой на артефакт
    artifact_links: Mapped[list["ArtifactLinkModel"]] = relationship(
        "ArtifactLinkModel",
        back_populates="artifact",
        cascade="all, delete-orphan",
    )

