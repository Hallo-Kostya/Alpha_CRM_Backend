from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.infrastructure.database.models.auth_tokens.base_token import BaseTokenModel


class RefreshTokenModel(BaseTokenModel):
    """Модель авторизационных токенов (авторизационных сессий)"""

    __tablename__ = "auth_sessions"

    curator_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("curators.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

