from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from app.api.dependencies import get_current_curator
from app.schemas.team import TeamCreate, TeamUpdate, TeamSummaryResponse
from app.schemas.team_member import TeamMemberCreate, TeamMemberUpdate
from app.services.team_service import (
    TeamService,
    team_service_getter,
)
from app.services.team_member_service import (
    TeamMemberService,
    team_member_service_getter,
)
from app.schemas.team import Team, TeamDetail
from app.schemas.team_member import TeamMember
from app.api.filters import TeamFilter


router = APIRouter(
    prefix="/teams",
    tags=["teams"],
    responses={404: {"description": "Team not found"}},
    dependencies=[Depends(get_current_curator)],
)


@router.post(
    "/",
    response_model=Team,
    summary="Создать команду",
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    data: TeamCreate,
    service: TeamService = Depends(team_service_getter),
):
    """Создать новую команду с именем и опциональной ссылкой на беседу."""
    return await service.create(data)


@router.get("/", response_model=TeamSummaryResponse, summary="Краткий список команд")
async def summarize_teams(
    project_id: UUID = Query(None, description="ID проекта для фильтрации команд"),
    service: TeamService = Depends(team_service_getter),
    filters: TeamFilter = Depends(),
):
    """Получить список команд с фильтром по проекту. Включает ID, имя, количество участников и список участников."""
    return await service.get_teams_summary(
        project_id, **filters.model_dump(exclude_none=True)
    )


@router.get(
    "/detailed_list",
    response_model=list[TeamDetail],
    summary="Детализированный список команд",
)
async def list_teams(
    project_id: UUID = Query(None, description="ID проекта для фильтрации команд"),
    service: TeamService = Depends(team_service_getter),
    filters: TeamFilter = Depends(),
) -> list[TeamDetail]:
    """Получить список команд с фильтром по проекту. Включает ID, имя, количество участников и список участников."""
    return await service.get_list(project_id, **filters.model_dump(exclude_none=True))


@router.get("/{team_id}", response_model=Team, summary="Получить команду по ID")
async def get_team(
    team_id: UUID,
    service: TeamService = Depends(team_service_getter),
):
    """Получить детальную информацию о команде."""
    team = await service.get_by_id(team_id, ["members"])
    if team is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Команда с ID {team_id} не найдена",
        )
    return team


@router.post(
    "/{team_id}/students",
    response_model=TeamMember,
    summary="Добавить студента в команду",
    status_code=status.HTTP_201_CREATED,
)
async def add_student_to_team(
    team_id: UUID,
    data: TeamMemberCreate,
    member_service: TeamMemberService = Depends(team_member_service_getter),
):
    """Добавить студента в команду с указанием роли и группы."""
    return await member_service.add_student_to_team(
        team_id, data.student_id, data.role, data.study_group
    )


@router.patch(
    "/{team_id}/students/{student_id}",
    response_model=TeamMember,
    summary="Обновить студента в команде",
)
async def update_team_member(
    team_id: UUID,
    student_id: UUID,
    data: TeamMemberUpdate,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Обновить роль и группу студента в команде."""
    return await service.update_student_role_and_group(
        team_id, student_id, data.role, data.study_group
    )


@router.delete(
    "/{team_id}/students/{student_id}", summary="Удалить студента из команды"
)
async def remove_student_from_team(
    team_id: UUID,
    student_id: UUID,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Удалить студента из команды."""
    deleted = await service.remove_student_from_team(team_id, student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    return Response("Студент удален из команды", status.HTTP_200_OK)


@router.patch("/{team_id}", response_model=Team, summary="Обновить команду")
async def update_team(
    team_id: UUID,
    data: TeamUpdate,
    service: TeamService = Depends(team_service_getter),
):
    """Обновить данные команды: имя, ссылка на беседу."""
    return await service.update(team_id, data)


@router.delete("/{team_id}", summary="Удалить команду")
async def delete_team(
    team_id: UUID,
    service: TeamService = Depends(team_service_getter),
):
    """Удалить команду."""
    deleted = await service.delete(team_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Команда с ID {team_id} не найдена для удаления",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
