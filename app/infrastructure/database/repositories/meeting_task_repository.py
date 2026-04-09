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


def meeting_task_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> MeetingTaskRepository:
    repository = MeetingTaskRepository(session)
    return repository