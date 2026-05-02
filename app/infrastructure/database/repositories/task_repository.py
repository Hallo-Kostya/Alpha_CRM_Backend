from typing import Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import Depends

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.meetings.task import TaskModel
from app.core.database import db_helper


class TaskRepository(BaseRepository[TaskModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(TaskModel, session)

    async def get_by_meeting_id(self, meeting_id: UUID) -> Sequence[TaskModel]:
        """Get all tasks for a specific meeting."""
        query = (
            select(TaskModel)
            .join(TaskModel.meeting_tasks)
            .where(TaskModel.meeting_tasks.any(meeting_id=meeting_id))
            .options(selectinload(TaskModel.meeting_tasks))
        )
        result = await self.session.execute(query)
        return result.scalars().all()


def task_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> TaskRepository:
    repository = TaskRepository(session)
    return repository