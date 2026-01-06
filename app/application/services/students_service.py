from uuid import UUID
import logging
from fastapi import Depends
from app.application.services.base_service import BaseService
from app.application.dto.student import StudentCreate, StudentUpdate
from app.domain.entities.persons.student import Student
from app.infrastructure.database.models import StudentModel
from app.infrastructure.database.repositories.student_repository import (
    StudentRepository,
    student_repository_getter,
)

logger = logging.getLogger("student_service")

class StudentService(BaseService[StudentModel, Student]):
    orm_model = StudentModel
    pyd_scheme = Student

    def __init__(self, student_repo: StudentRepository):
        super().__init__(student_repo)

    async def create(self, student: StudentCreate, request_id: str | None = None) -> Student:
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
        self, new_data: StudentUpdate, student_id: UUID, request_id: str | None = None
    ) -> Student | None:
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


def student_service_getter(
    repository: StudentRepository = Depends(student_repository_getter),
):
    return StudentService(repository)
