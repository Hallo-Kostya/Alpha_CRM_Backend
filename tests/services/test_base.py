import pytest
from uuid import uuid4
from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.application.services.base_service import BaseService
from app.infrastructure.database.models.teams.team import TeamModel
from app.domain.entities.teams.team import Team
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_team_service_crud_with_domain(session: AsyncSession):
    # Репозиторий
    repo = BaseRepository(TeamModel, session)

    # Сервис
    service = BaseService[TeamModel, Team](repo)
    service.orm_model = TeamModel
    service.pyd_scheme = Team

    # --- CREATE ---
    team_data = Team(
        id=uuid4(),
        name="Team Beta",
        group_link="https://t.me/team_beta"
    )
    orm_obj = service._to_orm(team_data)
    created = await repo.create(orm_obj)

    assert created.id == orm_obj.id
    assert created.name == "Team Beta"
    assert created.group_link == "https://t.me/team_beta"

    fetched = await service.get_by_id(created.id)
    assert fetched is not None
    assert fetched.name == "Team Beta"

    teams = await service.get_list(name="Team Beta")
    assert len(teams) == 1
    assert teams[0].group_link == "https://t.me/team_beta"

    deleted = await service.delete(created.id)
    assert deleted is True

    fetched_none = await service.get_by_id(created.id)
    assert fetched_none is None
