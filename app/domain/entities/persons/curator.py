from datetime import datetime
from uuid import UUID
from app.domain.entities import Person
from app.domain.entities.persons.refresh_token import OAuthToken

class Curator(Person):
    def __init__(self, first_name: str, last_name: str, email: str | None , 
                 tg_link: str | None, patronymic: str | None , id: UUID | None,
                 outlook: str | None, oauth_tokens: dict[str, OAuthToken] | None = None):
        super().__init__(first_name, last_name, email, tg_link, patronymic, id)
        self.outlook = outlook
        self.oauth_tokens = oauth_tokens or {}

    def full_name(self) -> str:
        if self.patronymic:
            return f"{self.first_name} {self.last_name} {self.patronymic}"
        return f"{self.first_name} {self.last_name}"
    
    def get_token(self, provider: str) -> OAuthToken | None:
        return self.oauth_tokens.get(provider)

    def add_token(self, token: OAuthToken):
        self.oauth_tokens[token.provider] = token