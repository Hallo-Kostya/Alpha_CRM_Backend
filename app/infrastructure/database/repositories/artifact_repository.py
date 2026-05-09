# app/infrastructure/database/repositories/artifact_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.infrastructure.database.database import db_helper

from app.infrastructure.database.models.artifacts.artifact import ArtifactModel
from app.infrastructure.database.models.artifacts.artifact_link import ArtifactLinkModel
from app.infrastructure.database.repositories.base_repository import BaseRepository


class ArtifactRepository(BaseRepository[ArtifactModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ArtifactModel, session)

    async def get_by_id_with_links(self, artifact_id: UUID) -> Optional[ArtifactModel]:
        query = (
            select(self.model)
            .where(self.model.id == artifact_id)
            .options(selectinload(self.model.artifact_links))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_project(self, project_id: UUID) -> List[ArtifactModel]:
        query = (
            select(self.model)
            .join(ArtifactLinkModel)
            .where(ArtifactLinkModel.project_id == project_id)
            .options(selectinload(self.model.artifact_links))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_meeting(self, meeting_id: UUID) -> List[ArtifactModel]:
        query = (
            select(self.model)
            .join(ArtifactLinkModel)
            .where(ArtifactLinkModel.meeting_id == meeting_id)
            .options(selectinload(self.model.artifact_links))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def delete_links_by_artifact(self, artifact_id: UUID) -> None:
        await self.session.execute(
            delete(ArtifactLinkModel).where(ArtifactLinkModel.artifact_id == artifact_id)
        )
        await self.session.commit()

    async def get_by_project_and_artifact(self, project_id: UUID, artifact_id: UUID) -> Optional[ArtifactLinkModel]:
        query = (
            select(ArtifactLinkModel)
            .where(
                ArtifactLinkModel.project_id == project_id,
                ArtifactLinkModel.artifact_id == artifact_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_meeting_and_artifact(self, meeting_id: UUID, artifact_id: UUID) -> Optional[ArtifactLinkModel]:
        query = (
            select(ArtifactLinkModel)
            .where(
                ArtifactLinkModel.meeting_id == meeting_id,
                ArtifactLinkModel.artifact_id == artifact_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


async def artifact_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter)
    ) -> BaseRepository:
    repository = ArtifactRepository(session)
    return repository
    