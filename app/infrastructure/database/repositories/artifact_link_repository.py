# app/infrastructure/database/repositories/artifact_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy import func, select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.common.enums import ArtifactEntityType
from app.infrastructure.database.database import db_helper

from app.infrastructure.database.models.artifacts.artifact_link import ArtifactLinkModel
from app.infrastructure.database.repositories.base_repository import BaseRepository


class ArtifactLinkRepository(BaseRepository[ArtifactLinkModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ArtifactLinkModel, session)
        
    async def attach(
        self,
        artifact_id: UUID,
        entity_type: ArtifactEntityType,
        entity_id: UUID,
    ) -> ArtifactLinkModel:
        link = ArtifactLinkModel(
            artifact_id=artifact_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        self.session.add(link)

        await self.session.commit()
        await self.session.refresh(link)

        return link
        
    async def exists(
        self,
        artifact_id: UUID,
        entity_type: ArtifactEntityType,
        entity_id: UUID,
    ) -> bool:
        stmt = select(ArtifactLinkModel.id).where(
            ArtifactLinkModel.artifact_id == artifact_id,
            ArtifactLinkModel.entity_type == entity_type,
            ArtifactLinkModel.entity_id == entity_id,
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None
    
    async def detach(
        self,
        artifact_id: UUID,
        entity_type: ArtifactEntityType,
        entity_id: UUID,
    ) -> None:
        stmt = delete(ArtifactLinkModel).where(
            ArtifactLinkModel.artifact_id == artifact_id,
            ArtifactLinkModel.entity_type == entity_type,
            ArtifactLinkModel.entity_id == entity_id,
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_all(
        self,
        artifact_id: UUID,
    ) -> None:
        stmt = delete(ArtifactLinkModel).where(
            ArtifactLinkModel.artifact_id == artifact_id
        )

        await self.session.execute(stmt)
        await self.session.commit()
            
    async def count_links(
        self,
        artifact_id: UUID,
    ) -> int:
        stmt = select(func.count()).where(
            ArtifactLinkModel.artifact_id == artifact_id
        )

        result = await self.session.execute(stmt)

        return result.scalar_one()

async def artifact_link_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter)
    ) -> BaseRepository:
    repository = ArtifactLinkRepository(session)
    return repository
    