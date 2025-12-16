from uuid import UUID
from typing import List

from app.domain.entities.persons.student import Student
from app.infrastructure.database.repositories.crud_repository import CRUDRepository
from app.infrastructure.database.models.persons.student import StudentModel  # предполагаем


class StudentService:
    def __init__(
        self,
        student_repo: CRUDRepository[Student, StudentModel],
    ) -> None:
        self._repo = student_repo

    async def create_student(self, student: Student) -> Student:
        return await self._repo.create(student)

    async def get_student(self, student_id: UUID) -> Student | None:
        return await self._repo.get(student_id)

    async def update_student(self, student: Student) -> Student:
        return await self._repo.update(student)

    async def delete_student(self, student_id: UUID) -> None:
        await self._repo.delete(student_id)

    async def list_students(self) -> List[Student]:
        return await self._repo.list()