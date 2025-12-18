from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.application.dto.curator import (
    CuratorPATCH,
    CuratorPOST,
)
from app.application.services.curator_service import CuratorService, curator_service_getter
from app.domain.entities.auth_tokens.auth_token import AuthToken


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Curator not found"}}
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
)
async def register_user(data: CuratorPOST, service: CuratorService = Depends(curator_service_getter)):
    token_pair = await service.register_curator(data)
    return token_pair


@router.get("/")
async def list_curators(
    service: CuratorService = Depends(curator_service_getter)
):
    """Получить список всех проектов (с фильтрами можно расширить позже)."""
    return await service.get_list()