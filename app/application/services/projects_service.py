from uuid import UUID
from typing import List

from app.domain.entities.projects.project import Project
from app.infrastructure.database.repositories.crud_repository import CRUDRepository
from app.infrastructure.database.models.projects.project import ProjectModel  # предполагаем путь


class ProjectService:
    """
    Application Service для проектов.
    Содержит CRUD и место для доменной логики (start, complete, archive).
    """

    def __init__(
        self,
        project_repo: CRUDRepository[Project, ProjectModel],
    ) -> None:
        self._repo = project_repo

    async def create_project(self, project: Project) -> Project:
        return await self._repo.create(project)

    async def get_project(self, project_id: UUID) -> Project | None:
        return await self._repo.get(project_id)

    async def update_project(self, project: Project) -> Project:
        return await self._repo.update(project)

    async def delete_project(self, project_id: UUID) -> None:
        await self._repo.delete(project_id)

    async def list_projects(self) -> List[Project]:
        return await self._repo.list()