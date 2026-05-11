from typing import Optional
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from app.api.dependencies import get_current_curator
from app.schemas.project import ProjectCreate, ProjectSummaryResponse, ProjectCreateMinimal, ProjectUpdate
from app.schemas.project_team import ProjectTeamCreate
from app.services.projects_service import (
    project_service_getter,
    ProjectService,
)
from app.services.project_team_service import (
    ProjectTeamService,
    project_team_service_getter,
)
from app.common.enums import Semester
from app.schemas.project import Project
from app.schemas.project_team import ProjectTeam


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Project not found"}},
    dependencies=[Depends(get_current_curator)],
)

@router.post(
    "/", 
    response_model=Project, 
    summary="Создать новый проект", 
    status_code=status.HTTP_201_CREATED,
)
async def create_project_minimal(
    data: ProjectCreate,
    service: ProjectService = Depends(project_service_getter),
):
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
    return Response(f"successfully deleted project with id {project_id}", status.HTTP_200_OK)


@router.get("/", response_model=ProjectSummaryResponse, summary="Сводка проектов для главной страницы")
async def get_projects_summary(
    year: Optional[int] = Query(None, description="Год проекта"),
    semester: Optional[Semester] = Query(None, description="Семестр проекта"),
    team_id: Optional[UUID] = Query(None, description="ID команды для фильтрации проектов"),
    service: ProjectService = Depends(project_service_getter),
):
    """Получить сводку проектов с количеством команд и участников, с фильтрами по году, семестру и команде."""
    return await service.get_projects_summary(year, semester, team_id)


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


@router.post("/{project_id}/teams", response_model=ProjectTeam, summary="Добавить команду к проекту", status_code=status.HTTP_201_CREATED)
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


@router.delete("/{project_id}/teams/{team_id}", summary="Удалить команду из проекта", status_code=status.HTTP_204_NO_CONTENT)
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


