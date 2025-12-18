from uuid import UUID
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.api.utils.auth import validate_curator
from app.application.dto.student import StudentCreate, StudentUpdate
from app.application.services.students_service import (
    StudentService,
    student_service_getter,
)
from app.domain.entities.persons.student import Student
from app.application.services.team_member_service import (
    TeamMemberService,
    team_member_service_getter,
)
from app.domain.entities.teams.team_member import TeamMember

router = APIRouter(
    prefix="/students",
    tags=["students"],
    responses={404: {"description": "Student not found"}},
)


@router.post(
    "/",
    response_model=Student,
    status_code=status.HTTP_201_CREATED,
    summary="Создать студента",
)
async def create_student(
    data: StudentCreate,
    service: StudentService = Depends(student_service_getter),
    curator_id: uuid.UUID = Depends(validate_curator)
):
    """Создать нового студента (без привязки к команде)."""
    return await service.create(data)


@router.get("/", response_model=List[Student], summary="Список всех студентов")
async def list_students(
    service: StudentService = Depends(student_service_getter),
):
    """Получить список всех студентов."""
    return await service.get_list()


@router.get(
    "/{student_id}",
    response_model=Student,
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


@router.patch(
    "/{student_id}",
    response_model=Student,
    summary="Обновить данные студента",
)
async def update_student(
    student_id: UUID,
    data: StudentUpdate,
    service: StudentService = Depends(student_service_getter),
    curator_id: uuid.UUID = Depends(validate_curator)
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
    status_code=status.HTTP_200_OK,
    summary="Удалить студента",
)
async def delete_student(
    student_id: UUID,
    service: StudentService = Depends(student_service_getter),
    curator_id: uuid.UUID = Depends(validate_curator)
):
    """Удалить студента (каскадно удалятся связи с командами и посещаемость)."""
    deleted = await service.delete(student_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Студент с ID {student_id} не найден для удаления",
        )
    return Response(f"Successfully deleted student with id {student_id}", 200)


@router.get(
    "/{student_id}/teams",
    response_model=List[TeamMember],
    summary="Получить все команды студента",
)
async def get_student_teams(
    student_id: UUID,
    service: TeamMemberService = Depends(team_member_service_getter),
):
    """Получить список всех команд, в которых состоит студент."""
    return await service.get_student_teams(student_id)