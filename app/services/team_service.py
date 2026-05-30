from uuid import UUID
from fastapi import Depends, HTTPException, status
from app.common.enums import ProjectTeamStatus
from app.schemas.team import (
    CuratorShort,
    TeamCreate,
    TeamUpdate,
    TeamSummary,
    TeamMemberSummary,
    TeamSummaryResponse,
)
from app.schemas.team import Team, TeamDetail
from app.infrastructure.database.models import TeamModel, CuratorModel
from app.infrastructure.database.repositories.team_repository import (
    TeamRepository,
    team_repository_getter,
)
from app.infrastructure.database.repositories.curator_repository import (
    CuratorRepository,
    curator_repository_getter,
)
from app.infrastructure.database.repositories.curator_team_repository import (
    CuratorTeamRepository,
    curator_team_repository_getter,
)


class TeamService:
    """Application service for teams."""

    def __init__(
        self,
        team_repo: TeamRepository,
        curator_repo: CuratorRepository,
        curator_team_repo: CuratorTeamRepository,
    ):
        self._repo = team_repo
        self._curator_repo = curator_repo
        self._curator_team_repo = curator_team_repo

    def _to_orm(self, scheme: TeamCreate) -> TeamModel:
        """Convert schema to ORM model."""
        data = scheme.model_dump(exclude_unset=True, exclude={"curator_id"})
        return TeamModel(**data)

    def _to_schema(self, orm_model: TeamModel) -> Team:
        """Convert ORM model to schema."""
        return Team.model_validate(orm_model, from_attributes=True)

    async def _validate_curator_exists(self, curator_id: UUID) -> CuratorModel:
        """Проверить существование куратора."""
        curator = await self._curator_repo.get_by_id(curator_id)
        if not curator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Куратор с ID {curator_id} не найден",
            )
        return curator

    async def create(self, team: TeamCreate) -> Team:
        """Create new team, optionally attaching a curator."""
        orm_obj = self._to_orm(team)
        created_obj = await self._repo.create(orm_obj)

        # Привязываем куратора при создании, если передан
        if team.curator_id:
            await self._validate_curator_exists(team.curator_id)
            await self._curator_team_repo.add(team.curator_id, created_obj.id)

        # Перезагружаем объект с кураторами
        created_obj = await self._repo.get_by_id(created_obj.id, eager_loads=["curators"])
        return self._to_schema(created_obj)

    async def update(self, team_id: UUID, new_data: TeamUpdate) -> Team | None:
        """Update team."""
        old_obj = await self._repo.get_by_id(team_id, eager_loads=["curators"])
        if not old_obj:
            return None
        updated_orm = await self._repo.update(
            old_obj, new_data.model_dump(exclude_unset=True)
        )
        updated_orm = await self._repo.get_by_id(team_id, eager_loads=["curators"])
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
        loads = list(eager_loads or [])
        if "curators" not in loads:
            loads.append("curators")
        obj = await self._repo.get_by_id(team_id, loads)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_list(self, project_id=None, **filters) -> list[TeamDetail]:
        if project_id:
            filters["project_id"] = project_id
        _, objs = await self._repo.get_list(
            filters, eager_loads=["members", "members.student", "curators"]
        )
        return [TeamDetail.model_validate(obj, from_attributes=True) for obj in objs]

    async def get_teams_summary(
        self, status: list[ProjectTeamStatus] | None = None, project_id=None, **filters
    ) -> TeamSummaryResponse:
        """Get teams summary with members as Pydantic models."""
        raw_teams = await self._repo.get_teams_summary(project_id, status, **filters)

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

    async def add_curator(self, team_id: UUID, curator_id: UUID) -> Team:
        """Привязать куратора к команде."""
        # Проверяем существование команды
        team = await self._repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Команда с ID {team_id} не найдена",
            )
        # Проверяем существование куратора
        await self._validate_curator_exists(curator_id)

        # Проверяем, не привязан ли уже куратор
        already_linked = await self._curator_team_repo.exists(curator_id, team_id)
        if already_linked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Куратор уже привязан к этой команде",
            )

        await self._curator_team_repo.add(curator_id, team_id)

        updated = await self._repo.get_by_id(team_id, ["members", "curators"])
        return self._to_schema(updated)

    async def remove_curator(self, team_id: UUID, curator_id: UUID) -> Team:
        """Отвязать куратора от команды."""
        team = await self._repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Команда с ID {team_id} не найдена",
            )

        removed = await self._curator_team_repo.remove(curator_id, team_id)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь куратора с командой не найдена",
            )

        updated = await self._repo.get_by_id(team_id, ["members", "curators"])
        return self._to_schema(updated)


def team_service_getter(
    repository: TeamRepository = Depends(team_repository_getter),
    curator_repo: CuratorRepository = Depends(curator_repository_getter),
    curator_team_repo: CuratorTeamRepository = Depends(curator_team_repository_getter),
) -> TeamService:
    return TeamService(repository, curator_repo, curator_team_repo)