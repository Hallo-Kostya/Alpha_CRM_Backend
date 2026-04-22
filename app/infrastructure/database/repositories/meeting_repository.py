from typing import Sequence, Optional, List, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.orm import selectinload

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.meetings.meeting import MeetingModel
from app.common.enums import MeetingStatus
from app.core.database import db_helper


class MeetingRepository(BaseRepository[MeetingModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(MeetingModel, session)

    async def get_meetings_for_calendar(self, team_id: Optional[UUID] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
        """Получить встречи для календаря с фильтрами по команде и датам."""
        query = select(
            MeetingModel.id,
            MeetingModel.name,
            MeetingModel.resume,
            MeetingModel.date,
            MeetingModel.status,
            MeetingModel.team_id
        ).select_from(MeetingModel)

        if team_id:
            query = query.where(MeetingModel.team_id == team_id)
        if start_date:
            query = query.where(MeetingModel.date >= start_date)
        if end_date:
            query = query.where(MeetingModel.date <= end_date)

        query = query.order_by(MeetingModel.date)

        result = await self.session.execute(query)
        rows = result.all()

        return [
            {
                "id": row.id,
                "name": row.name,
                "resume": row.resume,
                "date": row.date,
                "status": row.status,
                "team_id": row.team_id
            }
            for row in rows
        ]


def meeting_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> MeetingRepository:
    repository = MeetingRepository(session)
    return repository