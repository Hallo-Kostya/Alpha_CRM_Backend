from fastapi import APIRouter

router = APIRouter(prefix="/auth")


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
async def register_user():
    pass
