from app.application.usecases.use_case_interface import IUseCase
from app.domain.entities.teams.team import Team
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface

class CreateStudent(IUseCase):
    def __init__(self, team_repo : CRUDRepositoryInterface[Team]):
        self.team_repo = team_repo

    async def execute(self, team: Team) -> None:
        await self.team_repo.create(team)