from uuid import UUID

from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import TeamModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, join
from app.infrastructure.database.models.teams.team_member import TeamMemberModel
from app.infrastructure.database.models.persons.student import StudentModel


class TeamRepository(BaseRepository[TeamModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(TeamModel, session)

    async def get_teams_summary(self, project_id=None):
        """Получить сводку команд с участниками"""
        # Сначала получить все команды
        query = select(TeamModel.id, TeamModel.name)
        if project_id:
            # Join with project_teams to filter by project
            from app.infrastructure.database.models.projects.project_team import ProjectTeamModel
            query = query.select_from(
                join(TeamModel, ProjectTeamModel, TeamModel.id == ProjectTeamModel.team_id)
            ).where(ProjectTeamModel.project_id == project_id)
        
        teams_result = await self.session.execute(query)
        teams = teams_result.all()

        result = []
        for team_row in teams:
            team_id = team_row.id
            team_name = team_row.name

            # Получить участников
            members_query = select(
                StudentModel.id,
                func.concat(
                    StudentModel.first_name,
                    ' ',
                    StudentModel.last_name,
                    func.coalesce(func.concat(' ', StudentModel.patronymic), '')
                ).label("full_name")
            ).select_from(
                join(TeamMemberModel, StudentModel, TeamMemberModel.student_id == StudentModel.id)
            ).where(TeamMemberModel.team_id == team_id)

            members_result = await self.session.execute(members_query)
            members = [
                {"id": str(row.id), "full_name": row.full_name.strip()}
                for row in members_result.all()
            ]

            result.append({
                "id": str(team_id),
                "name": team_name,
                "members_count": len(members),
                "members": members
            })

        return result

    async def get_teams_by_project(self, project_id: UUID):
        """Получить команды, назначенные на проект"""
        from app.infrastructure.database.models.projects.project_team import ProjectTeamModel
        
        query = select(TeamModel).select_from(
            TeamModel.join(ProjectTeamModel, TeamModel.id == ProjectTeamModel.team_id)
        ).where(ProjectTeamModel.project_id == project_id)
        
        result = await self.session.execute(query)
        return result.scalars().all()


def team_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = TeamRepository(session)
    return repository
