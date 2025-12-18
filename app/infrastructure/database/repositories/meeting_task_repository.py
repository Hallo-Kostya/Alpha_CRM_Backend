from typing import Sequence, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
from app.core.database import db_helper


class MeetingTaskRepository(BaseRepository[MeetingTaskModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(MeetingTaskModel, session)

    async def get_by_meeting_and_task(
        self, meeting_id: UUID, task_id: UUID
    ) -> Optional[MeetingTaskModel]:
        """Найти связь по встрече и задаче"""
        query = select(self.model).where(
            self.model.meeting_id == meeting_id,
            self.model.task_id == task_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_meeting_id(self, meeting_id: UUID) -> Sequence[MeetingTaskModel]:
        """Получить все связи для встречи"""
        query = select(self.model).where(self.model.meeting_id == meeting_id)
        result = await self.session.scalars(query)
        return result.all()

    async def get_by_task_id(self, task_id: UUID) -> Sequence[MeetingTaskModel]:
        """Получить все связи для задачи"""
        query = select(self.model).where(self.model.task_id == task_id)
        result = await self.session.scalars(query)
        return result.all()

    async def delete_by_meeting_and_task(
        self, meeting_id: UUID, task_id: UUID
    ) -> bool:
        """Удалить связь по встрече и задаче"""
        meeting_task = await self.get_by_meeting_and_task(meeting_id, task_id)
        if not meeting_task:
            return False
        
        await self.session.delete(meeting_task)
        await self.session.commit()
        return True


def meeting_task_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> MeetingTaskRepository:
    repository = MeetingTaskRepository(session)
    return repository