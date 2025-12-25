from typing import Sequence, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.projects.project_team import ProjectTeamModel
from app.domain.enums.project_team_status import ProjectTeamStatus
from app.core.database import db_helper


class ProjectTeamRepository(BaseRepository[ProjectTeamModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectTeamModel, session)

    async def get_by_project_and_team(
        self, project_id: UUID, team_id: UUID
    ) -> Optional[ProjectTeamModel]:
        """Найти связь по проекту и команде"""
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.team_id == team_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_project_id(
        self, project_id: UUID, 
        status: Optional[ProjectTeamStatus] = None
    ) -> Sequence[ProjectTeamModel]:
        """Получить все связи для проекта"""
        query = select(self.model).where(self.model.project_id == project_id)

        if status:
            query = query.where(self.model.status == status)

        result = await self.session.scalars(query)
        return result.all()

    async def get_by_team_id(
        self, team_id: UUID,
        status: Optional[ProjectTeamStatus] = None
    ) -> Sequence[ProjectTeamModel]:
        """Получить все связи для команды"""
        query = select(self.model).where(self.model.team_id == team_id)
        
        if status:
            query = query.where(self.model.status == status)
            
        result = await self.session.scalars(query)
        return result.all()

    async def get_active_project_for_team_in_semester(
    self, team_id: UUID, year: int, semester: str
    ) -> Optional[ProjectTeamModel]:
        """Получить активный проект команды в указанном семестре"""
        from app.infrastructure.database.models.projects.project import ProjectModel
        
        query = (
            select(ProjectTeamModel)
            .join(ProjectModel)  # Просто join без указания условий
            .where(
                ProjectTeamModel.team_id == team_id,
                ProjectTeamModel.status == ProjectTeamStatus.ACTIVE,
                ProjectModel.year == year,  # Ссылаемся на ProjectModel
                ProjectModel.semester == semester  # Ссылаемся на ProjectModel
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_by_project_and_team(
        self, project_id: UUID, team_id: UUID
    ) -> bool:
        """Удалить связь по проекту и команде"""
        project_team = await self.get_by_project_and_team(project_id, team_id)
        if not project_team:
            return False
        
        await self.session.delete(project_team)
        await self.session.commit()
        return True


def project_team_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> ProjectTeamRepository:
    repository = ProjectTeamRepository(session)
    return repository