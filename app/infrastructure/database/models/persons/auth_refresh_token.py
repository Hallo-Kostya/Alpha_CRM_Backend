from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.persons.curator import CuratorModel


class AuthRefreshTokenModel(Base):
    __tablename__ = "auth_refresh_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    # Кто владелец токена
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("curators.id", ondelete="CASCADE"),
        nullable=False
    )

    refresh_token: Mapped[str] = mapped_column(String(1024), nullable=False)
    access_token: Mapped[str | None] = mapped_column(String(1024))

    # Сроки истечения
    access_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    refresh_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # Если человек разлогинился или админ дал пинка
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    # Чтобы ORM могла ходить обратно
    curator: Mapped["CuratorModel"] = relationship(
        "CuratorModel",
        back_populates="auth_tokens"
    )
