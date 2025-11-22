from uuid import UUID
from app.application.usecases.use_case_interface import IUseCase
from app.domain.entities.teams.team import Team
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface

class CreateStudent(IUseCase):
    def __init__(self, team_repo : CRUDRepositoryInterface[Team]):
        self.team_repo = team_repo

    async def execute(self, id: UUID) -> Team:
        team = await self.team_repo.get(id)
        if team is None:
            raise ValueError(f"Team with id {id} not found")
        return team