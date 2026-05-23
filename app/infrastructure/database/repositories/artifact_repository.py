# app/infrastructure/database/repositories/artifact_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.common.enums import ArtifactEntityType
from app.infrastructure.database.database import db_helper

from app.infrastructure.database.models.artifacts.artifact import ArtifactModel
from app.infrastructure.database.models.artifacts.artifact_link import ArtifactLinkModel
from app.infrastructure.database.repositories.base_repository import BaseRepository


class ArtifactRepository(BaseRepository[ArtifactModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(ArtifactModel, session)

    async def get_by_checksum(self, checksum: str) -> Optional[ArtifactModel]:
        result = await self.session.execute(
            select(ArtifactModel).where(ArtifactModel.checksum == checksum)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, artifact_id: UUID) -> Optional[ArtifactModel]:
        result = await self.session.execute(
            select(ArtifactModel)
            .where(ArtifactModel.id == artifact_id)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
    ) -> list[ArtifactModel]:
        stmt = (
            select(ArtifactModel)
            .join(
                ArtifactLinkModel,
                ArtifactLinkModel.artifact_id == ArtifactModel.id,
            )
        )
        
        if project_id:
            stmt = stmt.where(
                ArtifactLinkModel.entity_type
                == ArtifactEntityType.PROJECT,

                ArtifactLinkModel.entity_id
                == project_id,
            )
            
        if meeting_id:
            stmt = stmt.where(
                ArtifactLinkModel.entity_type
                == ArtifactEntityType.MEETING,

                ArtifactLinkModel.entity_id
                == meeting_id,
            )
            
        result = await self.session.execute(stmt)

        return list(result.scalars().unique().all())
    
    async def delete_by_id(self, id: UUID):
        stmt = delete(self.model).where(self.model.id == id)
        await self.session.execute(stmt)
        await self.session.commit()

async def artifact_repository_getter(
    session: AsyncSession = Depends(db_helper.session_getter)
    ) -> BaseRepository:
    repository = ArtifactRepository(session)
    return repository
    