from pydantic import Field
from typing import Optional, TYPE_CHECKING
from app.domain.entities.persons.person import Person
from app.domain.entities.persons.auth_refresh_token import AuthRefreshToken
from app.domain.entities.persons.oauth_token import OAuthToken

if TYPE_CHECKING:
    from app.domain.entities.teams.team import Team


class Curator(Person):
    """Доменная модель куратора"""
    
    outlook: Optional[str] = Field(None, max_length=255)
    password_hash: str = Field(..., min_length=1)
    teams: list['Team'] = Field(default_factory=list)
    auth_tokens: list[AuthRefreshToken] = Field(default_factory=list)
    oauth_tokens: list[OAuthToken] = Field(default_factory=list)