from uuid import UUID
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.application.dto.project import (
    ProjectCreate,
    ProjectUpdate,
)
from app.application.dto.project_team import ProjectTeamCreate, ProjectTeamUpdate, ProjectTeamWithInfo
from app.application.services.project_team_service import ProjectTeamService, project_team_service_getter
from app.application.services.projects_service import (
    project_service_getter,
    ProjectService,
)
from app.domain.entities.projects.project import Project
from app.domain.entities.projects.project_team import ProjectTeam
from app.api.utils.auth import validate_curator


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Project not found"}},
)


@router.post(
    "/",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый проект",
)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(project_service_getter),
    curator_id: uuid.UUID = Depends(validate_curator)
):
    """Создать проект (на этапе планирования, без команд)."""
    return await service.create(data)


@router.get("/", response_model=List[Project], summary="Список всех проектов")
async def list_projects(
    service: ProjectService = Depends(project_service_getter),
):
    """Получить список всех проектов (с фильтрами можно расширить позже)."""
    return await service.get_list()


@router.get(
    "/{project_id}",
    response_model=Project,
    summary="Получить проект по ID",
)
async def get_project(
    project_id: UUID, service: ProjectService = Depends(project_service_getter)
):
    """Получить детальную информацию о проекте."""
    project = await service.get_by_id(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект с ID {project_id} не найден",
        )
    return project


@router.patch(
    "/{project_id}",
    response_model=Project,
    summary="Обновить проект (частично)",
)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    service: ProjectService = Depends(project_service_getter),
    credentials: tuple[uuid.UUID, str] = Depends(validate_curator)
):
    """Частичное обновление данных проекта."""
    updated_obj = await service.update(data, project_id)
    if not updated_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект с ID {project_id} не найден для обновления",
        )
    return updated_obj


@router.delete(
    "/{project_id}",
    summary="Удалить проект",
)
async def delete_project(
    project_id: UUID,
    service: ProjectService = Depends(project_service_getter),
    credentials: tuple[uuid.UUID, str] = Depends(validate_curator)
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
    return Response(f"successfully deleted project with id {project_id}", 200)


@router.post(
    "/{project_id}/teams",
    response_model=ProjectTeam,
    status_code=status.HTTP_201_CREATED,
    summary="Назначить команду на проект",
)
async def assign_team_to_project(
    project_id: UUID,
    data: ProjectTeamCreate,
    service: ProjectTeamService = Depends(project_team_service_getter),
    credentials: tuple[uuid.UUID, str] = Depends(validate_curator)
):
    """
    Назначить команду на проект.
    
    Ограничения:
    - Команда не может участвовать в двух проектах в одном семестре
    - Команда не может быть назначена на один проект дважды
    """
    return await service.assign_team_to_project(project_id, data)

@router.get(
    "/{project_id}/teams",
    response_model=List[ProjectTeam],
    summary="Получить все команды проекта",
)
async def get_project_teams(
    project_id: UUID,
    service: ProjectTeamService = Depends(project_team_service_getter),
):
    """Получить список всех команд, назначенных на проект."""
    return await service.get_project_teams(project_id)

@router.delete(
    "/{project_id}/teams/{team_id}",
    status_code=status.HTTP_200_OK,
    summary="Открепить команду от проекта",
)
async def remove_team_from_project(
    project_id: UUID,
    team_id: UUID,
    service: ProjectTeamService = Depends(project_team_service_getter),
    credentials: tuple[uuid.UUID, str] = Depends(validate_curator)
):
    """
    Открепить команду от проекта.
    
    Примечание: вместо удаления связь помечается статусом WITHDRAWN
    для сохранения истории.
    """
    deleted = await service.remove_team_from_project(project_id, team_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь между проектом и командой не найдена"
        )
    return Response(f"Successfully removed team {team_id} from project {project_id}", 200)
