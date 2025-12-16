from uuid import UUID
from typing import List

from app.domain.entities.teams.team import Team
from app.infrastructure.database.repositories.crud_repository import CRUDRepository
from app.infrastructure.database.models.teams.team import TeamModel


class TeamService:
    def __init__(
        self,
        team_repo: CRUDRepository[Team, TeamModel],
    ) -> None:
        self._repo = team_repo

    async def create_team(self, team: Team) -> Team:
        return await self._repo.create(team)

    async def get_team(self, team_id: UUID) -> Team | None:
        return await self._repo.get(team_id)

    async def update_team(self, team: Team) -> Team:
        return await self._repo.update(team)

    async def delete_team(self, team_id: UUID) -> None:
        await self._repo.delete(team_id)

    async def list_teams(self) -> List[Team]:
        return await self._repo.list()