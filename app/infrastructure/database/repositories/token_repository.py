from app.infrastructure.database.repositories.base_repository import BaseRepository
from app.infrastructure.database.models import RefreshTokenModel
from app.infrastructure.database.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class TokenRepository(BaseRepository[RefreshTokenModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshTokenModel, session)

    async def get_by_token_hash(self, token_hash: str) -> RefreshTokenModel | None:
        query = select(self.model).where(
            self.model.token_hash == token_hash,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


def token_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> TokenRepository:
    return TokenRepository(session)