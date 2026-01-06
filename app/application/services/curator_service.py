from fastapi import Depends, UploadFile
import requests
from app.application.dto.curator import (
    CuratorPOST,
    CuratorPATCH,
    CuratorPostBase,
)
from app.application.services.auth_service import AuthService, auth_service_getter
from app.core.config import settings
from app.infrastructure.database.models import CuratorModel
from app.domain.entities.persons.curator import Curator
from app.application.services.base_service import BaseService
from app.domain.entities.auth_tokens.auth_token import AuthToken
from app.infrastructure.database.repositories.curator_repository import (
    CuratorRepository,
    curator_repository_getter,
)
from app.infrastructure.s3_storage.s3_client import S3Client
from uuid import UUID
from sqlalchemy.exc import IntegrityError


class CuratorService(BaseService[CuratorModel, Curator]):
    """
    Application Service для проектов.
    Содержит CRUD и место для доменной логики (start, complete, archive).
    """

    orm_model = CuratorModel
    pyd_scheme = Curator

    def __init__(
        self,
        curator_repo: CuratorRepository,
        auth_service: AuthService,
    ):
        super().__init__(curator_repo)
        self.auth_service = auth_service
        self.s3_client = S3Client(
            settings.s3.curator_bucket.name, settings.s3.curator_bucket.policy,
        )

    def _to_orm(self, scheme_: CuratorPOST) -> CuratorModel:
        return CuratorModel(
            hashed_password=scheme_.password,
            first_name=scheme_.first_name,
            last_name=scheme_.last_name,
            email=scheme_.email,
            patronymic=scheme_.patronymic,
            tg_link=scheme_.tg_link,
        )

    async def get_by_email(self, email: str) -> CuratorModel | None:
        curators = await self._repo.get_list(email=email)
        if curators:
            return curators[0]
        return None

    async def _create(self, new_obj: CuratorPOST) -> CuratorModel:
        orm_model = self._to_orm(new_obj)
        created_obj = await self._repo.create(orm_model)
        return created_obj

    async def update(self, new_data: CuratorPATCH, curator_id: UUID) -> Curator | None:
        old_obj = await self._repo.get_by_id(curator_id)
        if not old_obj:
            return None
        updated_obj = await self._repo.update(
            old_obj, new_data.model_dump(exclude_unset=True)
        )
        return self._to_schema(updated_obj)

    async def register_curator(
        self, curator_data: CuratorPOST
    ) -> tuple[AuthToken, AuthToken] | None:
        hashed_pass = self.auth_service.get_hashed_pass(curator_data.password)
        curator_data.password = hashed_pass
        try:
            created_obj = await self._create(curator_data)
            auth_tokens = await self.auth_service.create_token_pair(created_obj.id)
            notify_auth(created_obj.id, created_obj.email)
            return auth_tokens
        except IntegrityError:
            return None

    async def login_curator(
        self,
        curator_data: CuratorPostBase,
        existing_curator: CuratorModel,
    ) -> tuple[AuthToken, AuthToken] | None:
        is_password_correct = self.auth_service.verify_password(
            curator_data.password, existing_curator.hashed_password
        )
        if not is_password_correct:
            return None
        auth_tokens = await self.auth_service.create_token_pair(existing_curator.id)
        notify_auth(existing_curator.id, existing_curator.email)
        return auth_tokens

    async def logout_curator(self, refresh_token: str) -> None:
        await self.auth_service.revoke_token_pair(refresh_token)

    async def upload_avatar(
        self,
        file: UploadFile,
        curator_id: UUID,
    ) -> Curator | None:
        avatar_file_path = build_avatar_path(
            curator_id, file.filename if file.filename else "default.jpg"
        )
        self.s3_client.put_object(avatar_file_path, file)
        data_to_update = CuratorPATCH(
            avatar_s3_path=f"{settings.s3.public_host}/{settings.s3.curator_bucket.name}/{avatar_file_path}")
        return await self.update(data_to_update, curator_id)


def curator_service_getter(
    curator_repository: CuratorRepository = Depends(curator_repository_getter),
    auth_service: AuthService = Depends(auth_service_getter),
) -> CuratorService:
    return CuratorService(curator_repository, auth_service)


def build_avatar_path(curator_id: UUID, file_name: str) -> str:
    return f"avatars/{curator_id}/{file_name}"


def notify_auth(user_id: UUID, email: str):
    requests.post(
        settings.yandex_log.url,
        json={
            "event": "user_authenticated",
            "user_id": str(user_id),
            "email": email
        },
        timeout=2
    )