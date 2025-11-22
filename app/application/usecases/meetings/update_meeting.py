
from app.application.usecases.use_case_interface import IUseCase
from app.domain.entities.meetings.meetings import Meeting
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface

class CreateProject(IUseCase):
    def __init__(self, meeting_repo : CRUDRepositoryInterface[Meeting]):
        self.meeting_repo = meeting_repo

    async def execute(self, meeting: Meeting) -> None:
        await self.meeting_repo.update(meeting)
