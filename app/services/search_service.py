# app/services/search_service.py
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select, or_, func, literal, text, literal
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.infrastructure.database.models.persons.student import StudentModel
from app.infrastructure.database.models.projects.project import ProjectModel
from app.infrastructure.database.models.teams.team import TeamModel
from app.infrastructure.database.repositories.curator_team_repository import CuratorTeamRepository
from app.infrastructure.database.repositories.project_repository import ProjectRepository, project_repository_getter
from app.infrastructure.database.repositories.team_repository import TeamRepository, team_repository_getter
from app.infrastructure.database.repositories.student_repository import StudentRepository, student_repository_getter
from app.infrastructure.database.database import db_helper
from app.schemas.team import CuratorShort

class SearchService:
    def __init__(
        self,
        project_repo: ProjectRepository,
        team_repo: TeamRepository,
        student_repo: StudentRepository,
        curator_team_repo: CuratorTeamRepository
    ):
        self.project_repo = project_repo
        self.team_repo = team_repo
        self.student_repo = student_repo
        self._curator_team_repo = curator_team_repo

    async def search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Умный поиск по проектам, командам и студентам."""
        results = []
        
        # Поиск по проектам
        project_query = select(
            literal("project").label("type"),
            ProjectModel.id,
            ProjectModel.name,
            ProjectModel.description.label("description")
        ).select_from(ProjectModel).where(ProjectModel.name.ilike(f"%{query}%")).limit(limit)
        project_results = await self.project_repo.session.execute(project_query)
        results.extend([row._asdict() for row in project_results])
        
        # Поиск по командам
        team_query = select(
            literal("team").label("type"),
            TeamModel.id,
            TeamModel.name,
            literal("").label("description")  # Команды могут не иметь описания
        ).select_from(TeamModel).where(TeamModel.name.ilike(f"%{query}%")).limit(limit)
        team_results = await self.team_repo.session.execute(team_query)
        results.extend([row._asdict() for row in team_results])
        
        # Поиск по студентам (по first_name + last_name)
        student_query = select(
            literal("student").label("type"),
            StudentModel.id,
            func.concat(StudentModel.first_name, " ", StudentModel.last_name).label("name"),
            literal("").label("description")
        ).where(
            or_(
                StudentModel.first_name.ilike(f"%{query}%"),
                StudentModel.last_name.ilike(f"%{query}%"),
                func.concat(StudentModel.first_name, " ", StudentModel.last_name).ilike(f"%{query}%")
            )
        ).limit(limit)
        student_results = await self.student_repo.session.execute(student_query)
        results.extend([row._asdict() for row in student_results])
        
        # Сортировка: точные совпадения выше (опционально)
        results.sort(key=lambda x: 0 if query.lower() in x["name"].lower() else 1)
        
        return results[:limit * 3]  # Общий лимит
    
    async def search_students(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        student_query = select(
            StudentModel.id,
            StudentModel.first_name,
            StudentModel.last_name,
            StudentModel.email,
        ).where(
            or_(
                StudentModel.first_name.ilike(f"%{query}%"),
                StudentModel.last_name.ilike(f"%{query}%"),
                StudentModel.email.ilike(f"%{query}%"),
                func.concat(
                    StudentModel.first_name, " ", StudentModel.last_name
                ).ilike(f"%{query}%"),
            )
        ).order_by(StudentModel.last_name, StudentModel.first_name).limit(limit)

        results = await self.student_repo.session.execute(student_query)
        return [row._asdict() for row in results]

    async def search_curators(self, query: str, limit: int = 20) -> list[CuratorShort]:
        curators = await self._curator_team_repo.search_curators(query, limit)
        return [CuratorShort.model_validate(c, from_attributes=True) for c in curators]

def search_service_getter(
    project_repo: ProjectRepository = Depends(project_repository_getter),
    team_repo: TeamRepository = Depends(team_repository_getter),
    student_repo: StudentRepository = Depends(student_repository_getter),
) -> SearchService:
    return SearchService(project_repo, team_repo, student_repo)
