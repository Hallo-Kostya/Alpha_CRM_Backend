from uuid import UUID
from fastapi import Depends
from app.schemas.team import (
    TeamCreate,
    TeamUpdate,
    TeamSummary,
    TeamMemberSummary,
    TeamSummaryResponse,
)
from app.schemas.team import Team, TeamDetail
from app.infrastructure.database.models import TeamModel
from app.infrastructure.database.repositories.team_repository import (
    TeamRepository,
    team_repository_getter,
)


class TeamService:
    """Application service for teams."""

    def __init__(self, team_repo: TeamRepository):
        self._repo = team_repo

    def _to_orm(self, scheme: TeamCreate) -> TeamModel:
        """Convert schema to ORM model."""
        return TeamModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: TeamModel) -> Team:
        """Convert ORM model to schema."""
        return Team.model_validate(orm_model, from_attributes=True)

    async def create(self, team: TeamCreate) -> Team:
        """Create new team."""
        orm_obj = self._to_orm(team)
        created_obj = await self._repo.create(orm_obj)
        return Team(id=created_obj.id, name=created_obj.name, members=[], group_link=created_obj.group_link)

    async def update(self, team_id: UUID, new_data: TeamUpdate) -> Team | None:
        """Update team."""
        old_obj = await self._repo.get_by_id(team_id)
        if not old_obj:
            return None
        updated_orm = await self._repo.update(
            old_obj, new_data.model_dump(exclude_unset=True)
        )
        return self._to_schema(updated_orm)

    async def delete(self, team_id: UUID) -> bool:
        """Delete team."""
        obj = await self._repo.get_by_id(team_id)
        if not obj:
            return False
        await self._repo.delete(obj)
        return True

    async def get_by_id(
        self, team_id: UUID, eager_loads: list[str] | None = None
    ) -> Team | None:
        """Get team by ID."""
        obj = await self._repo.get_by_id(team_id, eager_loads)
        if not obj:
            return None
        return self._to_schema(obj)
    
    async def get_list(self, project_id=None, **filters) -> list[TeamDetail]:
        if project_id:
            filters["project_id"] = project_id
        _, objs = await self._repo.get_list(filters, eager_loads=["members", "members.student"])
        return [TeamDetail.model_validate(obj, from_attributes=True) for obj in objs]

    async def get_teams_summary(
        self, project_id=None, **filters
    ) -> TeamSummaryResponse:
        """Get teams summary with members as Pydantic models."""
        raw_teams = await self._repo.get_teams_summary(project_id, **filters)

        teams = []
        for raw_team in raw_teams:
            members = [
                TeamMemberSummary(id=UUID(member["id"]), full_name=member["full_name"])
                for member in raw_team["members"]
            ]

            team_summary = TeamSummary(
                id=UUID(raw_team["id"]),
                name=raw_team["name"],
                members_count=raw_team["members_count"],
                members=members,
            )
            teams.append(team_summary)

        return TeamSummaryResponse(total=len(teams), teams=teams)


def team_service_getter(
    repository: TeamRepository = Depends(team_repository_getter),
):
    return TeamService(repository)
