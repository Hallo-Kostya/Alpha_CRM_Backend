from typing import Sequence, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.teams.team_member import TeamMemberModel
from app.core.database import db_helper


class TeamMemberRepository(BaseRepository[TeamMemberModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(TeamMemberModel, session)

    async def get_by_team_and_student(
        self, team_id: UUID, student_id: UUID
    ) -> Optional[TeamMemberModel]:
        """Найти связь по команде и студенту"""
        query = select(self.model).where(
            self.model.team_id == team_id,
            self.model.student_id == student_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_team_id(self, team_id: UUID) -> Sequence[TeamMemberModel]:
        """Получить все связи для команды"""
        query = select(self.model).where(self.model.team_id == team_id)
        result = await self.session.scalars(query)
        return result.all()

    async def get_by_student_id(self, student_id: UUID) -> Sequence[TeamMemberModel]:
        """Получить все связи для студента"""
        query = select(self.model).where(self.model.student_id == student_id)
        result = await self.session.scalars(query)
        return result.all()

    async def delete_by_team_and_student(self, team_id: UUID, student_id: UUID) -> bool:
        """Удалить связь по команде и студенту"""
        team_member = await self.get_by_team_and_student(team_id, student_id)
        if not team_member:
            return False
        
        await self.session.delete(team_member)
        await self.session.commit()
        return True


def team_member_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> TeamMemberRepository:
    repository = TeamMemberRepository(session)
    return repository