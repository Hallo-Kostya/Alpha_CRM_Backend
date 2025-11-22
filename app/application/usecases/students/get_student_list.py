from app.application.usecases.use_case_interface import IUseCase
from app.domain.entities.persons.student import Student
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface

class CreateStudent(IUseCase):
    def __init__(self, student_repo : CRUDRepositoryInterface[Student]):
        self.student_repo = student_repo

    async def execute(self) -> list[Student]:
        return await self.student_repo.list()