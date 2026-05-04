from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.schemas.project import (
    ProjectSummaryResponse,
    ProjectCreateMinimal,
    ProjectUpdate,
)
from app.schemas.project_team import ProjectTeamCreate
from app.services.projects_service import (
    project_service_getter,
    ProjectService,
)
from app.services.project_team_service import (
    ProjectTeamService,
    project_team_service_getter,
)
from app.common.enums import Semester, ProjectTeamStatus
from app.schemas.project import Project, ProjectRead
from app.schemas.project_team import ProjectTeam
from app.api.filters import ProjectFilter

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Project not found"}},
)


@router.post("/", response_model=Project, summary="Создать новый проект (минимально)")
async def create_project_minimal(
    data: ProjectCreateMinimal,
    service: ProjectService = Depends(project_service_getter),
):
    """Создать проект с базовыми полями. Год, семестр и статус заполняются автоматически по текущей дате, если не указаны."""
    # Авто-заполнение года/семестра
    if data.year is None:
        data.year = datetime.now().year
    if data.semester is None:
        month = datetime.now().month
        data.semester = Semester.SPRING if month < 7 else Semester.AUTUMN

    # статус вычисляется на основе даты, если не передан
    if data.status is None:
        data.status = service.compute_status(data.year, data.semester)
    return await service.create(data)


@router.patch("/{project_id}", response_model=Project, summary="Обновить проект")
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    service: ProjectService = Depends(project_service_getter),
):
    """Обновить поля проекта: описание, цель, требования, критерии оценки."""
    return await service.update(project_id, data)


@router.delete("/{project_id}", summary="Удалить проект")
async def delete_project(
    project_id: UUID,
    service: ProjectService = Depends(project_service_getter),
):
    """
    Удалить проект. Каскадно удалятся вехи, оценки,
    связи с командами и артефакты.
    """
    deleted = await service.delete(project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект с ID {project_id} не найден для удаления",
        )
    return Response(
        f"successfully deleted project with id {project_id}", status.HTTP_200_OK
    )


@router.get(
    "/",
    response_model=ProjectSummaryResponse,
    summary="Сводка проектов для главной страницы",
)
async def get_projects_summary(
    filters: ProjectFilter = Depends(),
    service: ProjectService = Depends(project_service_getter),
):
    """Получить сводку проектов с количеством команд и участников, с фильтрами по году, семестру и команде."""
    return await service.get_projects_summary(**filters.model_dump(exclude_none=True))


@router.get("/{project_id}", response_model=Project, summary="Получить проект по ID")
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(project_service_getter),
):
    """Получить детальную информацию о проекте."""
    project = await service.get_by_id(
        project_id,
        ["project_teams", "project_teams.team", "project_teams.team.members"],
    )
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект с ID {project_id} не найден",
        )
    return project


@router.get(
    "/{team_id}/available_projects",
    response_model=list[ProjectRead],
    summary="Получить доступные для записи проекты для команды",
)
async def get_available_projects(
    team_id: UUID,
    project_team_service: ProjectTeamService = Depends(project_team_service_getter),
    project_service: ProjectService = Depends(project_service_getter),
):
    unavailable_projects = await project_team_service.get_team_projects(
        team_id, ProjectTeamStatus.PENDING
    )
    unavailable_ids = [project_team.project_id for project_team in unavailable_projects]
    available_projects = await project_service.get_projects_with_excluded_ids(
        unavailable_ids
    )
    return available_projects


@router.get(
    "/{team_id}/project_teams",
    response_model=list[ProjectTeam],
    summary="Получить отправленные заявки на проект для команды",
)
async def get_team_projects(
    team_id: UUID,
    status: ProjectTeamStatus,
    project_team_service: ProjectTeamService = Depends(project_team_service_getter),
):
    result = await project_team_service.get_team_projects(team_id, status, ["members"])
    return result


@router.post(
    "/{project_id}/teams",
    response_model=ProjectTeam,
    summary="Добавить команду к проекту",
)
async def assign_team_to_project(
    project_id: UUID,
    data: ProjectTeamCreate,
    project_service: ProjectService = Depends(project_service_getter),
    team_service: ProjectTeamService = Depends(project_team_service_getter),
):
    """Добавить команду к проекту."""
    # Проверить, что проект существует
    project = await project_service.get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return await team_service.assign_team_to_project(project_id, data)


@router.delete("/{project_id}/teams/{team_id}", summary="Удалить команду из проекта")
async def remove_team_from_project(
    project_id: UUID,
    team_id: UUID,
    service: ProjectTeamService = Depends(project_team_service_getter),
):
    """Удалить команду из проекта."""
    deleted = await service.delete_team_from_project(project_id, team_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
