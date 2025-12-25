from uuid import UUID
from datetime import datetime
from fastapi import Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.application.services.base_service import BaseService
from app.application.dto.meeting import MeetingCreate, MeetingUpdate, MeetingResponse
from app.application.dto.task import TaskResponse
from app.domain.entities.meetings.meetings import Meeting
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
from app.domain.enums.meeting_status import MeetingStatus


class MeetingService(BaseService[MeetingModel, MeetingResponse]):
    orm_model = MeetingModel
    pyd_scheme = MeetingResponse

    def __init__(
        self,
        meeting_repo: MeetingRepository,
        task_repo: TaskRepository,
        meeting_task_repo: MeetingTaskRepository,
        team_repo: TeamRepository,
    ):
        super().__init__(meeting_repo)
        self._meeting_repo = meeting_repo
        self._task_repo = task_repo
        self._meeting_task_repo = meeting_task_repo
        self._team_repo = team_repo

    async def _validate_team_exists(self, team_id: UUID) -> None:
        """Проверить существование команды"""
        team = await self._team_repo.get_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Команда с ID {team_id} не найдена"
            )

    async def create(self, data: MeetingCreate) -> MeetingResponse:
        """Создать новую встречу"""
        # Проверяем существование команды
        await self._validate_team_exists(data.team_id)

        # Если указана предыдущая встреча, проверяем ее существование
        if data.previous_meeting_id:
            previous_meeting = await self._meeting_repo.get_by_id(data.previous_meeting_id)
            if not previous_meeting:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Предыдущая встреча с ID {data.previous_meeting_id} не найдена"
                )
            if previous_meeting.team_id != data.team_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Предыдущая встреча должна принадлежать той же команде"
                )

        # Создаем встречу
        meeting_data = data.model_dump(exclude_unset=True)
        orm_obj = MeetingModel(**meeting_data)
        created_obj = await self._repo.create(orm_obj)
        
        # Обновляем связь следующей встречи у предыдущей
        if data.previous_meeting_id:
            previous_meeting = await self._meeting_repo.get_by_id(data.previous_meeting_id)
            if previous_meeting:
                # Используем update метод репозитория для обновления
                await self._meeting_repo.update(
                    previous_meeting, 
                    {"next_meeting_id": created_obj.id}
                )

        return self._to_schema(created_obj)

    async def get_team_meetings(
        self, 
        team_id: UUID, 
        status: Optional[MeetingStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[MeetingResponse]:
        """Получить все встречи команды"""
        # Проверяем существование команды
        await self._validate_team_exists(team_id)

        meetings = await self._meeting_repo.get_by_team_id(
            team_id, status, from_date, to_date
        )
        return [self._to_schema(meeting) for meeting in meetings]

    async def get_meeting_with_tasks(self, meeting_id: UUID) -> MeetingResponse:
        """Получить встречу с задачами"""
        meeting = await self._meeting_repo.get_meeting_with_tasks(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Встреча с ID {meeting_id} не найдена"
            )
        return self._to_schema(meeting)

    async def complete_meeting(self, meeting_id: UUID) -> MeetingResponse:
        """Завершить встречу и перенести незавершенные задачи"""
        # Получаем встречу с задачами
        meeting = await self._meeting_repo.get_meeting_with_tasks(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Встреча с ID {meeting_id} не найдена"
            )

        if meeting.status == MeetingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Встреча уже завершена"
            )

        # Находим следующую запланированную встречу для этой команды
        next_meeting = await self._meeting_repo.get_upcoming_meeting(UUID(str(meeting.team_id)))
        
        # Если есть следующая встреча, переносим незавершенные задачи
        if next_meeting:
            # Получаем задачи текущей встречи
            from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
            
            query = (
                select(MeetingTaskModel)
                .where(MeetingTaskModel.meeting_id == meeting_id)
                .options(selectinload(MeetingTaskModel.task))
            )
            result = await self._meeting_repo.session.execute(query)
            meeting_tasks = result.scalars().all()
            
            # Переносим незавершенные задачи
            for meeting_task in meeting_tasks:
                if not meeting_task.task.is_completed:
                    # Создаем новую связь для следующей встречи
                    new_meeting_task = MeetingTaskModel(
                        meeting_id=next_meeting.id,
                        task_id=meeting_task.task.id
                    )
                    await self._meeting_task_repo.create(new_meeting_task)

        # Обновляем статус встречи
        meeting.status = MeetingStatus.COMPLETED
        await self._meeting_repo.session.commit()
        await self._meeting_repo.session.refresh(meeting)

        return self._to_schema(meeting)

    async def cancel_meeting(self, meeting_id: UUID) -> MeetingResponse:
        """Отменить встречу"""
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Встреча с ID {meeting_id} не найдена"
            )

        if meeting.status == MeetingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя отменить завершенную встречу"
            )

        meeting.status = MeetingStatus.CANCELED
        await self._meeting_repo.session.commit()
        await self._meeting_repo.session.refresh(meeting)

        return self._to_schema(meeting)

    async def get_meeting_tasks(self, meeting_id: UUID) -> List[TaskResponse]:
        """Получить задачи встречи"""
        # Проверяем существование встречи
        meeting = await self._meeting_repo.get_by_id(meeting_id)
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Встреча с ID {meeting_id} не найдена"
            )

        # Получаем задачи через репозиторий задач
        tasks = await self._task_repo.get_by_meeting_id(meeting_id)
        
        # Конвертируем в TaskResponse
        return [
            TaskResponse(
                id=task.id,
                description=task.description,
                is_completed=task.is_completed
            )
            for task in tasks
        ]

    async def update(
        self, new_data: MeetingUpdate, meeting_id: UUID
    ) -> MeetingResponse | None:
        """Обновить встречу"""
        old_obj = await self._meeting_repo.get_by_id(meeting_id)
        if not old_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Встреча с ID {meeting_id} не найдена"
            )

        update_data = new_data.model_dump(exclude_unset=True)
        updated_obj = await self._repo.update(old_obj, update_data)
        return self._to_schema(updated_obj)


def meeting_service_getter(
    meeting_repo: MeetingRepository = Depends(meeting_repository_getter),
    task_repo: TaskRepository = Depends(task_repository_getter),
    meeting_task_repo: MeetingTaskRepository = Depends(meeting_task_repository_getter),
    team_repo: TeamRepository = Depends(team_repository_getter),
) -> MeetingService:
    return MeetingService(meeting_repo, task_repo, meeting_task_repo, team_repo)