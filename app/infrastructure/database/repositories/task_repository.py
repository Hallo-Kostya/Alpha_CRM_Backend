from typing import Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models.meetings.task import TaskModel
from app.core.database import db_helper


class TaskRepository(BaseRepository[TaskModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(TaskModel, session)

    async def get_by_meeting_id(self, meeting_id: UUID) -> Sequence[TaskModel]:
        """Получить все задачи встречи"""
        from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
        
        query = (
            select(TaskModel)
            .join(MeetingTaskModel, TaskModel.id == MeetingTaskModel.task_id)
            .where(MeetingTaskModel.meeting_id == meeting_id)
        )
        
        result = await self.session.scalars(query)
        return result.all()

    async def get_incomplete_tasks_by_team(self, team_id: UUID) -> Sequence[TaskModel]:
        """Получить незавершенные задачи команды"""
        from app.infrastructure.database.models.meetings.meeting import MeetingModel
        from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
        
        query = (
            select(TaskModel)
            .join(MeetingTaskModel, TaskModel.id == MeetingTaskModel.task_id)
            .join(MeetingModel, MeetingTaskModel.meeting_id == MeetingModel.id)
            .where(
                MeetingModel.team_id == team_id,
                TaskModel.is_completed == False
            )
            .distinct()
        )
        
        result = await self.session.scalars(query)
        return result.all()


def task_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> TaskRepository:
    repository = TaskRepository(session)
    return repository