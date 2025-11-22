from uuid import UUID
from app.application.usecases.use_case_interface import IUseCase
from app.domain.entities.projects.project import Project
from app.domain.interfaces.repositories.crud_repository_interface import CRUDRepositoryInterface

class GetProject(IUseCase[UUID, Project]):
    def __init__(self, project_repo : CRUDRepositoryInterface[Project]):
        self.project_repo = project_repo

    async def execute(self, id: UUID) -> Project:
        project = await self.project_repo.get(id)
        if project is None:
            raise ValueError(f"Project with id {id} not found")
        return project
    