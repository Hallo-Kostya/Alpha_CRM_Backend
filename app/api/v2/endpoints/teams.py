from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from app.application.dto.team import TeamCreate, TeamUpdate, TeamSummary, TeamSummaryResponse
from app.application.dto.team_member import TeamMemberCreate, TeamMemberUpdate
from app.application.services.team_service import (
    TeamService,
    team_service_getter,
)
from app.application.services.team_member_service import (
    TeamMemberService,
    team_member_service_getter,
)
from app.domain.entities.teams.team import Team
from app.domain.entities.teams.team_member import TeamMember


router = APIRouter(
    prefix="/teams",
    tags=["v2", "teams"],
    responses={404: {"description": "Team not found"}},
)


@router.post("/", response_model=Team, summary="Создать команду")
async def create_team(
    data: TeamCreate,
    service: TeamService = Depends(team_service_getter),
):
    """Создать новую команду с именем и опциональной ссылкой на беседу."""
    return await service.create(data)


@router.get("/", response_model=TeamSummaryResponse, summary="Список команд")
async def list_teams(
    project_id: UUID = Query(None, description="ID проекта для фильтрации команд"),
    service: TeamService = Depends(team_service_getter),
):
    """Получить список команд с фильтром по проекту. Включает ID, имя, количество участников и список участников."""
    total, teams = await service.get_teams_summary(project_id)
    return TeamSummaryResponse(total=total, teams=teams)


@router.get("/{team_id}", response_model=Team, summary="Получить команду по ID")
async def get_team(
    team_id: int,
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


@router.post("/{team_id}/students", response_model=TeamMember, summary="Добавить студента в команду")
async def add_student_to_team(
    team_id: int,
    data: TeamMemberCreate,
    team_service: TeamService = Depends(team_service_getter),
    member_service: TeamMemberService = Depends(team_member_service_getter),
):
    """Добавить студента в команду с ролью и группой."""
    # Проверить, что команда существует
    team = await team_service.get_by_id(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return await member_service.add_student_to_team(team_id, data)


@router.get("/{team_id}/students", response_model=list[TeamMember], summary="Получить студентов команды")
async def get_team_students(
    team_id: int,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Получить список студентов команды."""
    return await service.get_team_members(team_id)


@router.patch("/{team_id}/students/{student_id}", response_model=TeamMember, summary="Обновить студента в команде")
async def update_team_member(
    team_id: int,
    student_id: int,
    data: TeamMemberUpdate,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Обновить роль и группу студента в команде."""
    return await service.update_team_member(team_id, student_id, data)


@router.delete("/{team_id}/students/{student_id}", summary="Удалить студента из команды")
async def remove_student_from_team(
    team_id: int,
    student_id: int,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Удалить студента из команды."""
    deleted = await service.remove_student_from_team(team_id, student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    return Response("Студент удален из команды", status.HTTP_200_OK)


@router.patch("/{team_id}", response_model=Team, summary="Обновить команду")
async def update_team(
    team_id: int,
    data: TeamUpdate,
    service: TeamService = Depends(team_service_getter),
):
    """Обновить данные команды: имя, ссылка на беседу."""
    return await service.update(team_id, data)


@router.delete("/{team_id}", summary="Удалить команду")
async def delete_team(
    team_id: int,
    service: TeamService = Depends(team_service_getter),
):
    """Удалить команду."""
    deleted = await service.delete(team_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Команда с ID {team_id} не найдена для удаления",
        )
    return Response(f"successfully deleted team with id {team_id}", status.HTTP_200_OK)