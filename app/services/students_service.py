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
        self._repo = student_repo

    def _to_orm(self, scheme: StudentCreate) -> StudentModel:
        """Convert schema to ORM model."""
        return StudentModel(**scheme.model_dump(exclude_unset=True))

    def _to_schema(self, orm_model: StudentModel) -> Student:
        """Convert ORM model to schema."""
        return Student.model_validate(orm_model, from_attributes=True)

    async def create(self, student: StudentCreate, request_id: str | None = None) -> Student:
        """Create new student."""
        log_prefix = f"[{request_id}]" if request_id else ""
        logger.info(f'{log_prefix} Creating student: {student.last_name}')
        try:
            orm_obj = self._to_orm(student)
            created_obj = await self._repo.create(orm_obj)
            student_schema = self._to_schema(created_obj)
            logger.info(f'{log_prefix} Successfully created student with id: {student_schema.id}')
            return student_schema
        except Exception as e:
            logger.exception(f'{log_prefix} Failed to create student: {e}')
            raise

    async def update(
        self, student_id: UUID, new_data: StudentUpdate, request_id: str | None = None
    ) -> Student | None:
        """Update student."""
        log_prefix = f"[{request_id}]" if request_id else ""
        logger.info(f'{log_prefix} Updating student with id: {student_id}')
        old_obj = await self._repo.get_by_id(student_id)
        if not old_obj:
            logger.warning(f'{log_prefix} Student with id {student_id} not found for update')
            return None

        try:
            updated_orm = await self._repo.update(
                old_obj, new_data.model_dump(exclude_unset=True)
            )
            student_schema = self._to_schema(updated_orm)
            logger.info(f'{log_prefix} Successfully updated student with id: {student_schema.id}')
            return student_schema
        except Exception as e:
            logger.exception(f'{log_prefix} Failed to update student {student_id}: {e}')
            raise

    async def delete(self, student_id: UUID) -> bool:
        """Delete student."""
        obj = await self._repo.get_by_id(student_id)
        if not obj:
            return False
        await self._repo.delete(obj)
        return True

    async def get_by_id(self, student_id: UUID) -> Student | None:
        """Get student by ID."""
        obj = await self._repo.get_by_id(student_id)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_list(self, **filter_attrs) -> list[Student]:
        """Get list of students."""
        items = await self._repo.get_list(**filter_attrs)
        return [self._to_schema(item) for item in items]

    async def get_students_summary(self) -> StudentSummaryResponse:
        """Get students summary: id, full_name."""
        total, raw_items = await self._repo.get_students_summary()
        students = [StudentSummary(**item) for item in raw_items]
        return StudentSummaryResponse(total=total, students=students)

    async def get_students_detailed(self) -> StudentDetailedResponse:
        """Get detailed students summary: id, full_name, email, tg_link."""
        total, raw_items = await self._repo.get_students_detailed()
        students = [StudentDetailed(**item) for item in raw_items]
        return StudentDetailedResponse(total=total, students=students)


def student_service_getter(
    repository: StudentRepository = Depends(student_repository_getter),
):
    return StudentService(repository)
