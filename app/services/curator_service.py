from fastapi import Depends, UploadFile
from app.schemas.curator import (
    CuratorPOST,
    CuratorPATCH,
    CuratorPostBase,
)
from app.services.auth_service import AuthService, auth_service_getter
from app.core.config import settings
from app.infrastructure.database.models import CuratorModel
from app.schemas.curator import Curator
from app.schemas.entities.auth_tokens.auth_token import AuthToken
from app.infrastructure.database.repositories.curator_repository import (
    CuratorRepository,
    curator_repository_getter,
)
from app.infrastructure.s3_storage.s3_client import S3Client
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from typing import List


class CuratorService:
    """
    Application service for curators.
    Contains CRUD and business logic.
    """

    def __init__(
        self,
        curator_repo: CuratorRepository,
        auth_service: AuthService,
    ):
        self._repo = curator_repo
        self.auth_service = auth_service
        self.s3_client = S3Client(
            settings.s3.curator_bucket.name, settings.s3.curator_bucket.policy,
        )

    def _to_orm(self, scheme) -> CuratorModel:
        """Convert schema to ORM model."""
        return CuratorModel(
            hashed_password=scheme.password if hasattr(scheme, 'password') else scheme.hashed_password,
            first_name=scheme.first_name,
            last_name=scheme.last_name,
            email=scheme.email,
            patronymic=scheme.patronymic,
            tg_link=scheme.tg_link,
        )

    def _to_schema(self, orm_model: CuratorModel) -> Curator:
        """Convert ORM model to schema."""
        return Curator.model_validate(orm_model, from_attributes=True)

    async def create(self, curator_data: CuratorPOST) -> Curator:
        """Create new curator."""
        orm_obj = self._to_orm(curator_data)
        created_obj = await self._repo.create(orm_obj)
        created_obj = await self._repo.get_by_id(created_obj.id, eager_loads=['teams'])
        return self._to_schema(created_obj)

    async def update(self, curator_id: UUID, data: CuratorPATCH) -> Curator | None:
        """Update curator."""
        old_obj = await self._repo.get_by_id(curator_id, eager_loads=['teams'])
        if not old_obj:
            return None
        updated_obj = await self._repo.update(
            old_obj, data.model_dump(exclude_unset=True)
        )
        updated_obj = await self._repo.get_by_id(curator_id, eager_loads=['teams'])
        return self._to_schema(updated_obj)

    async def delete(self, curator_id: UUID) -> bool:
        """Delete curator."""
        obj = await self._repo.get_by_id(curator_id)
        if not obj:
            return False
        await self._repo.delete(obj)
        return True

    async def get_by_id(self, curator_id: UUID) -> Curator | None:
        """Get curator by ID."""
        obj = await self._repo.get_by_id(curator_id, eager_loads=['teams'])
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_list(self, **filter_attrs) -> List[Curator]:
        """Get list of curators."""
        items = await self._repo.get_list(eager_loads=['teams'], **filter_attrs)
        return [self._to_schema(item) for item in items]

    async def get_by_email(self, email: str) -> CuratorModel | None:
        """Get curator by email."""
        curators = await self._repo.get_list(email=email)
        if curators:
            return curators[0]
        return None

    async def register_curator(
        self, curator_data: CuratorPOST
    ) -> tuple[AuthToken, AuthToken] | None:
        """Register new curator."""
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
        """Login curator."""
        is_password_correct = self.auth_service.verify_password(
            curator_data.password, existing_curator.hashed_password
        )
        if not is_password_correct:
            return None
        auth_tokens = await self.auth_service.create_token_pair(existing_curator.id)
        return auth_tokens

    async def logout_curator(self, refresh_token: str) -> None:
        """Logout curator."""
        await self.auth_service.revoke_token_pair(refresh_token)

    async def upload_avatar(
        self,
        file: UploadFile,
        curator_id: UUID,
    ) -> Curator | None:
        """Upload curator avatar."""
        avatar_file_path = build_avatar_path(
            curator_id, file.filename if file.filename else "default.jpg"
        )
        self.s3_client.put_object(avatar_file_path, file)
        data_to_update = CuratorPATCH(
            avatar_s3_path=f"{settings.s3.public_host}/{settings.s3.curator_bucket.name}{avatar_file_path}")
        return await self.update(curator_id, data_to_update)


def curator_service_getter(
    curator_repository: CuratorRepository = Depends(curator_repository_getter),
    auth_service: AuthService = Depends(auth_service_getter),
) -> CuratorService:
    return CuratorService(curator_repository, auth_service)


def build_avatar_path(curator_id: UUID, file_name: str) -> str:
    return f"/avatars/{curator_id}/{file_name}"
