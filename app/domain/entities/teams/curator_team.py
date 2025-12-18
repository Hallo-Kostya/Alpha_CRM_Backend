from pydantic import BaseModel
from uuid import UUID

from app.domain.entities.persons.curator import Curator
from app.domain.entities.teams.team import Team


class CuratorTeam(BaseModel):
    team_id: UUID
    curator_id: UUID

    team: Team
    curator: Curator