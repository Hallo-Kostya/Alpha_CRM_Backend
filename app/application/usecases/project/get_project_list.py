from app.application.usecases.use_case_interface import IUseCase
from app.domain.entities.projects.project import Project
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface

class GetProjectList(IUseCase[None, list[Project]]):
    def __init__(self, project_repo : CRUDRepositoryInterface[Project]):
        self.project_repo = project_repo

    async def execute(self) -> list[Project]:
        return await self.project_repo.list()