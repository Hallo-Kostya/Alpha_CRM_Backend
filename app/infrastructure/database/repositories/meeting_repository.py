from typing import Sequence, Optional, List, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sqlalchemy.orm import selectinload

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.meetings.meeting import MeetingModel
from app.infrastructure.database.database import db_helper


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
        
    async def exists_by_team_and_date(
        self,
        team_id: UUID,
        meeting_date: datetime,
        exclude_id: Optional[UUID] = None,
    ) -> bool:
        """Check whether a meeting exists for the team at the same date/time."""
        query = select(func.count()).where(
            MeetingModel.team_id == team_id,
            MeetingModel.date == meeting_date,
        )
        if exclude_id is not None:
            query = query.where(MeetingModel.id != exclude_id)

        result = await self.session.execute(query)
        return result.scalar_one() > 0

    async def find_neighbours(
        self, team_id: UUID, meeting_date: datetime
    ) -> tuple[MeetingModel | None, MeetingModel | None]:
        """Find the closest previous and next meetings by date for a given team."""
        prev_query = (
            select(MeetingModel)
            .where(
                MeetingModel.team_id == team_id,
                MeetingModel.date < meeting_date,
            )
            .order_by(MeetingModel.date.desc())
            .limit(1)
        )
        next_query = (
            select(MeetingModel)
            .where(
                MeetingModel.team_id == team_id,
                MeetingModel.date > meeting_date,
            )
            .order_by(MeetingModel.date.asc())
            .limit(1)
        )

        prev_result = await self.session.execute(prev_query)
        next_result = await self.session.execute(next_query)

        return prev_result.scalar_one_or_none(), next_result.scalar_one_or_none()


def meeting_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> MeetingRepository:
    repository = MeetingRepository(session)
    return repository