from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class AuthRefreshToken(BaseModel):
    """Токен обновления авторизации"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    refresh_token: str = Field(..., min_length=1)
    expire_at: datetime
    is_revoked: bool = False

    def is_expired(self) -> bool:
        """Проверить, истёк ли токен"""
        return datetime.now() >= self.expire_at
    
    def revoke(self) -> None:
        """Отозвать токен"""
        self.is_revoked = True