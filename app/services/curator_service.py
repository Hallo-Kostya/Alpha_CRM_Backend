from fastapi import Depends, UploadFile
from app.schemas.curator import CuratorPOST, CuratorPATCH, CuratorPostBase
from app.services.auth_service import AuthService, auth_service_getter
from app.core.config import settings
from app.infrastructure.database.models import CuratorModel
from app.schemas.curator import Curator
from app.schemas.auth import AuthToken
from app.infrastructure.database.repositories.curator_repository import (
    CuratorRepository,
    curator_repository_getter,
)
from uuid import UUID, uuid4
from sqlalchemy.exc import IntegrityError
from typing import List

from app.services.storage_service import StorageService, storage_service_getter


class CuratorService:
    def __init__(
        self,
        curator_repo: CuratorRepository,
        auth_service: AuthService,
        storage_service: StorageService,
    ):
        self._repo = curator_repo
        self.auth_service = auth_service
        self.storage_service = storage_service

    def _to_orm(self, scheme) -> CuratorModel:
        data = {
            "first_name": scheme.first_name,
            "last_name": scheme.last_name,
            "email": scheme.email,
            "patronymic": scheme.patronymic,
            "tg_link": scheme.tg_link,
        }
        if hasattr(scheme, 'password') and scheme.password:
            data["hashed_password"] = self.auth_service.get_hashed_pass(scheme.password)
        elif hasattr(scheme, 'hashed_password'):
            data["hashed_password"] = scheme.hashed_password
        return CuratorModel(**data)

    def _to_schema(self, orm_model: CuratorModel) -> Curator:
        return Curator.model_validate(orm_model, from_attributes=True)

    async def create(self, curator_data: CuratorPOST) -> Curator:
        orm_obj = self._to_orm(curator_data)
        created_obj = await self._repo.create(orm_obj)
        created_obj = await self._repo.get_by_id(created_obj.id, eager_loads=['teams'])
        return self._to_schema(created_obj)

    async def update(self, curator_id: UUID, data: CuratorPATCH) -> Curator | None:
        old_obj = await self._repo.get_by_id(curator_id, eager_loads=['teams'])
        if not old_obj:
            return None
        updated_obj = await self._repo.update(
            old_obj, data.model_dump(exclude_unset=True)
        )
        updated_obj = await self._repo.get_by_id(curator_id, eager_loads=['teams'])
        return self._to_schema(updated_obj)

    async def delete(self, curator_id: UUID) -> bool:
        obj = await self._repo.get_by_id(curator_id)
        if not obj:
            return False

        if obj.avatar_s3_path:
            try:
                key = obj.avatar_s3_path.split(f"{settings.s3.curator_bucket.name}/", 1)[1]
                await self.storage_service.delete_curator_img(key)
            except Exception:
                pass
        
        await self._repo.delete(obj)
        return True

    async def get_by_id(self, curator_id: UUID) -> Curator | None:
        obj = await self._repo.get_by_id(curator_id, eager_loads=['teams'])
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_list(self, **filter_attrs) -> List[Curator]:
        total, items = await self._repo.get_list(eager_loads=['teams'], **filter_attrs)
        return [self._to_schema(item) for item in items]

    async def get_by_email(self, email: str) -> Curator | None:
        total, curators = await self._repo.get_list(filters={"email": email})
        if curators:
            return self._to_schema(curators[0])
        return None

    async def register_curator(
        self, curator_data: CuratorPOST
    ) -> tuple[AuthToken, AuthToken] | None:
        try:
            created_obj = await self.create(curator_data)
            auth_tokens = await self.auth_service.create_token_pair(created_obj.id)
            return auth_tokens
        except IntegrityError:
            return None


    async def login_curator(
        self,
        curator_data: CuratorPostBase,
    ) -> tuple[AuthToken, AuthToken] | None:
        """Login curator by email and password."""
        total, curators = await self._repo.get_list(filters={"email": curator_data.email})
        if not curators:
            return None
        
        existing_curator = curators[0]
        is_password_correct = self.auth_service.verify_password(
            curator_data.password, existing_curator.hashed_password
        )
        if not is_password_correct:
            return None
        
        auth_tokens = await self.auth_service.create_token_pair(existing_curator.id)
        return auth_tokens
    
    async def logout_curator(self, refresh_token: str) -> None:
        await self.auth_service.revoke_token_pair(refresh_token)

    async def _build_avatar_path(curator_id: UUID, file_name: str) -> str:
        return await f"avatars/{curator_id}/{file_name}"

    async def upload_avatar(
        self,
        file: UploadFile,
        curator_id: UUID,
        old_key: str | None = None,
    ) -> Curator:

        key = await self.storage_service.upload_curator_img(
            file=file,
            key_prefix=f"avatars/{curator_id}"
        )

        data_to_update = CuratorPATCH(
            avatar_s3_path=key
        )

        try:
            updated_curator = await self.update(
                curator_id,
                data_to_update,
            )

        except Exception:
            await self.storage_service.delete_curator_img(key)
            raise

        if old_key:
            try:
                await self.storage_service.delete_curator_img(old_key)

            except Exception as e:
                pass

        return updated_curator


def curator_service_getter(
    curator_repository: CuratorRepository = Depends(curator_repository_getter),
    auth_service: AuthService = Depends(auth_service_getter),
    storage_service: StorageService = Depends(storage_service_getter),
) -> CuratorService:
    return CuratorService(curator_repository, auth_service, storage_service)