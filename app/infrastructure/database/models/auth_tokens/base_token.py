from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.entity_base import BaseEntity


class BaseTokenModel(BaseEntity):
    """Модель авторизационных токенов (авторизационных сессий)"""

    __abstract__ = True

    curator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("curators.id", ondelete="CASCADE"),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
