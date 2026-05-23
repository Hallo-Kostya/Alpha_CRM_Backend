from typing import Any

from fastapi import Depends
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectSummary,
    ProjectSummaryResponse,
)
from app.schemas.project import Project, ProjectRead
from app.infrastructure.database.models import ProjectModel
from app.infrastructure.database.repositories.project_repository import (
    ProjectRepository,
    project_repository_getter,
)
from app.common.enums import Semester, ProjectStatus
from datetime import datetime
from uuid import UUID


class ProjectService:
    """
    Application Service for projects.
    Contains CRUD and business logic (start, complete, archive).
    """

    def __init__(self, project_repo: ProjectRepository):
        self.project_repo = project_repo

    def _to_orm(self, scheme: ProjectCreate) -> ProjectModel:
        """Convert schema to ORM model."""
        return ProjectModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: ProjectModel) -> Project:
        """Convert ORM model to schema."""
        return Project.model_validate(orm_model, from_attributes=True)

    @staticmethod
    def compute_status(year: int, semester: Semester) -> ProjectStatus:
        """Compute project status based on year/semester relative to current date.

        Used both when creating and periodically updating.
        """
        return Project.compute_status(year, semester)

    async def create(self, new_obj: ProjectCreate) -> Project:
        """Create new project."""
        now = datetime.now()
        orm_obj = self._to_orm(new_obj)
        if orm_obj.year is None:
            orm_obj.year = now.year
        if orm_obj.semester is None:
            orm_obj.semester = Semester.SPRING if now.month < 7 else Semester.AUTUMN
        orm_obj.status = self.compute_status(orm_obj.year, orm_obj.semester)
        created_obj = await self.project_repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def update(self, project_id: UUID, new_data: ProjectUpdate) -> Project | None:
        """Update project."""
        old_obj = await self.project_repo.get_by_id(project_id)
        if not old_obj:
            return None
        updated_obj = await self.project_repo.update(
            old_obj, new_data.model_dump(exclude_unset=True)
        )
        return self._to_schema(updated_obj)

    async def delete(self, project_id: UUID) -> bool:
        """Delete project."""
        obj = await self.project_repo.get_by_id(project_id)
        if not obj:
            return False
        await self.project_repo.delete(obj)
        return True

    async def get_by_id(
        self, project_id: UUID, eager_loads: list[str] | None = None
    ) -> Project | None:
        """Get project by ID."""
        obj = await self.project_repo.get_by_id(project_id, eager_loads)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_projects_summary(self, **filters) -> ProjectSummaryResponse:
        """Get projects summary."""
        total, items = await self.project_repo.get_projects_summary(**filters)
        summaries = [ProjectSummary(**item) for item in items]
        return ProjectSummaryResponse(total=total, projects=summaries)

    async def get_projects_with_excluded_ids(
        self,
        excluded_ids: list[UUID],
        filters: dict[str, Any],
    ) -> list[ProjectRead]:
        result = await self.project_repo.get_projects_with_excluded_ids(
            excluded_ids, filters
        )
        return [ProjectRead.model_validate(project) for project in result]


def project_service_getter(
    repository: ProjectRepository = Depends(project_repository_getter),
) -> ProjectService:
    return ProjectService(repository)
