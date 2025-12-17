from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.application.dto.student import StudentCreate, StudentUpdate, StudentRead
from app.application.services.students_service import (
    StudentService,
    student_service_getter,
)

router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Student not found"}},
)


@router.post(
    "/",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать студента",
)
async def create_student(
    data: StudentCreate,
    service: StudentService = Depends(student_service_getter),
):
    """Создать нового студента (без привязки к команде)."""
    return await service.create(data)


@router.get("/", response_model=List[StudentRead], summary="Список всех студентов")
async def list_students(
    service: StudentService = Depends(student_service_getter),
):
    """Получить список всех студентов."""
    return await service.get_list()


@router.get(
    "/{student_id}",
    response_model=StudentRead,
    summary="Получить студента по ID",
)
async def get_student(
    student_id: UUID,
    service: StudentService = Depends(student_service_getter),
):
    """Получить информацию о студенте."""
    student = await service.get_by_id(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден",
        )
    return student


@router.put(
    "/{student_id}",
    response_model=StudentRead,
    summary="Обновить данные студента",
)
async def update_student(
    student_id: UUID,
    data: StudentUpdate,
    service: StudentService = Depends(student_service_getter),
):
    """Частичное обновление данных студента."""
    updated_student = await service.update(data, student_id)
    if not updated_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден для обновления",
        )
    return updated_student


@router.delete(
    "/{student_id}",
    summary="Удалить студента",
)
async def delete_student(
    student_id: UUID,
    service: StudentService = Depends(student_service_getter),
):
    """Удалить студента (каскадно удалятся связи с командами и посещаемость)."""
    deleted = await service.delete(student_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден для удаления",
        )
    return Response(f"successfully deleted student with id {student_id}", 200)
