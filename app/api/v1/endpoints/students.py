from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.student import StudentCreate, StudentUpdate, StudentRead
from app.application.services.students_service import StudentService
from app.core.database import db_helper
from app.domain.entities.persons.student import Student
from app.infrastructure.database.models.persons.student import StudentModel
from app.infrastructure.database.repositories.crud_repository import CRUDRepository


router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Student not found"}},
)


async def get_student_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> StudentService:
    """Фабрика для StudentService с CRUD-репозиторием."""
    repo = CRUDRepository[Student, StudentModel](
        model=StudentModel,
        domain_model=Student,
        session=session,
    )
    return StudentService(student_repo=repo)


@router.post(
    "/",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать студента",
)
async def create_student(
    data: StudentCreate,
    service: StudentService = Depends(get_student_service),
) -> Student:
    """Создать нового студента (без привязки к команде)."""
    student = Student(**data.model_dump(exclude_unset=True))
    return await service.create_student(student)


@router.get("/", response_model=List[StudentRead], summary="Список всех студентов")
async def list_students(
    service: StudentService = Depends(get_student_service),
) -> List[Student]:
    """Получить список всех студентов."""
    return await service.list_students()


@router.get(
    "/{student_id}",
    response_model=StudentRead,
    summary="Получить студента по ID",
)
async def get_student(
    student_id: UUID,
    service: StudentService = Depends(get_student_service),
) -> Student:
    """Получить информацию о студенте."""
    student = await service.get_student(student_id)
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
    service: StudentService = Depends(get_student_service),
) -> Student:
    """Частичное обновление данных студента."""
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не переданы данные для обновления",
        )

    existing = await service.get_student(student_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден",
        )

    updated_student = existing.model_copy(update=update_data)
    return await service.update_student(updated_student)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить студента",
)
async def delete_student(
    student_id: UUID,
    service: StudentService = Depends(get_student_service),
) -> None:
    """Удалить студента (каскадно удалятся связи с командами и посещаемость)."""
    student = await service.get_student(student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден",
        )
    await service.delete_student(student_id)