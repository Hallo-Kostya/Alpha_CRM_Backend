from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.models.auth_tokens.base_token import BaseTokenModel


class OAuthTokenModel(BaseTokenModel):
    """Модель авторизационных токенов oauth2 для юзера"""

    __tablename__ = "oauth_sessions"

    access_token: Mapped[str] = mapped_column(String(255), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=False)

    provider: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint('curator_id', 'provider', name='curator_provider_uc'),
    )
