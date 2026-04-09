from typing import List
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from app.application.dto.project import ProjectSummaryResponse, ProjectCreateMinimal, ProjectUpdate
from app.application.dto.project_team import ProjectTeamCreate
from app.application.services.projects_service import (
    project_service_getter,
    ProjectService,
)
from app.application.services.project_team_service import (
    ProjectTeamService,
    project_team_service_getter,
)
from app.domain.enums.semester import Semester
from app.domain.entities.projects.project import Project
from app.domain.entities.projects.project_team import ProjectTeam


router = APIRouter(
    prefix="/projects",
    tags=["v2", "projects"],
    responses={404: {"description": "Project not found"}},
)

@router.get("/summary", response_model=ProjectSummaryResponse, summary="Сводка проектов для главной страницы")
async def get_projects_summary(
    year: int = Query(None, description="Год проекта"),
    semester: Semester = Query(None, description="Семестр проекта"),
    service: ProjectService = Depends(project_service_getter),
):
    """Получить сводку проектов с количеством команд и участников, с фильтрами по году и семестру."""
    total, items = await service.get_projects_summary(year, semester)
    return ProjectSummaryResponse(total=total, projects=items)


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


@router.get("/{project_id}", response_model=Project, summary="Получить проект по ID")
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(project_service_getter),
):
    """Получить детальную информацию о проекте."""
    project = await service.get_by_id(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект с ID {project_id} не найден",
        )
    return project


@router.post("/{project_id}/teams", response_model=ProjectTeam, summary="Добавить команду к проекту")
async def assign_team_to_project(
    project_id: int,
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


@router.get("/{project_id}/teams", response_model=list[ProjectTeam], summary="Получить команды проекта")
async def get_project_teams(
    project_id: int,
    service: ProjectTeamService = Depends(project_team_service_getter),
):
    """Получить список команд проекта."""
    return await service.get_project_teams(project_id)


@router.delete("/{project_id}/teams/{team_id}", summary="Удалить команду из проекта")
async def remove_team_from_project(
    project_id: int,
    team_id: int,
    service: ProjectTeamService = Depends(project_team_service_getter),
):
    """Удалить команду из проекта."""
    deleted = await service.remove_team_from_project(project_id, team_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Связь не найдена")
    return Response("Команда удалена из проекта", status.HTTP_200_OK)


@router.patch("/{project_id}", response_model=Project, summary="Обновить проект")
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    service: ProjectService = Depends(project_service_getter),
):
    """Обновить поля проекта: описание, цель, требования, критерии оценки."""
    return await service.update(project_id, data)


@router.delete("/{project_id}", summary="Удалить проект")
async def delete_project(
    project_id: int,
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
    return Response(f"successfully deleted project with id {project_id}", status.HTTP_200_OK)


