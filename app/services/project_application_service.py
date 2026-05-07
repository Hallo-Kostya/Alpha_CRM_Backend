from uuid import UUID
from fastapi import Depends, HTTPException, status, Response
from typing import Sequence
from app.common.utils import get_curr_year_and_semester
from app.schemas.project_application import (
    ProjectApplicationGET,
    ProjectApplicationPATCH,
    ProjectApplicationPOST,
)
from app.infrastructure.database.models import ProjectModel, TeamModel, ProjectApplicationModel
from app.infrastructure.database.repositories.project_application_repository import (
    ProjectApplicationRepository,
    project_applications_repository_getter,
)
from app.infrastructure.database.repositories.project_repository import (
    ProjectRepository,
    project_repository_getter,
)
from app.infrastructure.database.repositories.team_repository import (
    TeamRepository,
    team_repository_getter,
)
from app.infrastructure.database.repositories.project_team_repository import (
    ProjectTeamRepository,
    project_team_repository_getter,
)
from app.api.filters import ProjectApplicationFilter
from app.common.enums import ProjectStatus


class ProjectApplicationService:
    """Application service for project applications"""

    def __init__(
        self,
        project_application_repo: ProjectApplicationRepository,
        project_team_repo: ProjectTeamRepository,
        project_repo: ProjectRepository,
        team_repo: TeamRepository,
    ):
        self._project_application_repo = project_application_repo
        self._project_team_repo = project_team_repo
        self._project_repo = project_repo
        self._team_repo = team_repo

    def _to_orm(self, scheme: ProjectApplicationPOST) -> ProjectApplicationModel:
        """Convert schema to ORM model."""
        return ProjectApplicationModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: ProjectApplicationModel) -> ProjectApplicationGET:
        """Convert ORM model to schema."""
        return ProjectApplicationGET.model_validate(orm_model, from_attributes=True)

    async def _get_project_and_team(
        self, project_id: UUID, team_id: UUID
    ) -> tuple[ProjectModel, TeamModel]:
        """Check project and team existence."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} is not found",
            )

        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} is not found",
            )
        return project, team
    
    async def _get_applications_by_vk_id(
        self, vk_sender_id: int
    ) -> Sequence[ProjectApplicationModel]:
        """Check project and team existence."""
        _, applications_objs = await self._project_application_repo.get_list({"vk_sender_id": vk_sender_id})
        return applications_objs


    async def create_application(
        self, data: ProjectApplicationPOST
    ) -> ProjectApplicationGET:
        """Create team's project application"""
        _, applications_objs = await self._project_application_repo.get_list({"vk_sender_id": data.vk_sender_id, "project_id": data.project_id})
        if applications_objs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User already has been aplied to this project {data.project_id}, user: {data.vk_sender_id}",
            )
        project, team = await self._get_project_and_team(data.project_id, data.team_id)
        curr_year, curr_semester = get_curr_year_and_semester()
        if any((project.status != ProjectStatus.PLANNED, project.year != curr_year, project.semester != curr_semester)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with id {project.id} is not available for apply at this time",
            )
        prev_projs_mean_score = 0.0
        if team:
            _, prev_projs = await self._project_team_repo.get_list({"team_id": team.id})
            prev_projs_mean_scores = [proj["final_score"] for proj in prev_projs]
            if prev_projs_mean_scores:
                prev_projs_mean_score = sum(prev_projs_mean_scores) / len(prev_projs_mean_scores)
        data.mean_project_score = prev_projs_mean_score
        try:
            created_obj = await self._project_application_repo.create(self._to_orm(data))
            return self._to_schema(created_obj)
        except Exception as e:
            print
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with id {project.id} is not available for apply at this time",
            )
        

    async def update_project_application(
        self, application_id: UUID, new_data: ProjectApplicationPATCH,
    ) -> ProjectApplicationGET:
        """Update project application."""
        app_obj = await self._project_application_repo.get_by_id(application_id)
        if not app_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} is not found",
            )
        updated_obj = await self._project_application_repo.update(
            app_obj, new_data.model_dump(exclude_unset=True)
        )
        return self._to_schema(updated_obj)


    async def delete_application(self, application_id: UUID) -> Response:
        project_team = await self._project_application_repo.get_by_id(application_id)
        if not project_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} is not found",
            )
        await self._project_application_repo.delete(project_team)
        return Response(f"Successfuly deleted application with id: {application_id}", status_code=200)

    async def get_applications(
        self,
        filters: ProjectApplicationFilter,
        eager_loads: list[str] | None = None
    ) -> list[ProjectApplicationGET]:
        _, applications = await self._project_application_repo.get_list(filters=filters.model_dump(exclude_unset=True), eager_loads=eager_loads)
        return [self._to_schema(application) for application in applications]


def project_application_service_getter(
    project_team_repo: ProjectTeamRepository = Depends(project_team_repository_getter),
    project_repo: ProjectRepository = Depends(project_repository_getter),
    team_repo: TeamRepository = Depends(team_repository_getter),
    project_application_repo: ProjectApplicationRepository = Depends(project_applications_repository_getter),
) -> ProjectApplicationService:
    return ProjectApplicationService(project_application_repo, project_team_repo, project_repo, team_repo)
