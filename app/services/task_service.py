from uuid import UUID
from fastapi import Depends, HTTPException, status
from typing import List

from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.task import Task
from app.infrastructure.database.models.meetings.task import TaskModel
from app.infrastructure.database.repositories.task_repository import (
    TaskRepository,
    task_repository_getter,
)
from app.infrastructure.database.repositories.meeting_repository import (
    MeetingRepository,
    meeting_repository_getter,
)
from app.infrastructure.database.repositories.meeting_task_repository import (
    MeetingTaskRepository,
    meeting_task_repository_getter,
)


class TaskService:
    """Application service for tasks."""

    def __init__(
        self,
        task_repo: TaskRepository,
        meeting_repo: MeetingRepository,
       meeting_task_repo: MeetingTaskRepository,
    ):
        self._task_repo = task_repo
        self._meeting_repo = meeting_repo
        self._meeting_task_repo = meeting_task_repo

    def _to_orm(self, scheme: TaskCreate) -> TaskModel:
        """Convert schema to ORM model."""
        return TaskModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: TaskModel) -> Task:
        """Convert ORM model to schema."""
        return Task.model_validate(orm_model, from_attributes=True)

    async def create(self, data: TaskCreate) -> Task:
        """Create new task."""
        orm_obj = TaskModel(**data.model_dump(exclude_unset=True))
        created_obj = await self._repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def create_for_meeting(
        self, meeting_id: UUID, data: TaskCreate
    ) -> Task:
        """Create task and attach it to meeting."""
        # Check meeting existence
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Meeting with ID {meeting_id} not found"
            )

        # Create task
        task = await self.create(data)
        
        # Attach task to meeting
        from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
        
        meeting_task = MeetingTaskModel(
            meeting_id=meeting_id,
            task_id=task.id
        )
        await self._meeting_task_repo.create(meeting_task)

        return task

    async def update(
        self, task_id: UUID, new_data: TaskUpdate
    ) -> Task | None:
        """Update task."""
        old_obj = await self._repo.get_by_id(task_id)
        if not old_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )

        update_data = new_data.model_dump(exclude_unset=True)
        updated_obj = await self._repo.update(old_obj, update_data)
        return self._to_schema(updated_obj)

    async def delete(self, task_id: UUID) -> bool:
        """Delete task."""
        obj = await self._repo.get_by_id(task_id)
        if not obj:
            return False
        await self._repo.delete(obj)
        return True

    async def get_by_id(self, task_id: UUID) -> Task | None:
        """Get task by ID."""
        obj = await self._repo.get_by_id(task_id)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_list(self, **filter_attrs) -> List[Task]:
        """Get list of tasks."""
        items = await self._repo.get_list(**filter_attrs)
        return [self._to_schema(item) for item in items]

    async def complete_task(self, task_id: UUID) -> Task:
        """Mark task as completed."""
        task = await self._repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )

        if task.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task is already completed"
            )

        task.is_completed = True
        updated_task = await self._repo.update(task, {"is_completed": True})
        return self._to_schema(updated_task)
        await self._repo.session.commit()
        await self._repo.session.refresh(task)

        return self._to_schema(task)

    async def get_team_incomplete_tasks(self, team_id: UUID) -> List[TaskResponse]:
        """Получить незавершенные задачи команды"""
        tasks = await self._task_repo.get_incomplete_tasks_by_team(team_id)
        return [self._to_schema(task) for task in tasks]

    async def add_task_to_meeting(
        self, meeting_id: UUID, task_id: UUID
    ) -> bool:
        """Добавить существующую задачу в встречу"""
        # Проверяем существование встречи
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Встреча с ID {meeting_id} не найдена"
            )

        # Проверяем существование задачи
        task = await self._repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Задача с ID {task_id} не найдена"
            )

        # Проверяем, не привязана ли уже задача к этой встрече
        existing = await self._meeting_task_repo.get_by_meeting_and_task(meeting_id, task_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Задача уже добавлена в эту встречу"
            )

        # Создаем связь
        from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
        
        meeting_task = MeetingTaskModel(
            meeting_id=meeting_id,
            task_id=task_id
        )
        await self._meeting_task_repo.create(meeting_task)

        return True

    async def remove_task_from_meeting(
        self, meeting_id: UUID, task_id: UUID
    ) -> bool:
        """Удалить задачу из встречи"""
        deleted = await self._meeting_task_repo.delete_by_meeting_and_task(meeting_id, task_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь между встречей и задачей не найдена"
            )
        return True


def task_service_getter(
    task_repo: TaskRepository = Depends(task_repository_getter),
    meeting_repo: MeetingRepository = Depends(meeting_repository_getter),
    meeting_task_repo: MeetingTaskRepository = Depends(meeting_task_repository_getter),
) -> TaskService:
    return TaskService(task_repo, meeting_repo, meeting_task_repo)