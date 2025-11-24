from datetime import datetime

class AuthRefreshToken:
    def __init__(self, refresh_token: str, expire_at: datetime, is_revoked: bool) -> None:
        self.refresh_token = refresh_token
        self.expire_at = expire_at
        self.is_revoked = is_revoked

    def is_expired(self) -> bool:
        return datetime.now() >= self.expire_at
    
    def revoke(self):
        self.is_revoked = True