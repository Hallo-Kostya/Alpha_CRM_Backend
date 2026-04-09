from fastapi import Depends
from app.application.dto.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectSummary,
)
from app.domain.entities.projects.project import Project
from app.infrastructure.database.models import ProjectModel
from app.application.services.base_service import BaseService
from app.infrastructure.database.repositories.project_repository import (
    ProjectRepository,
    project_repository_getter,
)
from app.domain.enums.semester import Semester
from app.domain.enums.project_status import ProjectStatus
from typing import Tuple, List
from datetime import datetime
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

    def compute_status(self, year: int, semester: Semester) -> ProjectStatus:
        """Вычисляет статус проекта по году/семестру относительно текущей даты.

        Используется как при создании, так и при периодическом обновлении.
        """
        return self.pyd_scheme.compute_status(year, semester)

    async def update_status_based_on_date(self, project_id: UUID) -> Project | None:
        """Обновляет статус проекта на основе года и семестра относительно текущей даты."""
        project = await self.get_by_id(project_id)
        if not project:
            return None

        new_status = self.compute_status(project.year, project.semester)

        # Обновляем только если статус изменился
        if project.status != new_status:
            update_data = ProjectUpdate(status=new_status)
            return await self.update(project_id, update_data)
        return project

    async def create(self, item):
        # при создании заполняем год/семестр/статус по умолчанию, если отсутствуют
        now = datetime.now()
        if hasattr(item, "year") and getattr(item, "year", None) is None:
            item.year = now.year
        if hasattr(item, "semester") and getattr(item, "semester", None) is None:
            item.semester = Semester.SPRING if now.month < 7 else Semester.AUTUMN

        # статус вычисляем только если не передан явно
        if hasattr(item, "year") and hasattr(item, "semester") and getattr(item, "status", None) is None:
            try:
                item.status = self.compute_status(item.year, item.semester)
            except Exception:
                pass
        return await super().create(item)

    async def get_projects_summary(self, year: int = None, semester: Semester = None) -> Tuple[int, List[ProjectSummary]]:
        total, items = await self._repo.get_projects_summary(year, semester)
        summaries = [ProjectSummary(**item) for item in items]
        return total, summaries

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
