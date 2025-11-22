from app.application.usecases.use_case_interface import IUseCase
from app.domain.entities.projects.project import Project
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface

class UpdateProject(IUseCase[Project, None]):
    def __init__(self, project_repo : CRUDRepositoryInterface[Project]):
        self.project_repo = project_repo

    async def execute(self, project: Project) -> None:
        await self.project_repo.update(project)