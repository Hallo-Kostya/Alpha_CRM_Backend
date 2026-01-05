from fastapi import Depends, HTTPException
import jwt
import uuid
from passlib.context import CryptContext
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from app.application.services.base_service import BaseService
from app.domain.entities.auth_tokens.auth_token import AuthToken
from app.infrastructure.database.models import RefreshTokenModel
from app.infrastructure.database.repositories.token_repository import (
    TokenRepository,
    token_repository_getter,
)
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService(BaseService[RefreshTokenModel, AuthToken]):
    orm_model = RefreshTokenModel
    pyd_scheme = AuthToken

    def __init__(self, token_repo: TokenRepository):
        self._repo = token_repo

    async def create_token_pair(
        self, user_id: uuid.UUID,
    ) -> tuple[AuthToken, AuthToken]:
        access = self._create_access_token(user_id)
        refresh = self._create_refresh_token(user_id)
        orm_refresh = self._to_orm(refresh)
        await self._repo.create(orm_refresh)
        return access, refresh

    async def revoke_token_pair(
        self,
        refresh_token: str
    ) -> None:
        hashed_token = self.get_hash_for_string(refresh_token)
        existing_token = await self._repo.get_by_token_hash(hashed_token)
        if not existing_token:
            raise ValueError
        await self._repo.update(existing_token, {"is_revoked": True})

    async def refresh_token_pair(self, refresh_token: str, curator_id: uuid.UUID) -> tuple[AuthToken, AuthToken]:
        await self.revoke_token_pair(refresh_token)
        token_pair = await self.create_token_pair(curator_id)
        return token_pair

    def _to_orm(self, pyd_scheme: AuthToken) -> RefreshTokenModel:
        return RefreshTokenModel(
            token_hash=self.get_hash_for_string(pyd_scheme.token),
            curator_id=pyd_scheme.curator_id,
            expires_at=pyd_scheme.expires_at,
            is_revoked=pyd_scheme.is_revoked,
        )

    @staticmethod
    def get_hash_for_string(string_: str) -> str:
        return hashlib.sha256(string_.encode("utf-8")).hexdigest()

    @staticmethod
    def get_hashed_pass(string_: str) -> str:
        return pwd_context.hash(string_)

    @staticmethod
    def _create_access_token(curator_id: uuid.UUID) -> AuthToken:
        payload = {"id": str(curator_id)}
        to_encode = payload.copy()
        expires_at = datetime.now(tz=timezone.utc) + timedelta(
            minutes=settings.hash.access_expire_minutes
        )
        to_encode.update({"exp": int(expires_at.timestamp()), "jti": str(uuid.uuid4())})
        encoded_jwt = jwt.encode(
            to_encode, settings.hash.access_secret, algorithm=settings.hash.algorithm
        )
        return AuthToken(
            token=encoded_jwt,
            expires_at=expires_at,
            is_revoked=False,
            curator_id=curator_id,
        )

    @staticmethod
    def _create_refresh_token(curator_id: uuid.UUID) -> AuthToken:
        payload = {"id": str(curator_id)}
        to_encode = payload.copy()
        expires_at = datetime.now(tz=timezone.utc) + timedelta(
            days=settings.hash.refresh_expire_days
        )
        to_encode.update({"exp": int(expires_at.timestamp()), "jti": str(uuid.uuid4())})
        encoded_jwt = jwt.encode(
            to_encode, settings.hash.refresh_secret, algorithm=settings.hash.algorithm
        )
        return AuthToken(
            token=encoded_jwt,
            expires_at=expires_at,
            is_revoked=False,
            curator_id=curator_id,
        )

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_curator_id_from_access(token: str) -> uuid.UUID:
        """Метод для обработки входящего токена авторизации в заголовках"""
        try:
            payload = jwt.decode(
                token,
                settings.hash.access_secret,
                algorithms=[settings.hash.algorithm],
                options={"require": ["exp"], "verify_exp": True},
            )
            curator_id = payload.get("id")
            if not curator_id:
                raise HTTPException(
                    status_code=401, detail="Could not validate credentials"
                )
            return curator_id
        except Exception as e:
            print(e)
            raise HTTPException(status_code=401, detail="Invalid authorization token")

    @staticmethod
    def get_curator_id_from_refresh(token: str) -> uuid.UUID:
        """Метод для обработки входящего токена авторизации в заголовках"""
        try:
            payload = jwt.decode(
                token,
                settings.hash.refresh_secret,
                algorithms=[settings.hash.algorithm],
                options={"require": ["exp"], "verify_exp": True},
            )
            curator_id = payload.get("id")
            if not curator_id:
                raise HTTPException(
                    status_code=401, detail="Could not validate credentials"
                )
            return curator_id
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid authorization token")


def auth_service_getter(
    repository: TokenRepository = Depends(token_repository_getter),
):
    return AuthService(repository)
