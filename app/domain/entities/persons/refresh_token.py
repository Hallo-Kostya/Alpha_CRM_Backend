from datetime import datetime

class OAuthToken:
    def __init__(
        self,
        provider: str,
        access_token: str,
        access_expires_at: datetime,
        refresh_token: str | None = None,
        refresh_expires_at: datetime | None = None,
        is_revoked: bool = False
    ):
        self.provider = provider
        self.access_token = access_token
        self.access_expires_at = access_expires_at
        self.refresh_token = refresh_token
        self.refresh_expires_at = refresh_expires_at
        self.is_revoked = is_revoked

    def is_access_expired(self) -> bool:
        return datetime.now() >= self.access_expires_at

    def is_refresh_expired(self) -> bool:
        if self.refresh_expires_at is None:
            return False
        return datetime.now() >= self.refresh_expires_at

    def revoke(self):
        self.is_revoked = True
