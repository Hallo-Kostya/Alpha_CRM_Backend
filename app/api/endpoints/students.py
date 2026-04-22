from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.schemas.student import StudentCreate, StudentUpdate, StudentSummary, StudentDetailed, StudentSummaryResponse, StudentDetailedResponse
from app.services.students_service import (
    StudentService,
    student_service_getter,
)
from app.schemas.student import Student


router = APIRouter(
    prefix="/students",
    tags=["v2", "students"],
    responses={404: {"description": "Student not found"}},
)


@router.post("/", response_model=Student, summary="Создать студента")
async def create_student(
    data: StudentCreate,
    service: StudentService = Depends(student_service_getter),
):
    """Создать нового студента с ФИО, email и Telegram."""
    return await service.create(data)

@router.get("/", response_model=StudentDetailedResponse, summary="Список студентов")
async def list_students_summary(
    service: StudentService = Depends(student_service_getter),
):
    """Получить список студентов с ID, ФИО, email и Telegram."""
    return await service.get_students_summary()

@router.get("/{student_id}", response_model=Student, summary="Получить студента по ID")
async def get_student(
    student_id: UUID,
    service: StudentService = Depends(student_service_getter),
):
    """Получить детальную информацию о студенте."""
    student = await service.get_by_id(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден",
        )
    return student


@router.patch("/{student_id}", response_model=Student, summary="Обновить студента")
async def update_student(
    student_id: UUID,
    data: StudentUpdate,
    service: StudentService = Depends(student_service_getter),
):
    """Обновить данные студента: ФИО, email, Telegram."""
    return await service.update(student_id, data)


@router.delete("/{student_id}", summary="Удалить студента")
async def delete_student(
    student_id: UUID,
    service: StudentService = Depends(student_service_getter),
):
    """Удалить студента."""
    deleted = await service.delete(student_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден для удаления",
        )
    return Response(f"successfully deleted student with id {student_id}", status.HTTP_200_OK)