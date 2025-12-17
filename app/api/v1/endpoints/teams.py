from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.application.dto.team import TeamCreate, TeamUpdate
from app.application.dto.team_member import TeamMemberCreate, TeamMemberUpdate
from app.application.services.team_member_service import TeamMemberService, team_member_service_getter
from app.application.services.team_service import TeamService, team_service_getter
from app.domain.entities.teams.team import Team
from app.domain.entities.teams.team_member import TeamMember

router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Team not found"}},
)


@router.post(
    "/",
    response_model=Team,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую команду",
)
async def create_team(
    data: TeamCreate,
    service: TeamService = Depends(team_service_getter),
):
    """Создать команду (на начальном этапе без студентов и кураторов)."""
    return await service.create(data)


@router.get("/", response_model=List[Team], summary="Список всех команд")
async def list_teams(
    service: TeamService = Depends(team_service_getter),
):
    """Получить список всех команд."""
    return await service.get_list()


@router.get(
    "/{team_id}",
    response_model=Team,
    summary="Получить команду по ID",
)
async def get_team(
    team_id: UUID,
    service: TeamService = Depends(team_service_getter),
):
    """Получить детальную информацию о команде."""
    team = await service.get_by_id(team_id)
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Команда с ID {team_id} не найдена",
        )
    return team


@router.patch(
    "/{team_id}",
    response_model=Team,
    summary="Обновить данные команды (частично)",
)
async def update_team(
    team_id: UUID,
    data: TeamUpdate,
    service: TeamService = Depends(team_service_getter),
):
    """Частичное обновление команды (название, ссылка на чат и т.д.)."""
    updated_data = await service.update(data, team_id)
    if not updated_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Команда с ID {team_id} не найдена для обновления",
        )
    return updated_data


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить команду",
)
async def delete_team(
    team_id: UUID,
    service: TeamService = Depends(team_service_getter),
):
    """Удалить команду. Каскадно удалятся связи со студентами, кураторами, встречами, проектами и артефактами."""
    deleted = await service.delete(team_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Команда с ID {team_id} не найдена для удаления",
        )
    return Response(f"Successfully deleted team with id {team_id}", 200)


@router.post(
    "/{team_id}/students",
    response_model=TeamMember,  # Используем доменную сущность
    status_code=status.HTTP_201_CREATED,
    summary="Добавить студента в команду",
)
async def add_student_to_team(
    team_id: UUID,
    data: TeamMemberCreate,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Добавить студента в команду с указанием роли и учебной группы."""
    return await service.add_student_to_team(team_id, data)


@router.get(
    "/{team_id}/students",
    response_model=List[TeamMember],  # Используем доменную сущность
    summary="Получить всех студентов команды",
)
async def get_team_students(
    team_id: UUID,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Получить список всех студентов, состоящих в команде."""
    return await service.get_team_members(team_id)


@router.patch(
    "/{team_id}/students/{student_id}",
    response_model=TeamMember,  # Используем доменную сущность
    summary="Обновить данные студента в команде",
)
async def update_team_member(
    team_id: UUID,
    student_id: UUID,
    data: TeamMemberUpdate,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Обновить роль или учебную группу студента в команде."""
    return await service.update_team_member(team_id, student_id, data)


@router.delete(
    "/{team_id}/students/{student_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить студента из команды",
)
async def remove_student_from_team(
    team_id: UUID,
    student_id: UUID,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Удалить студента из команды."""
    deleted = await service.remove_student_from_team(team_id, student_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь между командой и студентом не найдена"
        )
    return Response(f"Successfully removed student {student_id} from team {team_id}", 200)