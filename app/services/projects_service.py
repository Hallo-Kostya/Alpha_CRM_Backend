from fastapi import Depends
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectSummary,
    ProjectSummaryResponse,
)
from app.schemas.project import Project
from app.infrastructure.database.models import ProjectModel
from app.infrastructure.database.repositories.project_repository import (
    ProjectRepository,
    project_repository_getter,
)
from app.common.enums import Semester, ProjectStatus
from typing import List
from datetime import datetime
from uuid import UUID


class ProjectService:
    """
    Application Service for projects.
    Contains CRUD and business logic (start, complete, archive).
    """

    def __init__(self, project_repo: ProjectRepository):
        self._repo = project_repo

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

    async def update_status_based_on_date(self, project_id: UUID) -> Project | None:
        """Update project status based on year and semester relative to current date."""
        project = await self.get_by_id(project_id)
        if not project:
            return None

        new_status = self.compute_status(project.year, project.semester)

        # Update only if status changed
        if project.status != new_status:
            update_data = ProjectUpdate(status=new_status)
            return await self.update(project_id, update_data)
        return project

    async def create(self, new_obj: ProjectCreate) -> Project:
        """Create new project."""
        # Fill in default values for year/semester/status if missing
        data = new_obj.model_dump(exclude_unset=True)
        now = datetime.now()
        
        if "year" not in data or data["year"] is None:
            data["year"] = now.year
        if "semester" not in data or data["semester"] is None:
            data["semester"] = Semester.SPRING if now.month < 7 else Semester.AUTUMN
        
        # Compute status if not provided
        if "status" not in data or data["status"] is None:
            try:
                data["status"] = self.compute_status(data["year"], data["semester"])
            except Exception:
                pass
        
        orm_obj = ProjectModel(**data)
        created_obj = await self._repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def update(self, project_id: UUID, new_data: ProjectUpdate) -> Project | None:
        """Update project."""
        old_obj = await self._repo.get_by_id(project_id)
        if not old_obj:
            return None
        updated_obj = await self._repo.update(
            old_obj, new_data.model_dump(exclude_unset=True)
        )
        return self._to_schema(updated_obj)

    async def delete(self, project_id: UUID) -> bool:
        """Delete project."""
        obj = await self._repo.get_by_id(project_id)
        if not obj:
            return False
        await self._repo.delete(obj)
        return True

    async def get_by_id(self, project_id: UUID) -> Project | None:
        """Get project by ID."""
        obj = await self._repo.get_by_id(project_id)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_list(self, **filter_attrs) -> List[Project]:
        """Get list of projects."""
        items = await self._repo.get_list(**filter_attrs)
        return [self._to_schema(item) for item in items]

    async def get_projects_summary(self, year: int = None, semester: Semester = None) -> ProjectSummaryResponse:
        """Get projects summary."""
        total, items = await self._repo.get_projects_summary(year, semester)
        summaries = [ProjectSummary(**item) for item in items]
        return ProjectSummaryResponse(total=total, projects=summaries)


def project_service_getter(
    repository: ProjectRepository = Depends(project_repository_getter),
) -> ProjectService:
    return ProjectService(repository)
