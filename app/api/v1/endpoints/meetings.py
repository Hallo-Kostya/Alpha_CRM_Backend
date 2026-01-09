from uuid import UUID
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.application.dto.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
)
from app.application.dto.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    MeetingTaskCreate,
)
from app.application.services.meeting_service import (
    MeetingService,
    meeting_service_getter,
)
from app.application.services.task_service import (
    TaskService,
    task_service_getter,
)
from app.domain.enums.meeting_status import MeetingStatus

router = APIRouter(
    prefix="/meetings",
    tags=["meetings"],
    responses={404: {"description": "Meeting not found"}},
)


@router.post(
    "/",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую встречу",
)
async def create_meeting(
    data: MeetingCreate,
    service: MeetingService = Depends(meeting_service_getter),
):
    """
    Создать новую встречу для команды.
    
    При создании можно указать предыдущую встречу (previous_meeting_id).
    Если указана предыдущая встреча, автоматически обновляется ее связь next_meeting_id.
    """
    return await service.create(data)


@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse,
    summary="Получить встречу по ID",
)
async def get_meeting(
    meeting_id: UUID,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Получить детальную информацию о встрече."""
    meeting = await service.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Встреча с ID {meeting_id} не найдена"
        )
    return meeting


@router.patch(
    "/{meeting_id}",
    response_model=MeetingResponse,
    summary="Обновить данные встречи",
)
async def update_meeting(
    meeting_id: UUID,
    data: MeetingUpdate,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Частичное обновление встречи (название, описание, дата, статус)."""
    updated_meeting = await service.update(data, meeting_id)
    if not updated_meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Встреча с ID {meeting_id} не найдена для обновления"
        )
    return updated_meeting


@router.post(
    "/{meeting_id}/complete",
    response_model=MeetingResponse,
    summary="Завершить встречу",
)
async def complete_meeting(
    meeting_id: UUID,
    service: MeetingService = Depends(meeting_service_getter),
):
    """
    Завершить встречу.
    
    При завершении:
    1. Статус встречи меняется на COMPLETED
    2. Невыполненные задачи автоматически переносятся на следующую запланированную встречу
    3. Если следующей встречи нет, задачи остаются в текущей встрече
    """
    return await service.complete_meeting(meeting_id)


@router.post(
    "/{meeting_id}/cancel",
    response_model=MeetingResponse,
    summary="Отменить встречу",
)
async def cancel_meeting(
    meeting_id: UUID,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Отменить встречу (статус меняется на CANCELLED)."""
    return await service.cancel_meeting(meeting_id)


@router.delete(
    "/{meeting_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить встречу",
)
async def delete_meeting(
    meeting_id: UUID,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Удалить встречу."""
    deleted = await service.delete(meeting_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Встреча с ID {meeting_id} не найдена для удаления"
        )
    return Response(f"Successfully deleted meeting with id {meeting_id}", 200)


# Эндпоинты для работы с задачами встречи

@router.post(
    "/{meeting_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу для встречи",
)
async def create_task_for_meeting(
    meeting_id: UUID,
    data: TaskCreate,
    task_service: TaskService = Depends(task_service_getter),
):
    """Создать новую задачу и привязать ее к встрече."""
    return await task_service.create_for_meeting(meeting_id, data)


@router.get(
    "/{meeting_id}/tasks",
    response_model=List[TaskResponse],
    summary="Получить все задачи встречи",
)
async def get_meeting_tasks(
    meeting_id: UUID,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Получить список всех задач, привязанных к встрече."""
    return await service.get_meeting_tasks(meeting_id)


@router.post(
    "/{meeting_id}/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Добавить существующую задачу в встречу",
)
async def add_task_to_meeting(
    meeting_id: UUID,
    task_id: UUID,
    task_service: TaskService = Depends(task_service_getter),
):
    """Добавить существующую задачу в встречу."""
    added = await task_service.add_task_to_meeting(meeting_id, task_id)
    if not added:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось добавить задачу в встречу"
        )
    return Response(f"Successfully added task {task_id} to meeting {meeting_id}", 200)


@router.delete(
    "/{meeting_id}/tasks/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить задачу из встречи",
)
async def remove_task_from_meeting(
    meeting_id: UUID,
    task_id: UUID,
    task_service: TaskService = Depends(task_service_getter),
):
    """Удалить задачу из встречи (не удаляет саму задачу)."""
    removed = await task_service.remove_task_from_meeting(meeting_id, task_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь между встречей и задачей не найдена"
        )
    return Response(f"Successfully removed task {task_id} from meeting {meeting_id}", 200)


# Эндпоинты для фильтрации встреч

@router.get(
    "/",
    response_model=List[MeetingResponse],
    summary="Получить встречи с фильтрами",
)
async def get_meetings(
    team_id: Optional[UUID] = None,
    meeting_status: Optional[MeetingStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    service: MeetingService = Depends(meeting_service_getter),
):
    """Получить список встреч с фильтрами."""
    if not team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Параметр team_id обязателен"
        )
    
    return await service.get_team_meetings(team_id, meeting_status, from_date, to_date)