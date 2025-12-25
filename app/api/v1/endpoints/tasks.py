from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.application.dto.task import TaskCreate, TaskUpdate, TaskResponse
from app.application.services.task_service import TaskService, task_service_getter

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Получить задачу по ID",
)
async def get_task(
    task_id: UUID,
    service: TaskService = Depends(task_service_getter),
):
    """Получить информацию о задаче."""
    task = await service.get_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена"
        )
    return task


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Обновить данные задачи",
)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    service: TaskService = Depends(task_service_getter),
):
    """Частичное обновление задачи (описание, статус выполнения)."""
    updated_task = await service.update(data, task_id)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена для обновления"
        )
    return updated_task


@router.post(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Отметить задачу как выполненную",
)
async def complete_task(
    task_id: UUID,
    service: TaskService = Depends(task_service_getter),
):
    """Отметить задачу как выполненную."""
    return await service.complete_task(task_id)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить задачу",
)
async def delete_task(
    task_id: UUID,
    service: TaskService = Depends(task_service_getter),
):
    """Удалить задачу."""
    deleted = await service.delete(task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена для удаления"
        )
    return Response(f"Successfully deleted task with id {task_id}", 200)