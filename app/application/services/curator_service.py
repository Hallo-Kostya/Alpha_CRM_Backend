from fastapi import Depends
from app.application.dto.curator import (
    CuratorPOST,
    CuratorPATCH,
    CuratorPostBase,
)
from app.application.services.auth_service import AuthService, auth_service_getter
from app.domain.entities.teams.team import Team
from app.infrastructure.database.models import CuratorModel
from app.domain.entities.persons.curator import Curator
from app.application.services.base_service import BaseService
from app.domain.entities.auth_tokens.auth_token import AuthToken
from app.infrastructure.database.repositories.curator_repository import (
    CuratorRepository,
    curator_repository_getter,
)
from uuid import UUID
from typing import Sequence
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

    def _to_orm(self, scheme_: CuratorPOST) -> CuratorModel:
        return CuratorModel(
            hashed_password=scheme_.password,
            first_name=scheme_.first_name,
            last_name=scheme_.first_name,
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
            return auth_tokens
        except IntegrityError:
            return None

    async def login_curator(
        self, curator_data: CuratorPostBase, existing_curator: CuratorModel,
    ) -> tuple[AuthToken, AuthToken] | None:
        is_password_correct = self.auth_service.verify_password(curator_data.password, existing_curator.hashed_password)
        if not is_password_correct:
            return None
        auth_tokens = await self.auth_service.create_token_pair(existing_curator.id)
        return auth_tokens

    async def logout_curator(
            self, refresh_token: str
    ) -> None:
        await self.auth_service.revoke_token_pair(refresh_token)


def curator_service_getter(
    curator_repository: CuratorRepository = Depends(curator_repository_getter),
    auth_service: AuthService = Depends(auth_service_getter),
) -> CuratorService:
    return CuratorService(curator_repository, auth_service)
