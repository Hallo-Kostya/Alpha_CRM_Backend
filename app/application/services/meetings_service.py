from uuid import UUID
from typing import List

from app.domain.entities.meetings.meetings import Meeting
from app.infrastructure.database.repositories.base_repository import CRUDRepository
from app.infrastructure.database.models.meetings.meeting import (
    MeetingModel,
)  # предполагаем


class MeetingService:
    def __init__(
        self,
        meeting_repo: CRUDRepository[Meeting, MeetingModel],
    ) -> None:
        self._repo = meeting_repo

    async def create_meeting(self, meeting: Meeting) -> Meeting:
        return await self._repo.create(meeting)

    async def get_meeting(self, meeting_id: UUID) -> Meeting | None:
        return await self._repo.get(meeting_id)

    async def update_meeting(self, meeting: Meeting) -> Meeting:
        return await self._repo.update(meeting)

    async def delete_meeting(self, meeting_id: UUID) -> None:
        await self._repo.delete(meeting_id)

    async def list_meetings(self) -> List[Meeting]:
        return await self._repo.list()
