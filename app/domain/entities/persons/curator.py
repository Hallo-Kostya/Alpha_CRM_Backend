from datetime import datetime
from uuid import UUID
from app.domain.entities import Person
from app.domain.entities.persons.auth_refresh_token import AuthRefreshToken
from app.domain.entities.persons.oauth_token import OAuthToken
from app.domain.entities.teams.team import Team

class Curator(Person):
    def __init__(self, first_name: str, last_name: str, email: str | None , 
                 tg_link: str | None, patronymic: str | None , id: UUID | None,
                 outlook: str | None, password_hash: str, teams: list[Team] | None,
                 auth_tokens: list[AuthRefreshToken] | None, oauth_tokens: list[OAuthToken] | None ):
        super().__init__(first_name, last_name, email, tg_link, patronymic, id)
        self.outlook = outlook
        self.password_hash = password_hash
        self.teams = teams
        self.auth_tokens = auth_tokens
        self.oauth_tokens = oauth_tokens

    def full_name(self) -> str:
        if self.patronymic:
            return f"{self.first_name} {self.last_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"
    
