from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime


class AuthToken(BaseModel):
    """Токен обновления авторизации"""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )

    curator_id: uuid.UUID
    token: str = Field(..., min_length=1)
    expires_at: datetime
    is_revoked: bool = False

    def is_expired(self) -> bool:
        """Проверить, истёк ли токен"""
        return datetime.now() >= self.expires_at

    def revoke(self) -> None:
        """Отозвать токен"""
        self.is_revoked = True
