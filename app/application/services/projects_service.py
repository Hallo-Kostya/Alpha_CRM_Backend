from fastapi import Depends
from app.application.dto.project import (
    ProjectCreate,
    ProjectUpdate,
)
from app.domain.entities.projects.project import Project
from app.infrastructure.database.models import ProjectModel
from app.application.services.base_service import BaseService
from app.infrastructure.database.repositories.project_repository import (
    ProjectRepository,
    project_repository_getter,
)
from uuid import UUID


class ProjectService(BaseService[ProjectModel, Project]):
    """
    Application Service для проектов.
    Содержит CRUD и место для доменной логики (start, complete, archive).
    """

    orm_model = ProjectModel
    pyd_scheme = Project

    def __init__(
        self,
        project_repo: ProjectRepository,
    ):
        super().__init__(project_repo)

    async def create(self, new_obj: ProjectCreate) -> Project:
        orm_model = self._to_orm(new_obj)
        created_model = await self._repo.create(orm_model)
        return self._to_schema(created_model)

    async def update(
        self, new_data: ProjectUpdate, project_id: UUID
    ) -> Project | None:
        old_obj = await self._repo.get_by_id(project_id)
        if not old_obj:
            return None
        updated_obj = await self._repo.update(
            old_obj, new_data.model_dump(exclude_unset=True)
        )
        return self._to_schema(updated_obj)


def project_service_getter(
    repository: ProjectRepository = Depends(project_repository_getter),
) -> ProjectService:
    return ProjectService(repository)
