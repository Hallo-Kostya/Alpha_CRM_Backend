from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from uuid import UUID

from app.core.config import settings
from app.infrastructure.database.models import CuratorModel
from app.infrastructure.database.repositories.curator_repository import (
    CuratorRepository,
    curator_repository_getter,
)

security = HTTPBearer(auto_error=False)

async def get_current_curator(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    curator_repo: CuratorRepository = Depends(curator_repository_getter),
) -> CuratorModel:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.hash.access_secret,
            algorithms=[settings.hash.algorithm],
            options={"require": ["exp"], "verify_exp": True},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    curator_id = payload.get("id")
    if not curator_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    curator = await curator_repo.get_by_id(UUID(curator_id))
    if not curator:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Curator not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return curator