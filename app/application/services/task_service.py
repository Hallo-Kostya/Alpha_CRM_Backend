from uuid import UUID
from fastapi import Depends, HTTPException, status
from typing import List

from app.application.services.base_service import BaseService
from app.application.dto.task import TaskCreate, TaskUpdate, TaskResponse
from app.domain.entities.meetings.task import Task
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


class TaskService(BaseService[TaskModel, TaskResponse]):
    orm_model = TaskModel
    pyd_scheme = TaskResponse

    def __init__(
        self,
        task_repo: TaskRepository,
        meeting_repo: MeetingRepository,
        meeting_task_repo: MeetingTaskRepository,
    ):
        super().__init__(task_repo)
        self._task_repo = task_repo
        self._meeting_repo = meeting_repo
        self._meeting_task_repo = meeting_task_repo

    async def create(self, data: TaskCreate) -> TaskResponse:
        """Создать новую задачу"""
        orm_obj = TaskModel(**data.model_dump(exclude_unset=True))
        created_obj = await self._repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def create_for_meeting(
        self, meeting_id: UUID, data: TaskCreate
    ) -> TaskResponse:
        """Создать задачу и привязать ее к встрече"""
        # Проверяем существование встречи
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Встреча с ID {meeting_id} не найдена"
            )

        # Создаем задачу
        task = await self.create(data)
        
        # Привязываем задачу к встрече
        from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
        
        meeting_task = MeetingTaskModel(
            meeting_id=meeting_id,
            task_id=task.id
        )
        await self._meeting_task_repo.create(meeting_task)

        return task

    async def update(
        self, new_data: TaskUpdate, task_id: UUID
    ) -> TaskResponse | None:
        """Обновить задачу"""
        old_obj = await self._repo.get_by_id(task_id)
        if not old_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Задача с ID {task_id} не найдена"
            )

        update_data = new_data.model_dump(exclude_unset=True)
        updated_obj = await self._repo.update(old_obj, update_data)
        return self._to_schema(updated_obj)

    async def complete_task(self, task_id: UUID) -> TaskResponse:
        """Отметить задачу как выполненную"""
        task = await self._repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Задача с ID {task_id} не найдена"
            )

        if task.is_completed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Задача уже выполнена"
            )

        task.is_completed = True
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