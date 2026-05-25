from app.common.enums import ProjectTeamStatus
from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import (
    ProjectModel,
    ProjectTeamModel,
    TeamModel,
    TeamMemberModel,
)
from app.infrastructure.database.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case, distinct, select, func
from typing import Any, Tuple, List
from sqlalchemy.dialects.postgresql import UUID


FILTERS_MAP = {
    "id": ProjectModel.id,
    "name": ProjectModel.name,
    "year": ProjectModel.year,
    "semester": ProjectModel.semester,
    "status": ProjectModel.status,
    "team_id": ProjectTeamModel.team_id,
}


class ProjectRepository(BaseRepository[ProjectModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectModel, session)

    async def get_projects_summary(
        self, status: list[ProjectTeamStatus] | None = None, **filters
    ) -> Tuple[int, List[dict]]:
        # Base query for projects
        teams_count_expr = func.count(ProjectTeamModel.id.distinct())
        members_count_expr = func.count(TeamMemberModel.id.distinct())
        if status:  # filter project_team instances by its statuses
            teams_count_expr = func.count(
                distinct(
                    case((ProjectTeamModel.status.in_(status), ProjectTeamModel.id))
                )
            )

            members_count_expr = func.count(
                distinct(
                    case((ProjectTeamModel.status.in_(status), TeamMemberModel.id))
                )
            )
        query = (
            select(
                ProjectModel.id,
                ProjectModel.name,
                ProjectModel.description,
                teams_count_expr.label("teams_count"),
                members_count_expr.label("members_count"),
            )
            .select_from(ProjectModel)
            .outerjoin(ProjectTeamModel, ProjectModel.id == ProjectTeamModel.project_id)
            .outerjoin(TeamModel, ProjectTeamModel.team_id == TeamModel.id)
            .outerjoin(TeamMemberModel, TeamModel.id == TeamMemberModel.team_id)
        )
        # Filtering
        conditions = []

        for key, value in filters.items():
            column = FILTERS_MAP.get(key)

            if column:
                conditions.append(column == value)

        if conditions:
            query = query.where(*conditions)

        # Group by project
        query = query.group_by(
            ProjectModel.id, ProjectModel.name, ProjectModel.description
        )

        # Execute query
        result = await self.session.execute(query)
        rows = result.all()

        # Convert to dicts
        items = [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "teams_count": row.teams_count,
                "members_count": row.members_count,
            }
            for row in rows
        ]

        total = len(items)

        return total, items

    async def get_projects_with_excluded_ids(
        self, excluded_ids: list[UUID], filters: dict[str, Any]
    ) -> list[ProjectModel]:
        query = (
            select(ProjectModel)
            .where(ProjectModel.id.notin_(excluded_ids))
            .filter_by(**filters)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


def project_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = ProjectRepository(session)
    return repository
