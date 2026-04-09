from typing import Sequence, Optional
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


def meeting_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> MeetingRepository:
    repository = MeetingRepository(session)
    return repository