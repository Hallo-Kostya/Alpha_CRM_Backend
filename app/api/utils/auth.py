import uuid
from fastapi import Depends, HTTPException
from app.application.services.auth_service import AuthService
from app.infrastructure.database.repositories.curator_repository import (
    CuratorRepository,
    curator_repository_getter,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def validate_curator(
    authorization: HTTPAuthorizationCredentials = Depends(security),
    curator_service: CuratorRepository = Depends(curator_repository_getter),
) -> tuple[uuid.UUID, str]:
    curator_id = AuthService.get_curator_id_from_access(authorization.credentials)
    curator = await curator_service.get_by_id(curator_id)
    if not curator:
        raise HTTPException(status_code=401, detail="Incorrect access token")
    return curator_id, authorization.credentials


async def validate_refresh_token(
    refresh_token: str,
) -> uuid.UUID:
    curator_id = AuthService.get_curator_id_from_refresh(refresh_token)
    return curator_id
