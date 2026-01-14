from typing import Sequence, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.orm import selectinload

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.meetings.meeting import MeetingModel
from app.domain.enums.meeting_status import MeetingStatus
from app.core.database import db_helper


class MeetingRepository(BaseRepository[MeetingModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(MeetingModel, session)

    async def get_by_team_id(
        self, team_id: UUID, 
        status: Optional[MeetingStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Sequence[MeetingModel]:
        """Получить все встречи команды"""
        query = select(self.model).where(self.model.team_id == team_id)
        
        if status:
            query = query.where(self.model.status == status)
        
        if from_date:
            query = query.where(self.model.date >= from_date)
            
        if to_date:
            query = query.where(self.model.date <= to_date)
            
        query = query.order_by(self.model.date.asc())
        result = await self.session.scalars(query)
        return result.all()
    
    async def get_all_ordered_by_date(self) -> Sequence[MeetingModel]:
        """Получить все встречи всех команд, отсортированные по времени"""
        query = (
            select(self.model)
            .order_by(self.model.date.asc())
        )

        result = await self.session.scalars(query)
        return result.all()

    async def get_upcoming_meeting(self, team_id: UUID) -> Optional[MeetingModel]:
        """Получить ближайшую запланированную встречу команды"""
        query = (
            select(self.model)
            .where(
                self.model.team_id == team_id,
                self.model.status == MeetingStatus.SCHEDULED,
                self.model.date >= func.now()
            )
            .order_by(self.model.date.asc())
            .limit(1)
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_last_completed_meeting(self, team_id: UUID) -> Optional[MeetingModel]:
        """Получить последнюю завершенную встречу команды"""
        query = (
            select(self.model)
            .where(
                self.model.team_id == team_id,
                self.model.status == MeetingStatus.COMPLETED
            )
            .order_by(self.model.date.desc())
            .limit(1)
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_meeting_with_tasks(self, meeting_id: UUID) -> Optional[MeetingModel]:
        """Получить встречу с задачами"""
        from sqlalchemy.orm import selectinload
        
        query = (
            select(self.model)
            .where(self.model.id == meeting_id)
            .options(
                selectinload(self.model.meeting_tasks).selectinload(self.model.meeting_tasks.task)
            )
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


def meeting_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> MeetingRepository:
    repository = MeetingRepository(session)
    return repository