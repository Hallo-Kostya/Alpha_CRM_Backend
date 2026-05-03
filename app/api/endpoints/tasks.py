from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status, Query
from app.schemas.task import TaskCreate, TaskUpdate, Task
from app.services.task_service import (
    TaskService,
    task_service_getter,
)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)


@router.post("/", response_model=Task, summary="Создать задачу")
async def create_task(
    data: TaskCreate,
    service: TaskService = Depends(task_service_getter),
):
    """Создать новую задачу (без привязки к встрече)."""
    return await service.create(data)

@router.get("/", response_model=List[Task], summary="Получить задачи")
async def get_tasks(
    meeting_id: Optional[UUID] = Query(None, description="ID встречи для фильтрации задач"),
    service: TaskService = Depends(task_service_getter),
):
    """Получить список задач, опционально отфильтрованных по встрече."""
    return await service.get_list(meeting_id)


@router.get("/{task_id}", response_model=Task, summary="Получить задачу по ID")
async def get_task(
    task_id: UUID,
    service: TaskService = Depends(task_service_getter),
):
    """Получить детальную информацию о задаче."""
    task = await service.get_by_id(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена",
        )
    return task


@router.patch("/{task_id}", response_model=Task, summary="Обновить задачу")
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    service: TaskService = Depends(task_service_getter),
):
    """Обновить описание или статус задачи."""
    return await service.update(task_id, data)


@router.delete("/{task_id}", summary="Удалить задачу")
async def delete_task(
    task_id: UUID,
    service: TaskService = Depends(task_service_getter),
):
    """Удалить задачу."""
    deleted = await service.delete(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена для удаления",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/move-to-next-meeting", response_model=Task, summary="Перенести задачу на следующую встречу")
async def move_task_to_next_meeting(
    task_id: UUID,
    service: TaskService = Depends(task_service_getter),
):
    """Перенести невыполненную задачу на следующую встречу команды."""
    return await service.move_to_next_meeting(task_id)