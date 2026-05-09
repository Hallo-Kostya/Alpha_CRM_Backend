from uuid import UUID

from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import TeamModel
from app.infrastructure.database.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, join
from app.infrastructure.database.models.teams.team_member import TeamMemberModel
from app.infrastructure.database.models.persons.student import StudentModel


class TeamRepository(BaseRepository[TeamModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(TeamModel, session)

    async def get_teams_summary(self, project_id=None):
        query = (
            select(
                TeamModel.id,
                TeamModel.name,
                StudentModel.id.label("student_id"),
                func.concat(
                    StudentModel.first_name, ' ',
                    StudentModel.last_name,
                    func.coalesce(func.concat(' ', StudentModel.patronymic), '')
                ).label("full_name"),
            )
            .select_from(TeamModel)
            .outerjoin(TeamMemberModel, TeamModel.id == TeamMemberModel.team_id)
            .outerjoin(StudentModel, TeamMemberModel.student_id == StudentModel.id)
        )

        if project_id:
            from app.infrastructure.database.models.projects.project_team import ProjectTeamModel
            query = query.join(ProjectTeamModel, TeamModel.id == ProjectTeamModel.team_id)
            query = query.where(ProjectTeamModel.project_id == project_id)

        result = await self.session.execute(query)
        rows = result.all()

        # Группируем в памяти
        teams: dict[UUID, dict] = {}
        for row in rows:
            if row.id not in teams:
                teams[row.id] = {
                    "id": str(row.id),
                    "name": row.name,
                    "members": [],
                }
            if row.student_id:
                teams[row.id]["members"].append({
                    "id": str(row.student_id),
                    "full_name": row.full_name.strip(),
                })

        return [
            {**team, "members_count": len(team["members"])}
            for team in teams.values()
        ]


def team_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = TeamRepository(session)
    return repository
