from pydantic import BaseModel, ConfigDict
from app.domain.entities.auth_tokens.auth_token import AuthToken


class OAuthTokens(BaseModel):
    """OAuth токен для внешних провайдеров"""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True
    )
    access_token: AuthToken
    refresh_token: AuthToken
