from typing import Optional, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.base import Base
from app.infrastructure.database.database import db_helper
from app.infrastructure.database.models.teams.curator_team import CuratorTeamModel
from app.infrastructure.database.models.persons.curator import CuratorModel


class CuratorTeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, curator_id: UUID, team_id: UUID) -> CuratorTeamModel:
        """Привязать куратора к команде."""
        link = CuratorTeamModel(curator_id=curator_id, team_id=team_id)
        self.session.add(link)
        await self.session.commit()
        await self.session.refresh(link)
        return link

    async def remove(self, curator_id: UUID, team_id: UUID) -> bool:
        """Отвязать куратора от команды. Возвращает True если связь была найдена и удалена."""
        stmt = delete(CuratorTeamModel).where(
            CuratorTeamModel.curator_id == curator_id,
            CuratorTeamModel.team_id == team_id,
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def exists(self, curator_id: UUID, team_id: UUID) -> bool:
        """Проверить, привязан ли куратор к команде."""
        stmt = select(CuratorTeamModel).where(
            CuratorTeamModel.curator_id == curator_id,
            CuratorTeamModel.team_id == team_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_curators_for_team(self, team_id: UUID) -> Sequence[CuratorModel]:
        """Получить всех кураторов команды."""
        stmt = (
            select(CuratorModel)
            .join(CuratorTeamModel, CuratorTeamModel.curator_id == CuratorModel.id)
            .where(CuratorTeamModel.team_id == team_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_curators(self, query: str, limit: int = 20) -> Sequence[CuratorModel]:
        """Поиск по зарегистрированным кураторам (имя, фамилия)."""
        q = f"%{query}%"
        from sqlalchemy import or_, func
        stmt = (
            select(CuratorModel)
            .where(
                or_(
                    CuratorModel.first_name.ilike(q),
                    CuratorModel.last_name.ilike(q),
                    func.concat(
                        CuratorModel.first_name, " ", CuratorModel.last_name
                    ).ilike(q),
                )
            )
            .order_by(CuratorModel.last_name, CuratorModel.first_name)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


def curator_team_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> CuratorTeamRepository:
    return CuratorTeamRepository(session)