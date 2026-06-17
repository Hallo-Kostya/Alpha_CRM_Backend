# app/services/artifact_service.py
import hashlib
from uuid import UUID
from fastapi import Depends, UploadFile

from app.infrastructure.database.models.artifacts.artifact import ArtifactModel
from app.infrastructure.database.repositories.artifact_link_repository import ArtifactLinkRepository, artifact_link_repository_getter
from app.infrastructure.database.repositories.artifact_repository import (
    ArtifactRepository,
    artifact_repository_getter,
)
from app.common.enums import ArtifactEntityType, ArtifactType
from app.schemas.artifacts import ArtifactResponse
from app.services.storage_service import StorageService, storage_service_getter
from uuid import uuid4


class ArtifactService:
    def __init__(self, artifact_repo: ArtifactRepository, storage_service: StorageService, link_repo: ArtifactLinkRepository):
        self.artifact_repo = artifact_repo
        self.link_repo = link_repo
        self.s3_client = storage_service

    def _to_schema(self, orm_model: ArtifactModel) -> dict:
        """Преобразуем ORM в словарь для Pydantic"""
        return ArtifactResponse.model_validate(orm_model, from_attributes=True).model_dump()


    async def create_and_attach(
        self,
        file: UploadFile,
        entity_type: ArtifactEntityType,
        entity_id: UUID,
    ) -> ArtifactModel:

        content = await file.read()

        checksum = hashlib.sha256(content).hexdigest()

        artifact = await self.artifact_repo.get_by_checksum(
            checksum
        )

        if not artifact:
            s3_key = str(uuid4())

            try:
                await self.s3_client.upload_artifacts(
                    content=content,
                    key=s3_key,
                    content_type=file.content_type,
                )

                artifact = ArtifactModel(
                    name=file.filename,
                    checksum=checksum,
                    size=len(content),
                    type=ArtifactType.FILE,
                    content_type=file.content_type,
                    s3_key=s3_key,
                )

                artifact = await self.artifact_repo.create(
                    artifact
                )

            except Exception:
                await self.s3_client.delete_artifacts(
                    s3_key
                )
                raise

        exists = await self.link_repo.exists(
            artifact_id=artifact.id,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        if not exists:
            await self.link_repo.attach(
                artifact_id=artifact.id,
                entity_type=entity_type,
                entity_id=entity_id,
            )

        return artifact
    
    
    async def list(
        self,
        project_id: UUID | None = None,
        meeting_id: UUID | None = None,
    ):
        return await self.artifact_repo.list(
            project_id=project_id,
            meeting_id=meeting_id,
        )
        
    
    async def detach(
        self,
        artifact_id: UUID,
        entity_type: ArtifactEntityType,
        entity_id: UUID,
    ):
        await self.link_repo.detach(
            artifact_id=artifact_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        links_count = await self.link_repo.count_links(
            artifact_id
        )

        if links_count == 0:
            artifact = await self.artifact_repo.get_by_id(
                artifact_id
            )

            if artifact:
                await self.s3_client.delete_artifacts(
                    artifact.s3_key
                )

                await self.artifact_repo.delete_by_id(
                    artifact_id
                )

    
    async def delete(
        self,
        artifact_id: UUID,
    ):
        artifact = await self.artifact_repo.get_by_id(
            artifact_id
        )

        if not artifact:
            return

        await self.link_repo.delete_all(
            artifact_id
        )

        await self.s3_client.delete_artifacts(
            artifact.s3_key
        )

        await self.artifact_repo.delete_by_id(
            artifact_id
        )
    


def artifact_service_getter(
    repo: ArtifactRepository = Depends(artifact_repository_getter),
    storage_service: StorageService = Depends(storage_service_getter),
    link_repo: ArtifactLinkRepository = Depends(artifact_link_repository_getter),
) -> ArtifactService:
    return ArtifactService(repo, storage_service, link_repo)