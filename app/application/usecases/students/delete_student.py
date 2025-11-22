from uuid import UUID
from app.application.usecases.use_case_interface import IUseCase
from app.domain.entities.persons.student import Student
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface

class DeleteStudent(IUseCase):
    def __init__(self, student_repo : CRUDRepositoryInterface[Student]):
        self.student_repo = student_repo

    async def execute(self, id: UUID) -> None:
        await self.student_repo.delete(id)