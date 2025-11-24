from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from datetime import datetime
from uuid import UUID

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.persons.curator import CuratorModel

class OAuthTokenModel(Base):
    __tablename__ = "oauth_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True)

    curator_id: Mapped[UUID] = mapped_column(
        ForeignKey("curators.id", ondelete="CASCADE"),
        nullable=False
    )

    provider: Mapped[str] = mapped_column(String(32), nullable=False)

    access_token: Mapped[str] = mapped_column(String(1024), nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(String(1024))

    access_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    refresh_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)

    curator : Mapped[CuratorModel] = relationship(
        "CuratorModel",
        back_populates="oauthtokens"
    )