from uuid import UUID
from datetime import datetime
from fastapi import Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.schemas.meeting import MeetingCreate, MeetingUpdate, MeetingResponse
from app.schemas.task import TaskResponse
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
from app.common.enums import MeetingStatus


class MeetingService:
    """Application service for meetings."""

    def __init__(
        self,
        meeting_repo: MeetingRepository,
        task_repo: TaskRepository,
        meeting_task_repo: MeetingTaskRepository,
        team_repo: TeamRepository,
    ):
        self._meeting_repo = meeting_repo
        self._task_repo = task_repo
        self._meeting_task_repo = meeting_task_repo
        self._team_repo = team_repo

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
                detail=f"Team with ID {team_id} not found"
            )

    async def create(self, data: MeetingCreate) -> Meeting:
        """Create new meeting."""
        # Check team existence
        await self._validate_team_exists(data.team_id)

        # Check previous meeting if specified
        if data.previous_meeting_id:
            previous_meeting = await self._meeting_repo.get_by_id(data.previous_meeting_id)
            if not previous_meeting:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Previous meeting with ID {data.previous_meeting_id} not found"
                )
            if previous_meeting.team_id != data.team_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Previous meeting must belong to the same team"
                )

        # Create meeting
        meeting_data = data.model_dump(exclude_unset=True)
        orm_obj = MeetingModel(**meeting_data)
        created_obj = await self._repo.create(orm_obj)
        
        # Update next_meeting_id for previous meeting
        if data.previous_meeting_id:
            previous_meeting = await self._meeting_repo.get_by_id(data.previous_meeting_id)
            if previous_meeting:
                await self._meeting_repo.update(
                    previous_meeting, 
                    {"next_meeting_id": created_obj.id}
                )

        return self._to_schema(created_obj)

    async def update(
        self, meeting_id: UUID, new_data: MeetingUpdate
    ) -> Meeting | None:
        """Update meeting."""
        old_obj = await self._meeting_repo.get_by_id(meeting_id)
        if not old_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {meeting_id} not found"
            )

        update_data = new_data.model_dump(exclude_unset=True)
        updated_obj = await self._repo.update(old_obj, update_data)
        return self._to_schema(updated_obj)

    async def delete(self, meeting_id: UUID) -> bool:
        """Delete meeting."""
        obj = await self._repo.get_by_id(meeting_id)
        if not obj:
            return False
        await self._repo.delete(obj)
        return True

    async def get_by_id(self, meeting_id: UUID) -> Meeting | None:
        """Get meeting by ID."""
        obj = await self._repo.get_by_id(meeting_id)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_list(self, **filter_attrs) -> List[Meeting]:
        """Get list of meetings."""
        items = await self._repo.get_list(**filter_attrs)
        return [self._to_schema(item) for item in items]

    async def get_team_meetings(
        self, 
        team_id: UUID, 
        meeting_status: Optional[MeetingStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Meeting]:
        """Get all meetings of team."""
        # Check team existence
        await self._validate_team_exists(team_id)

        meetings = await self._meeting_repo.get_by_team_id(
            team_id, meeting_status, from_date, to_date
        )
        return [self._to_schema(meeting) for meeting in meetings]
    
    async def get_all_meetings(self) -> List[Meeting]:
        """Get all meetings ordered by date."""
        meetings = await self._meeting_repo.get_all_ordered_by_date()
        return [self._to_schema(meeting) for meeting in meetings]

    async def complete_meeting(self, meeting_id: UUID) -> Meeting:
        """Complete meeting and move incomplete tasks."""
        # Get meeting with tasks
        meeting = await self._meeting_repo.get_meeting_with_tasks(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {meeting_id} not found"
            )

        if meeting.status == MeetingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meeting is already completed"
            )

        # Find next scheduled meeting for this team
        next_meeting = await self._meeting_repo.get_upcoming_meeting(UUID(str(meeting.team_id)))
        
        # If there's next meeting, move incomplete tasks
        if next_meeting:
            from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
            
            query = (
                select(MeetingTaskModel)
                .where(MeetingTaskModel.meeting_id == meeting_id)
                .options(selectinload(MeetingTaskModel.task))
            )
            result = await self._meeting_repo.session.execute(query)
            meeting_tasks = result.scalars().all()
            
            # Move incomplete tasks
            for meeting_task in meeting_tasks:
                if not meeting_task.task.is_completed:
                    new_meeting_task = MeetingTaskModel(
                        meeting_id=next_meeting.id,
                        task_id=meeting_task.task.id
                    )
                    await self._meeting_task_repo.create(new_meeting_task)

        # Update meeting status
        meeting.status = MeetingStatus.COMPLETED
        await self._meeting_repo.session.commit()
        await self._meeting_repo.session.refresh(meeting)

        return self._to_schema(meeting)

    async def cancel_meeting(self, meeting_id: UUID) -> Meeting:
        """Cancel meeting."""
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {meeting_id} not found"
            )

        if meeting.status == MeetingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel completed meeting"
            )

        meeting.status = MeetingStatus.CANCELED
        await self._meeting_repo.session.commit()
        await self._meeting_repo.session.refresh(meeting)

        return self._to_schema(meeting)

    async def get_meeting_tasks(self, meeting_id: UUID) -> List[TaskResponse]:
        """Get meeting tasks."""
        # Check meeting existence
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {meeting_id} not found"
            )

        # Get tasks
        tasks = await self._task_repo.get_by_meeting_id(meeting_id)
        
        # Convert to TaskResponse
        return [
            TaskResponse(
                id=task.id,
                description=task.description,
                is_completed=task.is_completed
            )
            for task in tasks
        ]


def meeting_service_getter(
    meeting_repo: MeetingRepository = Depends(meeting_repository_getter),
    task_repo: TaskRepository = Depends(task_repository_getter),
    meeting_task_repo: MeetingTaskRepository = Depends(meeting_task_repository_getter),
    team_repo: TeamRepository = Depends(team_repository_getter),
) -> MeetingService:
    return MeetingService(meeting_repo, task_repo, meeting_task_repo, team_repo)