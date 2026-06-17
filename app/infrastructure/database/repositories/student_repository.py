from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import StudentModel, TeamMemberModel, TeamModel, ProjectTeamModel
from app.infrastructure.database.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, literal
from typing import Tuple, List, Optional
from uuid import UUID


class StudentRepository(BaseRepository[StudentModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(StudentModel, session)

    async def get_students_summary(self) -> Tuple[int, List[dict]]:
        """Получить сводку студентов: id, full_name"""
        query = select(
            StudentModel.id,
            StudentModel.first_name,
            StudentModel.last_name,
            StudentModel.patronymic
        ).select_from(StudentModel)

        result = await self.session.execute(query)
        rows = result.all()

        items = [
            {
                "id": row.id,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "patronymic": row.patronymic
            }
            for row in rows
        ]

        total = len(items)
        return total, items

    async def get_students_detailed(self, team_id: Optional[UUID] = None, project_id: Optional[UUID] = None) -> Tuple[int, List[dict]]:
        """Получить детальную сводку студентов: id, full_name, email, tg_link с фильтрами по команде и проекту"""
        
        if team_id:
            # Если фильтр по команде, JOIN для получения role и study_group
            query = select(
                StudentModel.id,
                StudentModel.first_name,
                StudentModel.last_name,
                StudentModel.patronymic,
                StudentModel.email,
                StudentModel.tg_link,
                TeamMemberModel.role,
                TeamMemberModel.study_group
            ).select_from(
                StudentModel
            ).join(
                TeamMemberModel, StudentModel.id == TeamMemberModel.student_id
            ).where(TeamMemberModel.team_id == team_id)
        else:
            # Без фильтра по команде
            query = select(
                StudentModel.id,
                StudentModel.first_name,
                StudentModel.last_name,
                StudentModel.patronymic,
                StudentModel.email,
                StudentModel.tg_link,
                literal(None).label("role"),
                literal(None).label("study_group")
            ).select_from(StudentModel)

        # Фильтр по проекту
        if project_id:
            query = query.where(
                select(1)
                .select_from(TeamMemberModel)
                .join(TeamModel, TeamMemberModel.team_id == TeamModel.id)
                .join(ProjectTeamModel, TeamModel.id == ProjectTeamModel.team_id)
                .where(
                    TeamMemberModel.student_id == StudentModel.id,
                    ProjectTeamModel.project_id == project_id
                )
                .exists()
            )

        result = await self.session.execute(query)
        rows = result.all()

        items = [
            {
                "id": row.id,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "patronymic": row.patronymic,
                "email": row.email,
                "tg_link": row.tg_link,
                "role": row.role,
                "study_group": row.study_group
            }
            for row in rows
        ]

        total = len(items)
        return total, items


def student_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = StudentRepository(session)
    return repository
