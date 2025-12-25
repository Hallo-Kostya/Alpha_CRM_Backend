from pydantic import Field
from typing import Optional, TYPE_CHECKING
from app.domain.entities.persons.person import Person
from app.domain.entities.auth_tokens.auth_token import AuthToken

from app.domain.entities.teams.team import Team


class Curator(Person):
    """Доменная модель куратора"""
    hashed_password: str = Field(..., min_length=1)
    teams: list[Team] = Field(default_factory=list)
