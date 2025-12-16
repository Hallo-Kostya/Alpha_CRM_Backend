from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.team import TeamCreate, TeamUpdate
from app.application.services.teams_service import TeamService
from app.core.database import db_helper
from app.domain.entities.teams.team import Team
from app.infrastructure.database.models.teams.team import TeamModel
from app.infrastructure.database.repositories.crud_repository import CRUDRepository


router = APIRouter(prefix="/teams", tags=["teams"])


async def get_team_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> TeamService:
    repo = CRUDRepository[Team, TeamModel](
        model=TeamModel,
        domain_model=Team,
        session=session,
    )
    return TeamService(repo)


@router.post("/", response_model=Team, status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    service: TeamService = Depends(get_team_service),
) -> Team:
    team = Team(**data.model_dump(exclude_unset=True))
    return await service.create_team(team)


@router.get("/", response_model=List[Team])
async def list_teams(
    service: TeamService = Depends(get_team_service),
) -> List[Team]:
    return await service.list_teams()


@router.get("/{team_id}", response_model=Team)
async def get_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
) -> Team:
    team = await service.get_team(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.put("/{team_id}", response_model=Team)
async def update_team(
    team_id: UUID,
    data: TeamUpdate,
    service: TeamService = Depends(get_team_service),
) -> Team:
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    existing = await service.get_team(team_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Team not found")

    updated_team = existing.model_copy(update=update_data)
    return await service.update_team(updated_team)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
) -> None:
    await service.delete_team(team_id)