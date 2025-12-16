from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto.student import StudentCreate, StudentUpdate
from app.application.services.students_service import StudentService
from app.core.database import db_helper
from app.domain.entities.persons.student import Student
from app.infrastructure.database.models.persons.student import StudentModel
from app.infrastructure.database.repositories.crud_repository import CRUDRepository


router = APIRouter(prefix="/students", tags=["students"])


async def get_student_service(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> StudentService:
    repo = CRUDRepository[Student, StudentModel](
        model=StudentModel,
        domain_model=Student,
        session=session,
    )
    return StudentService(repo)


@router.post("/", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(
    data: StudentCreate,
    service: StudentService = Depends(get_student_service),
) -> Student:
    student = Student(**data.model_dump(exclude_unset=True))
    return await service.create_student(student)


@router.get("/", response_model=List[Student])
async def list_students(
    service: StudentService = Depends(get_student_service),
) -> List[Student]:
    return await service.list_students()


@router.get("/{student_id}", response_model=Student)
async def get_student(
    student_id: UUID,
    service: StudentService = Depends(get_student_service),
) -> Student:
    student = await service.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.put("/{student_id}", response_model=Student)
async def update_student(
    student_id: UUID,
    data: StudentUpdate,
    service: StudentService = Depends(get_student_service),
) -> Student:
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided for update")

    existing = await service.get_student(student_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Student not found")

    updated_student = existing.model_copy(update=update_data)
    return await service.update_student(updated_student)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: UUID,
    service: StudentService = Depends(get_student_service),
) -> None:
    await service.delete_student(student_id)