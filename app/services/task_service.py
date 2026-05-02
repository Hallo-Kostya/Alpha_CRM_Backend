from uuid import UUID
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from app.schemas.task import TaskCreate, TaskUpdate, Task
from app.infrastructure.database.models.meetings.task import TaskModel
from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
from app.infrastructure.database.repositories.task_repository import (
    TaskRepository,
    task_repository_getter,
)
from app.infrastructure.database.repositories.meeting_task_repository import (
    MeetingTaskRepository,
    meeting_task_repository_getter,
)
from app.infrastructure.database.repositories.meeting_repository import (
    MeetingRepository,
    meeting_repository_getter,
)


class TaskService:
    """Application service for tasks."""

    def __init__(
        self,
        task_repo: TaskRepository,
        meeting_task_repo: MeetingTaskRepository,
        meeting_repo: MeetingRepository,
    ):
        self._task_repo = task_repo
        self._meeting_task_repo = meeting_task_repo
        self._meeting_repo = meeting_repo

    def _to_schema(self, orm_model: TaskModel) -> Task:
        """Convert ORM model to schema."""
        return Task.model_validate(orm_model, from_attributes=True)

    async def create(self, data: TaskCreate) -> Task:
        """Create new task."""
        orm_obj = TaskModel(**data.model_dump())
        created_obj = await self._task_repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def get_by_id(self, task_id: UUID) -> Task | None:
        """Get task by ID."""
        obj = await self._task_repo.get_by_id(task_id)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_list(self, meeting_id: Optional[UUID] = None) -> List[Task]:
        """Get list of tasks, optionally filtered by meeting."""
        if meeting_id:
            items = await self._task_repo.get_by_meeting_id(meeting_id)
        else:
            total, items = await self._task_repo.get_list()
        return [self._to_schema(item) for item in items]

    async def update(self, task_id: UUID, new_data: TaskUpdate) -> Task | None:
        """Update task (description and completion status can be updated)."""
        old_obj = await self._task_repo.get_by_id(task_id)
        if not old_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )

        update_data = new_data.model_dump(exclude_unset=True)

        if update_data:
            updated_obj = await self._task_repo.update(old_obj, update_data)
        else:
            updated_obj = old_obj

        return self._to_schema(updated_obj)

    async def delete(self, task_id: UUID) -> bool:
        """Delete task."""
        obj = await self._task_repo.get_by_id(task_id)
        if not obj:
            return False
        await self._task_repo.delete(obj)
        return True

    async def move_to_next_meeting(self, task_id: UUID) -> Task:
        """Move incomplete task to the next meeting of the same team."""
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )

        if task.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot move completed task"
            )

        # Find current meeting for this task
        query = select(MeetingTaskModel).where(MeetingTaskModel.task_id == task_id)
        result = await self._meeting_task_repo.session.execute(query)
        meeting_task = result.scalar_one_or_none()

        if not meeting_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task is not assigned to any meeting"
            )

        current_meeting = await self._meeting_repo.get_by_id(meeting_task.meeting_id)
        if not current_meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Current meeting not found"
            )

        # Find next meeting for the same team
        next_meeting = await self._meeting_repo.get_by_id(current_meeting.next_meeting_id)
        if not next_meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No upcoming meeting found for this team"
            )

        # Create new meeting-task relationship
        new_meeting_task = MeetingTaskModel(
            meeting_id=next_meeting.id,
            task_id=task_id
        )
        await self._meeting_task_repo.create(new_meeting_task)

        return self._to_schema(task)

    async def add_to_meeting(self, task_id: UUID, meeting_id: UUID) -> None:
        """Add existing task to a meeting."""
        # Check if task exists
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )

        # Check if meeting exists
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {meeting_id} not found"
            )

        query = select(MeetingTaskModel).where(
            MeetingTaskModel.task_id == task_id,
            MeetingTaskModel.meeting_id == meeting_id
        )
        result = await self._meeting_task_repo.session.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is already assigned to this meeting"
            )

        # Create relationship
        meeting_task = MeetingTaskModel(
            meeting_id=meeting_id,
            task_id=task_id
        )
        await self._meeting_task_repo.create(meeting_task)

    async def remove_from_meeting(self, task_id: UUID, meeting_id: UUID) -> None:
        """Remove task from a meeting (delete the relationship)."""
        # Check if task exists
        task = await self._task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )

        # Check if meeting exists
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {meeting_id} not found"
            )

        # Delete the relationship
        from sqlalchemy import delete
        await self._meeting_task_repo.session.execute(
            delete(MeetingTaskModel).where(
                MeetingTaskModel.task_id == task_id,
                MeetingTaskModel.meeting_id == meeting_id
            )
        )
        await self._meeting_task_repo.session.commit()


def task_service_getter(
    task_repo: TaskRepository = Depends(task_repository_getter),
    meeting_task_repo: MeetingTaskRepository = Depends(meeting_task_repository_getter),
    meeting_repo: MeetingRepository = Depends(meeting_repository_getter),
) -> TaskService:
    return TaskService(task_repo, meeting_task_repo, meeting_repo)