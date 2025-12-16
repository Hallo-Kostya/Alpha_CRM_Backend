from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.project import ProjectCreate, ProjectUpdate, ProjectRead
from app.application.services.projects_service import ProjectService
from app.core.database import db_helper
from app.domain.entities.projects.project import Project
from app.infrastructure.database.models.projects.project import ProjectModel
from app.infrastructure.database.repositories.crud_repository import CRUDRepository


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Project not found"}},
)


async def get_project_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> ProjectService:
    """Фабрика ProjectService с CRUD-репозиторием."""
    repo = CRUDRepository[Project, ProjectModel](
        model=ProjectModel,
        domain_model=Project,
        session=session,
    )
    return ProjectService(project_repo=repo)


@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый проект",
)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """Создать проект (на этапе планирования, без команд)."""
    project = Project(**data.model_dump(exclude_unset=True))
    return await service.create_project(project)


@router.get("/", response_model=List[ProjectRead], summary="Список всех проектов")
async def list_projects(
    service: ProjectService = Depends(get_project_service),
) -> List[Project]:
    """Получить список всех проектов (с фильтрами можно расширить позже)."""
    return await service.list_projects()


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Получить проект по ID",
)
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """Получить детальную информацию о проекте."""
    project = await service.get_project(project_id)
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
    service: ProjectService = Depends(get_project_service),
) -> Project:
    """Частичное обновление данных проекта."""
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не переданы данные для обновления",
        )

    existing = await service.get_project(project_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект с ID {project_id} не найден",
        )

    # Доменные методы (start/complete/archive) можно вызывать здесь, если нужно
    updated_project = existing.model_copy(update=update_data)
    return await service.update_project(updated_project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить проект",
)
async def delete_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> None:
    """Удалить проект. Каскадно удалятся вехи, оценки, связи с командами и артефакты."""
    project = await service.get_project(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Проект с ID {project_id} не найден",
        )
    await service.delete_project(project_id)