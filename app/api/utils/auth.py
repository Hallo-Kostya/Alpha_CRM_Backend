
from fastapi import Depends, Header, HTTPException
from app.application.services.auth_service import AuthService
from app.infrastructure.database.repositories.curator_repository import CuratorRepository, curator_repository_getter


async def validate_curator(authorization:  str = Header(...), curator_service: CuratorRepository = Depends(curator_repository_getter)):
    curator_id = AuthService.get_curator_id_from_token(authorization)
    curator = await curator_service.get_by_id(curator_id)
    if not curator:
        raise HTTPException(
                    status_code=401,
                    detail="Incorrect access token"
        )
    return curator_id
