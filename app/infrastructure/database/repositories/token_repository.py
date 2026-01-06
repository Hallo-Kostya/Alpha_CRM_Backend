from app.infrastructure.database.repositories.base_repository import (
    BaseRepository,
)
from app.infrastructure.database.models import RefreshTokenModel
from app.core.database import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class TokenRepository(BaseRepository[RefreshTokenModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshTokenModel, session)

    async def get_by_token_hash(self, token_hash: str) -> RefreshTokenModel | None:
        existing_token = await self.get_list(token_hash=token_hash, is_revoked=False)
        if existing_token:
            return existing_token[0]
        return None


def token_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> BaseRepository:
    repository = TokenRepository(session)
    return repository
