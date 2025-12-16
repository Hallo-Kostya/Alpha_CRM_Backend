from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.team import TeamCreate, TeamUpdate, TeamRead
from app.application.services.teams_service import TeamService
from app.core.database import db_helper
from app.domain.entities.teams.team import Team
from app.infrastructure.database.models.teams.team import TeamModel
from app.infrastructure.database.repositories.crud_repository import CRUDRepository


router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Team not found"}},
)


async def get_team_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> TeamService:
    """Фабрика TeamService с CRUD-репозиторием."""
    repo = CRUDRepository[Team, TeamModel](
        model=TeamModel,
        domain_model=Team,
        session=session,
    )
    return TeamService(team_repo=repo)


@router.post(
    "/",
    response_model=TeamRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую команду",
)
async def create_team(
    data: TeamCreate,
    service: TeamService = Depends(get_team_service),
) -> Team:
    """Создать команду (на начальном этапе без студентов и кураторов)."""
    team = Team(**data.model_dump(exclude_unset=True))
    return await service.create_team(team)


@router.get("/", response_model=List[TeamRead], summary="Список всех команд")
async def list_teams(
    service: TeamService = Depends(get_team_service),
) -> List[Team]:
    """Получить список всех команд."""
    return await service.list_teams()


@router.get(
    "/{team_id}",
    response_model=TeamRead,
    summary="Получить команду по ID",
)
async def get_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
) -> Team:
    """Получить детальную информацию о команде."""
    team = await service.get_team(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Команда с ID {team_id} не найдена",
        )
    return team


@router.put(
    "/{team_id}",
    response_model=TeamRead,
    summary="Обновить данные команды (частично)",
)
async def update_team(
    team_id: UUID,
    data: TeamUpdate,
    service: TeamService = Depends(get_team_service),
) -> Team:
    """Частичное обновление команды (название, ссылка на чат и т.д.)."""
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не переданы данные для обновления",
        )

    existing = await service.get_team(team_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Команда с ID {team_id} не найдена",
        )

    updated_team = existing.model_copy(update=update_data)
    return await service.update_team(updated_team)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить команду",
)
async def delete_team(
    team_id: UUID,
    service: TeamService = Depends(get_team_service),
) -> None:
    """Удалить команду. Каскадно удалятся связи со студентами, кураторами, встречами, проектами и артефактами."""
    team = await service.get_team(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Команда с ID {team_id} не найдена",
        )
    await service.delete_team(team_id)