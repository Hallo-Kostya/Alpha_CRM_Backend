from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from app.schemas.meeting import MeetingCreate, MeetingUpdate, Meeting
from app.services.meeting_service import (
    MeetingService,
    meeting_service_getter,
)

router = APIRouter(
    prefix="/meetings",
    tags=["v2", "meetings"],
    responses={404: {"description": "Meeting not found"}},
)


@router.post("/", response_model=Meeting, summary="Создать встречу")
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
    return await service.get_meetings_for_calendar(team_id, start_date, end_date)


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
    return Response(f"successfully deleted meeting with id {meeting_id}", status.HTTP_200_OK)
