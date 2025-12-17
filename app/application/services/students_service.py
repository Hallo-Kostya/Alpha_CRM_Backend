from uuid import UUID
from fastapi import Depends
from app.application.services.base_service import BaseService
from app.application.dto.student import StudentCreate, StudentRead, StudentUpdate
from app.infrastructure.database.models import StudentModel
from app.infrastructure.database.repositories.student_repository import (
    StudentRepository,
    student_repository_getter,
)


class StudentService(BaseService[StudentModel, StudentRead]):
    orm_model = StudentModel
    pyd_scheme = StudentRead

    def __init__(
        self,
        student_repo: StudentRepository,
    ):
        super().__init__(student_repo)

    async def create(self, student: StudentCreate) -> StudentRead:
        orm_obj = self._to_orm(student)
        created_obj = await self._repo.create(orm_obj)
        return self._to_schema(created_obj)

    async def update(
        self, new_data: StudentUpdate, student_id: UUID
    ) -> StudentRead | None:
        old_obj = await self._repo.get_by_id(student_id)
        if not old_obj:
            return None
        updated_orm = await self._repo.update(
            old_obj, new_data.model_dump(exclude_unset=True)
        )
        return self._to_schema(updated_orm)


def student_service_getter(
    repository: StudentRepository = Depends(student_repository_getter),
):
    return StudentService(repository)
