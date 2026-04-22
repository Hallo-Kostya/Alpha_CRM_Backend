from uuid import UUID
import logging
from fastapi import Depends
from app.schemas.student import StudentCreate, StudentUpdate, StudentDetailed, StudentDetailedResponse, StudentSummary, StudentSummaryResponse
from app.schemas.student import Student
from app.infrastructure.database.models import StudentModel
from app.infrastructure.database.repositories.student_repository import (
    StudentRepository,
    student_repository_getter,
)

logger = logging.getLogger("student_service")


class StudentService:
    """Application service for students."""

    def __init__(self, student_repo: StudentRepository):
        self.student_repo = student_repo

    def _to_orm(self, scheme: StudentCreate) -> StudentModel:
        """Convert schema to ORM model."""
        return StudentModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: StudentModel) -> Student:
        """Convert ORM model to schema."""
        return Student.model_validate(orm_model, from_attributes=True)

    async def create(self, student: StudentCreate) -> Student:
        """Create new student."""
        orm_obj = self._to_orm(student)
        created_obj = await self.student_repo.create(orm_obj)
        student_schema = self._to_schema(created_obj)
        return student_schema

    async def update(
        self, student_id: UUID, new_data: StudentUpdate
    ) -> Student | None:
        """Update student."""

        old_obj = await self.student_repo.get_by_id(student_id)
        if not old_obj:
            return None

        updated_orm = await self.student_repo.update(
            old_obj, new_data.model_dump(exclude_unset=True)
        )
        student_schema = self._to_schema(updated_orm)
        return student_schema

    async def delete(self, student_id: UUID) -> bool:
        """Delete student."""
        obj = await self.student_repo.get_by_id(student_id)
        if not obj:
            return False
        await self.student_repo.delete(obj)
        return True

    async def get_by_id(self, student_id: UUID) -> Student | None:
        """Get student by ID."""
        obj = await self.student_repo.get_by_id(student_id)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_students_summary(self) -> StudentDetailedResponse:
        """Get detailed students summary: id, full_name, email, tg_link."""
        total, raw_items = await self.student_repo.get_students_detailed()
        students = [StudentDetailed(**item) for item in raw_items]
        return StudentDetailedResponse(total=total, students=students)


def student_service_getter(
    repository: StudentRepository = Depends(student_repository_getter),
):
    return StudentService(repository)
