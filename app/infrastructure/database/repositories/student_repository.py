from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import StudentModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class StudentRepository(BaseRepository[StudentModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(StudentModel, session)


def student_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = StudentRepository(session)
    return repository
