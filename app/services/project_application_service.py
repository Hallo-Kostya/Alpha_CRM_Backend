from uuid import UUID
from fastapi import Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import Sequence
from app.common.utils import get_curr_year_and_semester
from app.schemas.project_application import (
    ProjectApplicationGET,
    ProjectApplicationPATCH,
    ProjectApplicationPOST,
    TeamMemberPOST,
    ProjectApplicationGETLimited,
)
from app.infrastructure.database.models import (
    ProjectModel,
    TeamModel,
    ProjectApplicationModel,
    StudentModel,
    ProjectApplicationMemberModel,
)
from app.services.team_member_service import (
    TeamMemberService,
    team_member_service_getter,
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
from app.infrastructure.database.repositories.project_applications import (
    ProjectApplicationRepository,
    ProjectApplicationMemberRepository,
    ProjectInterviewRepository,
    ArtifactInterviewRepository,
    project_application_members_repository_getter,
    project_interview_repository_getter,
    project_applications_repository_getter,
    artifact_interview_repository_getter,
)
from app.api.filters import ProjectApplicationFilter
from app.common.enums import ProjectStatus


class ProjectApplicationService:
    """Application service for project applications"""

    def __init__(
        self,
        project_application_repo: ProjectApplicationRepository,
        application_member_repo: ProjectApplicationMemberRepository,
        interview_repo: ProjectInterviewRepository,
        artifacts_repo: ArtifactInterviewRepository,
        project_team_repo: ProjectTeamRepository,
        project_repo: ProjectRepository,
        team_repo: TeamRepository,
        tm_service: TeamMemberService,
    ):
        self._project_application_repo = project_application_repo
        self._application_member_repo = application_member_repo
        self._interview_repo = interview_repo
        self._artifacts_repo = artifacts_repo
        self._project_team_repo = project_team_repo
        self._project_repo = project_repo
        self._team_repo = team_repo
        self._tm_service = tm_service

    def _to_orm(self, scheme: ProjectApplicationPOST) -> ProjectApplicationModel:
        """Convert schema to ORM model."""
        return ProjectApplicationModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: ProjectApplicationModel) -> ProjectApplicationGET:
        """Convert ORM model to schema."""
        return ProjectApplicationGET.model_validate(orm_model, from_attributes=True)

    async def _get_project(self, project_id: UUID) -> ProjectModel:
        """Check project existence."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} is not found",
            )
        return project

    async def _get_applications_by_vk_id(
        self, vk_sender_id: int
    ) -> Sequence[ProjectApplicationModel]:
        """Check project and team existence."""
        _, applications_objs = await self._project_application_repo.get_list(
            {"vk_sender_id": vk_sender_id}
        )
        return applications_objs

    async def _validate_project(self, project: ProjectModel) -> None:
        curr_year, curr_semester = get_curr_year_and_semester()
        if any(
            (
                project.status != ProjectStatus.PLANNED,
                project.year != curr_year,
                project.semester != curr_semester,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with id {project.id} is not available for apply at this time",
            )

    async def _validate_vk_sender(self, vk_sender_id: int, project_id: UUID) -> None:
        _, applications_objs = await self._project_application_repo.get_list(
            {"vk_sender_id": vk_sender_id, "project_id": project_id}
        )
        if applications_objs:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User already has been aplied for this project {project_id}, user: {vk_sender_id}",
            )

    async def _get_team_prev_projects_mean_rate(self, team_name: str) -> float:
        team = await self._get_team(team_name)
        if not team:
            return 0.0
        _, prev_projs = await self._project_team_repo.get_list({"team_id": team.id})
        prev_projs_rates = [proj["final_score"] for proj in prev_projs]
        mean_score = 0.0
        if prev_projs_rates:
            mean_score = sum(prev_projs_rates) / len(prev_projs_rates)
        return mean_score

    async def _validate_data(self, data: ProjectApplicationPOST) -> None:
        await self._validate_vk_sender(data.vk_sender_id, data.project_id)
        project = await self._get_project(data.project_id)
        await self._validate_project(project)

    async def _get_team(
        self,
        team_name: str | None = None,
        team_id: UUID | None = None,
    ) -> TeamModel | None:
        if not any((team_name, team_id)):
            return None
        filters: dict[str, str | UUID] = {}
        if team_id:
            filters["id"] = team_id
        if team_name:
            filters["name"] = team_name
        _, teams = await self._team_repo.get_list(filters)
        return next(iter(teams), None)

    async def _get_student_by_email(
        self, email: str, session: AsyncSession
    ) -> StudentModel | None:
        query = select(StudentModel).where(StudentModel.email == email)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    def _map_project_app_members(
        self,
        team_members: list[TeamMemberPOST],
    ) -> list[ProjectApplicationMemberModel]:
        result = []
        for team_member in team_members:
            obj = ProjectApplicationMemberModel(
                fullname=team_member.fullname,
                role=team_member.role,
                study_group=team_member.study_group,
            )
            result.append(obj)
        return result

    async def create_application(
        self, data: ProjectApplicationPOST, session: AsyncSession
    ) -> ProjectApplicationGETLimited:
        """Create team's project application"""
        async with session.begin():
            await self._validate_data(data)
            project_app_members = self._map_project_app_members(data.team_members)
            data.mean_project_score = await self._get_team_prev_projects_mean_rate(
                data.team_name
            )
            application_dto = ProjectApplicationModel(
                project_id=data.project_id,
                description=data.description,
                team_name=data.team_name,
                vk_sender_id=data.vk_sender_id,
                status=data.status,
                mean_project_score=data.mean_project_score,
                members=project_app_members,
            )
            session.add(application_dto)
        return ProjectApplicationGETLimited.model_validate(
            application_dto, from_attributes=True
        )

    async def update_project_application(
        self,
        application_id: UUID,
        new_data: ProjectApplicationPATCH,
    ) -> ProjectApplicationGETLimited:
        """Update project application."""
        app_obj = await self._project_application_repo.get_by_id(
            application_id, ["members"]
        )
        if not app_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} is not found",
            )
        data_to_update = new_data.model_dump(exclude_unset=True, exclude={"members"})
        await self._project_application_repo.update(app_obj, data_to_update)
        if new_data.members:
            for member in new_data.members:
                member_obj = await self._application_member_repo.get_by_id(member.id)
                member_data_to_update = member.model_dump(exclude_unset=True)
                await self._application_member_repo.update(
                    member_obj, member_data_to_update
                )
        return ProjectApplicationGETLimited.model_validate(
            app_obj, from_attributes=True
        )

    async def delete_application(self, application_id: UUID) -> Response:
        project_team = await self._project_application_repo.get_by_id(application_id)
        if not project_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application with ID {application_id} is not found",
            )
        await self._project_application_repo.delete(project_team)
        return Response(
            f"Successfuly deleted application with id: {application_id}",
            status_code=200,
        )

    async def get_applications(
        self,
        filters: ProjectApplicationFilter,
        detailed: bool = False,
        eager_loads: list[str] | None = None,
    ) -> list[ProjectApplicationGETLimited | ProjectApplicationGET]:
        _, applications = await self._project_application_repo.get_list(
            filters=filters.model_dump(exclude_unset=True), eager_loads=eager_loads
        )
        if detailed:
            return [self._to_schema(application) for application in applications]
        return [
            ProjectApplicationGETLimited.model_validate(
                application, from_attributes=True
            )
            for application in applications
        ]


def project_application_service_getter(
    project_team_repo: ProjectTeamRepository = Depends(project_team_repository_getter),
    app_members_repo: ProjectApplicationMemberRepository = Depends(
        project_application_members_repository_getter
    ),
    interviews_repo: ProjectInterviewRepository = Depends(
        project_interview_repository_getter
    ),
    interview_artifacts_repo: ArtifactInterviewRepository = Depends(
        artifact_interview_repository_getter
    ),
    team_repo: TeamRepository = Depends(team_repository_getter),
    project_repo: ProjectRepository = Depends(project_repository_getter),
    project_application_repo: ProjectApplicationRepository = Depends(
        project_applications_repository_getter
    ),
    tm_service: TeamMemberService = Depends(team_member_service_getter),
) -> ProjectApplicationService:
    return ProjectApplicationService(
        project_application_repo,
        app_members_repo,
        interviews_repo,
        interview_artifacts_repo,
        project_team_repo,
        project_repo,
        team_repo,
        tm_service,
    )
