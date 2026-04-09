from fastapi import Depends, UploadFile
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
    eager_loads = ['teams']

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

    def _to_orm(self, scheme) -> CuratorModel:
        return CuratorModel(
            hashed_password=scheme.password if hasattr(scheme, 'password') else scheme.hashed_password,
            first_name=scheme.first_name,
            last_name=scheme.last_name,
            email=scheme.email,
            patronymic=scheme.patronymic,
            tg_link=scheme.tg_link,
        )

    async def get_by_email(self, email: str) -> CuratorModel | None:
        curators = await self._repo.get_list(email=email)
        if curators:
            return curators[0]
        return None

    async def register_curator(
        self, curator_data: CuratorPOST
    ) -> tuple[AuthToken, AuthToken] | None:
        hashed_pass = self.auth_service.get_hashed_pass(curator_data.password)
        curator_data.password = hashed_pass
        try:
            created_obj = await self.create(curator_data)
            auth_tokens = await self.auth_service.create_token_pair(created_obj.id)
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
            avatar_s3_path=f"{settings.s3.public_host}/{settings.s3.curator_bucket.name}{avatar_file_path}")
        return await self.update(data_to_update, curator_id)


def curator_service_getter(
    curator_repository: CuratorRepository = Depends(curator_repository_getter),
    auth_service: AuthService = Depends(auth_service_getter),
) -> CuratorService:
    return CuratorService(curator_repository, auth_service)


def build_avatar_path(curator_id: UUID, file_name: str) -> str:
    return f"/avatars/{curator_id}/{file_name}"
