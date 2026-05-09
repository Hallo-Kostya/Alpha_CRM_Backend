from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import ProjectModel, ProjectTeamModel, TeamModel, TeamMemberModel
from app.infrastructure.database.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, join
from typing import Tuple, List, Optional
from sqlalchemy.dialects.postgresql import UUID
from app.common.enums import Semester


class ProjectRepository(BaseRepository[ProjectModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectModel, session)

    async def get_projects_summary(self, year: Optional[int] = None, semester: Optional[Semester] = None, team_id: Optional[UUID] = None) -> Tuple[int, List[dict]]:
        # Base query for projects
        query = select(
            ProjectModel.id,
            ProjectModel.name,
            ProjectModel.description,
            func.count(ProjectTeamModel.id.distinct()).label("teams_count"),
            func.count(TeamMemberModel.id.distinct()).label("members_count")
        ).select_from(
            ProjectModel
        ).outerjoin(
            ProjectTeamModel, ProjectModel.id == ProjectTeamModel.project_id
        ).outerjoin(
            TeamModel, ProjectTeamModel.team_id == TeamModel.id
        ).outerjoin(
            TeamMemberModel, TeamModel.id == TeamMemberModel.team_id
        )

        # Apply filters
        if year is not None:
            query = query.where(ProjectModel.year == year)
        if semester is not None:
            query = query.where(ProjectModel.semester == semester)
        if team_id is not None:
            query = query.where(ProjectTeamModel.team_id == team_id)

        # Group by project
        query = query.group_by(ProjectModel.id, ProjectModel.name, ProjectModel.description)

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
                "members_count": row.members_count
            }
            for row in rows
        ]
        
        total = len(items)

        return total, items


def project_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = ProjectRepository(session)
    return repository
