import uuid
from fastapi import APIRouter, File, UploadFile
from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.application.dto.curator import (
    CuratorPATCH,
    CuratorPOST,
    CuratorPostBase,
)
from app.application.services.curator_service import (
    CuratorService,
    curator_service_getter,
)
from app.application.services.auth_service import (
    AuthService,
    auth_service_getter,
)
from app.domain.entities.auth_tokens.auth_token import AuthToken
from app.api.utils.auth import validate_curator
from app.api.utils.responses import OkResponse


router = APIRouter(
    prefix="/auth", tags=["auth"], responses={404: {"description": "Curator not found"}}
)


@router.post(
    "/register",
    description="""
            Метод для регистрации пользователя.
            После успешной регистрации создается запись о пользователе в PG.
            Пароль сохраняется в хешированном виде.

            params:
                - email - outlook почта пользователя
                - password - пароль (8+ символов)
                - first_name - имя
                - last_name - фамилия
                - patronymic - отчество (опционально)
                - avatar - аватар (опционально)
            returns:
                - access_token - токен доступа jwt
                - refresh_token - токен для рефреша пары jwt токенов
        """,
    response_model=tuple[AuthToken, AuthToken],
)
async def register_curator(
    data: CuratorPOST,
    service: CuratorService = Depends(curator_service_getter)
):
    token_pair = await service.register_curator(data)
    if not token_pair:
        raise HTTPException(status_code=401, detail="User with this email already exists")
    return token_pair


@router.post("/login")
async def login_curator(
        data: CuratorPostBase,
        service: CuratorService = Depends(curator_service_getter)):
    existing_curator = await service.get_by_email(data.email)
    if not existing_curator:
        raise HTTPException(status_code=401, detail="User with this email is not registered")
    token_pair = await service.login_curator(data, existing_curator)
    if not token_pair:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return token_pair


@router.post("/logout")
async def logout_curator(
        refresh_token: str,
        service: CuratorService = Depends(curator_service_getter),
        credentials: tuple[uuid.UUID, str] = Depends(validate_curator)):
    try:
        await service.logout_curator(refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Refresh Token")
    return OkResponse("successfully logout")


@router.post("/token/refresh", response_model=tuple[AuthToken, AuthToken])
async def refresh_tokens(
        refresh_token: str,
        auth_service: AuthService = Depends(auth_service_getter)):
    owner_id = auth_service.get_curator_id_from_refresh(refresh_token)
    try:
        token_pair = await auth_service.refresh_token_pair(refresh_token, owner_id)
        return token_pair
    except ValueError:
        raise HTTPException(status_code=401, detail="Token had already been invoked")


@router.get("/me")
async def get_me(
        credentials: tuple[uuid.UUID, str] = Depends(validate_curator),
        service: CuratorService = Depends(curator_service_getter)):
    curator_id, _ = credentials
    return await service.get_by_id(curator_id)


@router.get("/{curator_id}")
async def get_curator(curator_id: uuid.UUID, service: CuratorService = Depends(curator_service_getter)):
    return await service.get_by_id(curator_id)


@router.get("/")
async def list_curators(service: CuratorService = Depends(curator_service_getter)):
    return await service.get_list()


@router.post("/avatar")
async def upload_file(
    file: UploadFile = File(...),
    service: CuratorService = Depends(curator_service_getter),
    credentials: tuple[uuid.UUID, str] = Depends(validate_curator),
):
    if file.size and file.size > 50 * 1024 * 1024:
        raise HTTPException(400, "File too large")
    curator_id, _ = credentials
    updated_curator = await service.upload_avatar(file, curator_id)
    if not updated_curator:
        raise HTTPException(status_code=401, detail="User with this id was not found")
    return updated_curator
