from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.base import Base
if TYPE_CHECKING:
    from app.infrastructure.database.models.persons.curator import CuratorModel


class CuratorRefreshTokenModel(Base):
    """Модель refresh токенов для кураторов (JWT)"""
    __tablename__ = "curator_refresh_tokens"
    
    # FK на куратора
    curator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("curators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Refresh токен (уникальный)
    refresh_token: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        unique=True,
        index=True,
    )
    
    # Дата истечения токена
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    
    # Флаг отозван ли токен
    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )
    
    # Relationships
    curator: Mapped["CuratorModel"] = relationship(
        "CuratorModel",
        back_populates="refresh_tokens",
    )

