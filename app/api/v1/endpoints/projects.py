from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.project import ProjectCreate, ProjectUpdate
from app.application.services.projects_service import ProjectService
from app.core.database import db_helper
from app.domain.entities.projects.project import Project
from app.infrastructure.database.models.projects.project import ProjectModel
from app.infrastructure.database.repositories.crud_repository import CRUDRepository


router = APIRouter(prefix="/projects", tags=["projects"])


async def get_project_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> ProjectService:
    repo = CRUDRepository[Project, ProjectModel](
        model=ProjectModel,
        domain_model=Project,
        session=session,
    )
    return ProjectService(repo)


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    project = Project(**data.model_dump(exclude_unset=True))
    return await service.create_project(project)


@router.get("/", response_model=List[Project])
async def list_projects(
    service: ProjectService = Depends(get_project_service),
) -> List[Project]:
    return await service.list_projects()


@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    project = await service.get_project(project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> Project:
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update",
        )

    existing = await service.get_project(project_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Project not found")

    updated_project = existing.model_copy(update=update_data)
    return await service.update_project(updated_project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> None:
    await service.delete_project(project_id)