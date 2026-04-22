from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import StudentModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Tuple, List


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

    async def get_students_detailed(self) -> Tuple[int, List[dict]]:
        """Получить детальную сводку студентов: id, full_name, email, tg_link"""
        query = select(
            StudentModel.id,
            StudentModel.first_name,
            StudentModel.last_name,
            StudentModel.patronymic,
            StudentModel.email,
            StudentModel.tg_link
        ).select_from(StudentModel)

        result = await self.session.execute(query)
        rows = result.all()

        items = [
            {
                "id": row.id,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "patronymic": row.patronymic,
                "email": row.email,
                "tg_link": row.tg_link
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
