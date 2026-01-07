import pytest
from uuid import UUID

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.teams.team import TeamModel


@pytest.mark.asyncio
async def test_create_team(session):
    repo = BaseRepository(TeamModel, session)
    team = TeamModel(name="Test Team", group_link=None)
    created = await repo.create(team)
    assert isinstance(created.id, UUID)
    assert created.name == "Test Team"


@pytest.mark.asyncio
async def test_get_by_id(session):
    repo = BaseRepository(TeamModel, session)
    team = await repo.create(TeamModel(name="Team A"))
    fetched = await repo.get_by_id(team.id)
    assert fetched is not None
    assert fetched.id == team.id
    assert fetched.name == "Team A"


@pytest.mark.asyncio
async def test_get_list_with_filter(session):
    repo = BaseRepository(TeamModel, session)
    await repo.create(TeamModel(name="Team 1"))
    await repo.create(TeamModel(name="Team 2"))
    teams = await repo.get_list(name="Team 1")
    assert len(teams) == 1
    assert teams[0].name == "Team 1"


@pytest.mark.asyncio
async def test_update(session):
    repo = BaseRepository(TeamModel, session)
    team = await repo.create(TeamModel(name="Old Name"))
    updated = await repo.update(team, {"name": "New Name"})
    assert updated.name == "New Name"


@pytest.mark.asyncio
async def test_delete(session):
    repo = BaseRepository(TeamModel, session)
    team = await repo.create(TeamModel(name="To Delete"))
    await repo.delete(team)
    deleted = await repo.get_by_id(team.id)
    assert deleted is None
