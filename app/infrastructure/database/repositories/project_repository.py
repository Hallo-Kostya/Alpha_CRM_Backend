from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import (
    ProjectModel,
    ProjectTeamModel,
    TeamModel,
    TeamMemberModel,
)
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Tuple, List
from sqlalchemy.dialects.postgresql import UUID


class ProjectRepository(BaseRepository[ProjectModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectModel, session)

    async def get_projects_summary(self, **filters) -> Tuple[int, List[dict]]:
        # Base query for projects
        query = (
            select(
                ProjectModel.id,
                ProjectModel.name,
                ProjectModel.description,
                func.count(ProjectTeamModel.id.distinct()).label("teams_count"),
                func.count(TeamMemberModel.id.distinct()).label("members_count"),
            )
            .filter_by(**filters)
            .select_from(ProjectModel)
            .outerjoin(ProjectTeamModel, ProjectModel.id == ProjectTeamModel.project_id)
            .outerjoin(TeamModel, ProjectTeamModel.team_id == TeamModel.id)
            .outerjoin(TeamMemberModel, TeamModel.id == TeamMemberModel.team_id)
        )

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
        self, excluded_ids: list[UUID], status: str
    ) -> list[ProjectModel]:
        query = (
            select(ProjectModel)
            .where(ProjectModel.id.notin_(excluded_ids))
            .where(ProjectModel.status == status)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


def project_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = ProjectRepository(session)
    return repository
