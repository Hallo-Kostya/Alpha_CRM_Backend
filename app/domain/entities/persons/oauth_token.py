from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class OAuthToken(BaseModel):
    """OAuth токен для внешних провайдеров"""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    
    provider: str = Field(..., min_length=1, max_length=50)
    access_token: str = Field(..., min_length=1)
    access_expires_at: datetime
    refresh_token: Optional[str] = None
    refresh_expires_at: Optional[datetime] = None
    is_revoked: bool = False

    def is_access_expired(self) -> bool:
        """Проверить, истёк ли access токен"""
        return datetime.now() >= self.access_expires_at

    def is_refresh_expired(self) -> bool:
        """Проверить, истёк ли refresh токен"""
        if self.refresh_expires_at is None:
            return False
        return datetime.now() >= self.refresh_expires_at

    def revoke(self) -> None:
        """Отозвать токен"""
        self.is_revoked = True