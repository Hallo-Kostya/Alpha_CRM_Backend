from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from app.api.dependencies import get_current_curator
from app.schemas.meeting import MeetingCreate, MeetingUpdate, Meeting
from app.schemas.task import TaskCreate, TaskResponse
from app.infrastructure.database.models.meetings.meeting_task import MeetingTaskModel
from app.services.meeting_service import (
    MeetingService,
    meeting_service_getter,
)
from app.services.task_service import (
    TaskService,
    task_service_getter,
)

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
    responses={404: {"description": "Meeting not found"}},
    dependencies=[Depends(get_current_curator)],
)


@router.post("/", response_model=Meeting, summary="Создать встречу",status_code=status.HTTP_201_CREATED)
async def create_meeting(
    data: MeetingCreate,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Создать новую встречу для команды."""
    return await service.create(data)


@router.get("/", summary="Получить встречи для календаря")
async def get_meetings_for_calendar(
    team_id: Optional[UUID] = Query(None, description="ID команды"),
    start_date: Optional[datetime] = Query(None, description="Начальная дата"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата"),
    service: MeetingService = Depends(meeting_service_getter),
):
    """Получить список встреч для отображения в календаре с фильтрами по команде и датам."""
    return await service.get_list(team_id, start_date, end_date)


@router.get("/{meeting_id}", response_model=Meeting, summary="Получить встречу по ID")
async def get_meeting(
    meeting_id: UUID,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Получить детальную информацию о встрече."""
    meeting = await service.get_by_id(meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Встреча с ID {meeting_id} не найдена",
        )
    return meeting


@router.patch("/{meeting_id}", response_model=Meeting, summary="Обновить встречу")
async def update_meeting(
    meeting_id: UUID,
    data: MeetingUpdate,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Обновить данные встречи."""
    return await service.update(meeting_id, data)


@router.delete("/{meeting_id}", summary="Удалить встречу")
async def delete_meeting(
    meeting_id: UUID,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Удалить встречу."""
    deleted = await service.delete(meeting_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Встреча с ID {meeting_id} не найдена для удаления",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{meeting_id}/tasks", response_model=TaskResponse, summary="Добавить задачу к встрече", status_code=status.HTTP_201_CREATED)
async def add_task_to_meeting(
    meeting_id: UUID,
    task_data: TaskCreate,
    meeting_service: MeetingService = Depends(meeting_service_getter),
    task_service: TaskService = Depends(task_service_getter),
):
    """Добавить задачу к встрече. Если задача с таким описанием уже существует, она будет привязана к встрече."""
    # Check if meeting exists
    meeting = await meeting_service.get_by_id(meeting_id)
    if meeting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Встреча с ID {meeting_id} не найдена",
        )
    
    # Create task
    task = await task_service.create(task_data)
    
    # Add task to meeting
    await task_service.add_to_meeting(task.id, meeting_id)

    return TaskResponse(
        id=task.id,
        description=task.description,
        is_completed=task.is_completed
    )


@router.delete("/{meeting_id}/tasks/{task_id}", summary="Убрать задачу со встречи", status_code=status.HTTP_204_NO_CONTENT)
async def remove_task_from_meeting(
    meeting_id: UUID,
    task_id: UUID,
    task_service: TaskService = Depends(task_service_getter),
):
    """Убрать задачу со встречи (не удаляет саму задачу, только связь)."""
    await task_service.remove_from_meeting(task_id, meeting_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
