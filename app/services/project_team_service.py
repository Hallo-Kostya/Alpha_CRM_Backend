from uuid import UUID
from fastapi import Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.schemas.project_team import ProjectTeam, ProjectTeamCreate, ProjectTeamUpdate, ProjectTeamWithInfo
from app.infrastructure.database.models.projects.project_team import ProjectTeamModel
from app.infrastructure.database.repositories.project_team_repository import (
    ProjectTeamRepository,
    project_team_repository_getter,
)
from app.infrastructure.database.repositories.project_repository import (
    ProjectRepository,
    project_repository_getter,
)
from app.infrastructure.database.repositories.team_repository import (
    TeamRepository,
    team_repository_getter,
)
from app.common.enums import ProjectTeamStatus


class ProjectTeamService:
    """Application service for project teams."""

    def __init__(
        self,
        project_team_repo: ProjectTeamRepository,
        project_repo: ProjectRepository,
        team_repo: TeamRepository,
    ):
        self._project_team_repo = project_team_repo
        self._project_repo = project_repo
        self._team_repo = team_repo

    def _to_orm(self, scheme: ProjectTeamCreate) -> ProjectTeamModel:
        """Convert schema to ORM model."""
        return ProjectTeamModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: ProjectTeamModel) -> ProjectTeam:
        """Convert ORM model to schema."""
        return ProjectTeam.model_validate(orm_model, from_attributes=True)

    async def _validate_project_and_team_exist(
        self, project_id: UUID, team_id: UUID
    ) -> None:
        """Check project and team existence."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found",
            )

        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} not found",
            )

    async def assign_team_to_project(
        self, project_id: UUID, data: ProjectTeamCreate
    ) -> ProjectTeam:
        """Assign team to project."""
        # Check project and team existence
        await self._validate_project_and_team_exist(project_id, data.team_id)

        # Get project info for validations
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found",
            )

        # Check project has year and semester
        if not hasattr(project, "year") or not hasattr(project, "semester"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project doesn't have year and semester",
            )

        # Check team not already assigned to project
        existing = await self._project_team_repo.get_by_project_and_team(
            project_id, data.team_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Team already assigned to this project",
            )

        # Check team doesn't have active project in same semester
        active_project = (
            await self._project_team_repo.get_active_project_for_team_in_semester(
                data.team_id, project.year, project.semester
            )
        )
        if active_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team already participates in project {active_project.project_id} "
                f"in {project.year} {project.semester.value} semester",
            )

        # Create link
        project_team_data = {
            "project_id": project_id,
            "team_id": data.team_id,
            "status": data.status,
        }

        orm_obj = ProjectTeamModel(**project_team_data)
        created_obj = await self._project_team_repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def update_project_team_status(
        self, project_id: UUID, team_id: UUID, new_data: ProjectTeamUpdate
    ) -> ProjectTeam | None:
        """Update project team."""
        project_team = await self._project_team_repo.get_by_project_and_team(
            project_id, team_id
        )
        if not project_team:
            return None
        updated_obj = await self._project_team_repo.update(
            project_team, new_data.model_dump(exclude_unset=True)
        )
        return self._to_schema(updated_obj)

    async def delete_team_from_project(self, project_id: UUID, team_id: UUID) -> bool:
        """Remove team from project (change status to WITHDRAWN)."""
        project_team = await self._project_team_repo.get_by_project_and_team(
            project_id, team_id
        )
        if not project_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Link between project and team not found",
            )

        # Instead of delete, change status to WITHDRAWN for history
        project_team.status = ProjectTeamStatus.WITHDRAWN
        await self._repo.session.commit()
        await self._repo.session.refresh(project_team)

        return True

    async def get_by_id(self, project_id: UUID, team_id: UUID) -> ProjectTeam | None:
        """Get project team by project and team IDs."""
        project_team = await self._project_team_repo.get_by_project_and_team(
            project_id, team_id
        )
        if not project_team:
            return None
        return self._to_schema(project_team)

    async def get_team_projects(
        self, team_id: UUID, project_team_status: Optional[ProjectTeamStatus] = None
    ) -> List[ProjectTeam]:
        """Get all projects of team."""
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} not found",
            )

        team_projects = await self._project_team_repo.get_by_team_id(
            team_id, project_team_status
        )
        return [self._to_schema(project_team) for project_team in team_projects]

    async def get_current_team_project(
        self, team_id: UUID
    ) -> Optional[ProjectTeam]:
        """Get current active project of team."""
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} not found",
            )

        active_links = await self._project_team_repo.get_by_team_id(
            team_id, ProjectTeamStatus.ACTIVE
        )

        if active_links:
            return self._to_schema(active_links[0])
        return None

    async def get_project_teams_with_info(
        self, project_id: UUID
    ) -> List[ProjectTeamWithInfo]:
        """Get project teams with detailed information."""
        project = await self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found",
            )

        # Get links with eager loaded team info
        query = (
            select(ProjectTeamModel)
            .where(ProjectTeamModel.project_id == project_id)
            .options(selectinload(ProjectTeamModel.team))
        )

        result = await self._project_team_repo.session.execute(query)
        project_teams = result.scalars().all()

        # Transform to DTO with info
        result_list = []
        for pt in project_teams:
            result_list.append(
                ProjectTeamWithInfo(
                    project_id=UUID(str(pt.project_id)),
                    team_id=UUID(str(pt.team_id)),
                    assigned_at=pt.assigned_at,
                    status=pt.status,
                    project_name=project.name,
                    team_name=pt.team.name if pt.team else "Unknown team",
                    project_year=project.year,
                    project_semester=project.semester,
                )
            )

        return result_list


def project_team_service_getter(
    project_team_repo: ProjectTeamRepository = Depends(project_team_repository_getter),
    project_repo: ProjectRepository = Depends(project_repository_getter),
    team_repo: TeamRepository = Depends(team_repository_getter),
) -> ProjectTeamService:
    return ProjectTeamService(project_team_repo, project_repo, team_repo)
