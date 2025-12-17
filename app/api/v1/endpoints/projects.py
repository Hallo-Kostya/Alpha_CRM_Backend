from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.application.dto.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
)
from app.application.services.projects_service import (
    project_service_getter,
    ProjectService,
)


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Project not found"}},
)


@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый проект",
)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(project_service_getter),
):
    """Создать проект (на этапе планирования, без команд)."""
    return await service.create(data)


@router.get("/", response_model=List[ProjectRead], summary="Список всех проектов")
async def list_projects(
    service: ProjectService = Depends(project_service_getter),
):
    """Получить список всех проектов (с фильтрами можно расширить позже)."""
    return await service.get_list()


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
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


@router.put(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Обновить проект (частично)",
)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    service: ProjectService = Depends(project_service_getter),
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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить проект",
)
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
    return Response(f"successfully deleted project with id {project_id}", 200)
