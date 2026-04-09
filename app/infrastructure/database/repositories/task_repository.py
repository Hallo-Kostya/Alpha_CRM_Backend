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


def task_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> TaskRepository:
    repository = TaskRepository(session)
    return repository