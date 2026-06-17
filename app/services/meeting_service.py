from uuid import UUID
from datetime import datetime
from fastapi import Depends, HTTPException, status
from typing import Optional
from itertools import chain

from app.schemas.common import ListResponse
from app.schemas.meeting import MeetingCreate, MeetingUpdate
from app.schemas.meeting import Meeting
from app.infrastructure.database.models.meetings.meeting import MeetingModel
from app.infrastructure.database.repositories.meeting_repository import (
    MeetingRepository,
    meeting_repository_getter,
)
from app.infrastructure.database.repositories.task_repository import (
    TaskRepository,
    task_repository_getter,
)
from app.infrastructure.database.repositories.meeting_task_repository import (
    MeetingTaskRepository,
    meeting_task_repository_getter,
)
from app.infrastructure.database.repositories.team_repository import (
    TeamRepository,
    team_repository_getter,
)
from app.infrastructure.database.repositories.project_applications.project_interviews_repository import (
    ProjectInterviewRepository,
    project_interview_repository_getter,
)
from app.common.enums import MeetingStatus


class MeetingService:
    """Application service for meetings."""

    def __init__(
        self,
        meeting_repo: MeetingRepository,
        task_repo: TaskRepository,
        meeting_task_repo: MeetingTaskRepository,
        team_repo: TeamRepository,
        interview_repo: ProjectInterviewRepository,
    ):
        self._meeting_repo = meeting_repo
        self._task_repo = task_repo
        self._meeting_task_repo = meeting_task_repo
        self._team_repo = team_repo
        self._interview_repo = interview_repo

    def _to_orm(self, scheme: MeetingCreate) -> MeetingModel:
        """Convert schema to ORM model."""
        return MeetingModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: MeetingModel) -> Meeting:
        """Convert ORM model to schema."""
        return Meeting.model_validate(orm_model, from_attributes=True)

    async def _validate_team_exists(self, team_id: UUID) -> None:
        """Check team existence."""
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with ID {team_id} not found",
            )

    async def _ensure_unique_meeting_time(
        self,
        team_id: UUID,
        meeting_date: datetime,
        exclude_meeting_id: Optional[UUID] = None,
    ) -> None:
        """Ensure no other meeting exists for the team at the same date/time."""
        if await self._meeting_repo.exists_by_team_and_date(
            team_id,
            meeting_date,
            exclude_id=exclude_meeting_id,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meeting time must be unique within the team",
            )

    async def create(self, create_meeting_data: MeetingCreate) -> Meeting:
        """Create new meeting and automatically insert it into the meeting chain by date."""
        await self._validate_team_exists(create_meeting_data.team_id)

        await self._ensure_unique_meeting_time(
            create_meeting_data.team_id,
            create_meeting_data.date,
        )

        meeting_data = create_meeting_data.model_dump(exclude_unset=True)
        meeting_data.pop("previous_meeting_id", None)
        meeting_data.pop("next_meeting_id", None)

        orm_obj = MeetingModel(**meeting_data)
        created_obj = await self._meeting_repo.create(orm_obj)

        previous, next_ = await self._meeting_repo.find_neighbours(
            create_meeting_data.team_id, create_meeting_data.date
        )

        if previous or next_:
            await self._chain_meetings(
                current_id=created_obj.id,
                previous_id=previous.id if previous else None,
                next_id=next_.id if next_ else None,
            )
            created_obj = await self._meeting_repo.get_by_id(created_obj.id)

        return self._to_schema(created_obj)

    async def _chain_meetings(
        self, current_id: UUID, previous_id: Optional[UUID], next_id: Optional[UUID]
    ) -> None:
        """Chain meetings together, handling insertion into existing chains."""
        current = await self._meeting_repo.get_by_id(current_id)
        if not current:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {current_id} not found",
            )

        # If there's a previous meeting
        if previous_id:
            previous = await self._meeting_repo.get_by_id(previous_id)
            if not previous:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Previous meeting with ID {previous_id} not found",
                )

            # Validate team and date
            if previous.team_id != current.team_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Previous meeting must belong to the same team",
                )
            if previous.date >= current.date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Previous meeting date must be earlier than current meeting",
                )

            # If previous meeting had a next meeting, link it to current
            old_next_id = previous.next_meeting_id
            if old_next_id and old_next_id != next_id:
                old_next = await self._meeting_repo.get_by_id(old_next_id)
                if old_next:
                    await self._meeting_repo.update(
                        old_next, {"previous_meeting_id": current_id}
                    )
                    if not next_id:
                        next_id = old_next_id

            # Link previous to current
            await self._meeting_repo.update(
                current, {"previous_meeting_id": previous_id}
            )
            await self._meeting_repo.update(previous, {"next_meeting_id": current_id})

        # If there's a next meeting
        if next_id:
            next_meeting = await self._meeting_repo.get_by_id(next_id)
            if not next_meeting:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Next meeting with ID {next_id} not found",
                )

            # Validate team and date
            if next_meeting.team_id != current.team_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Next meeting must belong to the same team",
                )
            if next_meeting.date <= current.date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Next meeting date must be later than current meeting",
                )

            # If next meeting had a previous meeting and it's not our previous, unlink it
            old_previous_id = next_meeting.previous_meeting_id
            if old_previous_id and old_previous_id != previous_id:
                old_previous = await self._meeting_repo.get_by_id(old_previous_id)
                if old_previous:
                    await self._meeting_repo.update(
                        old_previous, {"next_meeting_id": current_id}
                    )

            # Link current to next
            await self._meeting_repo.update(current, {"next_meeting_id": next_id})
            await self._meeting_repo.update(
                next_meeting, {"previous_meeting_id": current_id}
            )

    async def _unchain_meeting(self, meeting: MeetingModel) -> None:
        """Remove meeting from chain, linking its neighbours directly to each other."""
        previous_id = meeting.previous_meeting_id
        next_id = meeting.next_meeting_id

        if previous_id:
            previous = await self._meeting_repo.get_by_id(previous_id)
            if previous:
                await self._meeting_repo.update(previous, {"next_meeting_id": next_id})

        if next_id:
            next_meeting = await self._meeting_repo.get_by_id(next_id)
            if next_meeting:
                await self._meeting_repo.update(
                    next_meeting, {"previous_meeting_id": previous_id}
                )

    async def update(self, meeting_id: UUID, new_data: MeetingUpdate) -> Meeting | None:
        """Update meeting."""
        old_obj = await self._meeting_repo.get_by_id(meeting_id)
        if not old_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {meeting_id} not found",
            )

        update_data = new_data.model_dump(exclude_unset=True)

        if "date" in update_data:
            await self._ensure_unique_meeting_time(
                old_obj.team_id,
                update_data["date"],
                exclude_meeting_id=meeting_id,
            )

        if update_data:
            updated_obj = await self._meeting_repo.update(old_obj, update_data)
        else:
            updated_obj = await self._meeting_repo.get_by_id(meeting_id)

        return self._to_schema(updated_obj)

    async def delete(self, meeting_id: UUID) -> bool:
        """Delete meeting and relink its neighbours."""
        obj = await self._meeting_repo.get_by_id(meeting_id)
        if not obj:
            return False
        await self._unchain_meeting(obj)
        await self._meeting_repo.delete(obj)
        return True

    async def get_by_id(self, meeting_id: UUID) -> Meeting | None:
        """Get meeting by ID."""
        obj = await self._meeting_repo.get_by_id(meeting_id)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_list(
        self,
        team_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> ListResponse[Meeting]:
        total, items = await self._meeting_repo.get_list(
            filters={"team_id": team_id},
            range_filters={"date": (start_date, end_date)},
            order_by="date",
        )
        return ListResponse(
            total=total,
            items=[self._to_schema(i) for i in items],
        )

    async def get_list_with_interviews(
        self,
        team_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> ListResponse[Meeting]:
        total, items = await self._meeting_repo.get_list(
            filters={"team_id": team_id},
            range_filters={"date": (start_date, end_date)},
            order_by="date",
        )
        total_interviews, items_interviews = await self._interview_repo.get_list(
            range_filters={"date": (start_date, end_date)},
            order_by="date",
        )
        return ListResponse(
            total=total + total_interviews,
            items=[self._to_schema(i) for i in chain(items, items_interviews)],
        )

    async def cancel_meeting(self, meeting_id: UUID) -> Meeting:
        """Cancel meeting."""
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {meeting_id} not found",
            )

        if meeting.status == MeetingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel completed meeting",
            )

        meeting.status = MeetingStatus.CANCELED
        await self._meeting_repo.session.commit()
        await self._meeting_repo.session.refresh(meeting)

        return self._to_schema(meeting)


def meeting_service_getter(
    meeting_repo: MeetingRepository = Depends(meeting_repository_getter),
    task_repo: TaskRepository = Depends(task_repository_getter),
    meeting_task_repo: MeetingTaskRepository = Depends(meeting_task_repository_getter),
    team_repo: TeamRepository = Depends(team_repository_getter),
    interview_repo: ProjectInterviewRepository = Depends(
        project_interview_repository_getter
    ),
) -> MeetingService:
    return MeetingService(
        meeting_repo, task_repo, meeting_task_repo, team_repo, interview_repo
    )
