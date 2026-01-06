from pydantic import Field
from app.domain.entities.persons.person import Person

from app.domain.entities.teams.team import Team


class Curator(Person):
    """Доменная модель куратора"""
    avatar_s3_path: str | None = Field(None, min_length=1, max_length=255)
    teams: list[Team] = Field(default_factory=list)
