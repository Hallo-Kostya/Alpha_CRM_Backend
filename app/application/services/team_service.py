from uuid import UUID
from fastapi import Depends
from app.application.services.base_service import BaseService
from app.application.dto.team import TeamCreate, TeamUpdate
from app.domain.entities.teams.team import Team
from app.infrastructure.database.models import TeamModel
from app.infrastructure.database.repositories.team_repository import (
    TeamRepository,
    team_repository_getter,
)


class TeamService(BaseService[TeamModel, Team]):
    orm_model = TeamModel
    pyd_scheme = Team

    def __init__(
        self,
        team_repo: TeamRepository,
    ):
        super().__init__(team_repo)

    async def create(self, team: TeamCreate) -> Team:
        orm_obj = self._to_orm(team)
        created_obj = await self._repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def update(self, new_data: TeamUpdate, team_id: UUID) -> Team | None:
        old_obj = await self._repo.get_by_id(team_id)
        if not old_obj:
            return None
        updated_orm = await self._repo.update(
            old_obj, new_data.model_dump(exclude_unset=True)
        )
        return self._to_schema(updated_orm)


def team_service_getter(
    repository: TeamRepository = Depends(team_repository_getter),
):
    return TeamService(repository)
