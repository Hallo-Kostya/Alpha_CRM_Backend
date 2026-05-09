# app/services/artifact_service.py
import mimetypes
from typing import List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, UploadFile, status

from app.infrastructure.database.models.artifacts.artifact import ArtifactModel
from app.infrastructure.database.models.artifacts.artifact_link import ArtifactLinkModel
from app.infrastructure.database.repositories.artifact_repository import (
    ArtifactRepository,
    artifact_repository_getter,
)
from app.core.config import settings
from app.common.enums import ArtifactType
from app.schemas.artifacts import ArtifactCreate, ArtifactFileUpload, ArtifactResponse, ArtifactUpdate
from app.services.storage_service import StorageService


class ArtifactService:
    def __init__(self, artifact_repo: ArtifactRepository, storage_service: StorageService):
        self._repo = artifact_repo
        self.storage_service = storage_service

    def _to_schema(self, orm_model: ArtifactModel) -> dict:
        """Преобразуем ORM в словарь для Pydantic"""
        return ArtifactResponse.model_validate(orm_model, from_attributes=True).model_dump()

    async def create_link_artifact(self, data: ArtifactCreate) -> dict:
        """Создать артефакт-ссылку (URL, видео)"""
        # Валидация привязки
        self._validate_target(data.project_id, data.meeting_id)
        
        # Для ссылок и видео URL обязателен
        if data.type in (ArtifactType.LINK, ArtifactType.VIDEO) and not data.url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"URL обязателен для типа {data.type.value}"
            )

        # Создаём артефакт
        artifact = ArtifactModel(
            name=data.name,
            description=data.description,
            type=data.type,
            url=data.url or "",
        )
        created = await self._repo.create(artifact)
        
        # Создаём связь
        await self._create_link(created.id, data.project_id, data.meeting_id)
        
        # Перезагружаем с связями
        refreshed = await self._repo.get_by_id_with_links(created.id)
        return self._to_schema(refreshed)

    async def upload_file_artifact(
        self,
        file: UploadFile,
        meta: ArtifactFileUpload,
    ) -> dict:
        """Загрузить файл в S3 и создать артефакт"""
        self._validate_target(meta.project_id, meta.meeting_id)
        
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен иметь имя"
            )

        # Определяем тип контента
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        
        # Определяем ArtifactType по MIME
        artifact_type = self._detect_type_by_mime(content_type)
        
        # Читаем файл
        content = await file.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл пустой"
            )

        # Генерируем ключ для S3
        import uuid
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else ''
        s3_key = f"artifacts/{uuid.uuid4()}/{file.filename}"
        
        # Загружаем в S3
        url = await self._s3.put_object(
            key=s3_key,
            body=content,
            content_type=content_type,
        )

        # Создаём артефакт
        artifact = ArtifactModel(
            name=meta.name or file.filename,
            description=meta.description,
            type=artifact_type,
            url=url,
        )
        created = await self._repo.create(artifact)
        
        # Создаём связь
        await self._create_link(created.id, meta.project_id, meta.meeting_id)
        
        refreshed = await self._repo.get_by_id_with_links(created.id)
        return self._to_schema(refreshed)

    async def get_by_id(self, artifact_id: UUID) -> Optional[dict]:
        obj = await self._repo.get_by_id_with_links(artifact_id)
        if not obj:
            return None
        return self._to_schema(obj)

    async def get_by_project(self, project_id: UUID) -> List[dict]:
        items = await self._repo.get_by_project(project_id)
        return [self._to_schema(item) for item in items]

    async def get_by_meeting(self, meeting_id: UUID) -> List[dict]:
        items = await self._repo.get_by_meeting(meeting_id)
        return [self._to_schema(item) for item in items]

    async def update(self, artifact_id: UUID, data: ArtifactUpdate) -> Optional[dict]:
        old = await self._repo.get_by_id(artifact_id)
        if not old:
            return None
        
        updated = await self._repo.update(old, data.model_dump(exclude_unset=True))
        return self._to_schema(updated)

    async def delete(self, artifact_id: UUID) -> bool:
        """Удалить артефакт и файл из S3 (если есть)"""
        obj = await self._repo.get_by_id_with_links(artifact_id)
        if not obj:
            return False

        # Удаляем файл из S3 если это не просто ссылка
        if obj.type == ArtifactType.FILE and obj.url:
            try:
                # Извлекаем ключ из URL: public_host/bucket/key
                # URL формат: {public_host}/{bucket}/{key}
                key = self._extract_s3_key(obj.url)
                if key:
                    await self._s3.delete_object(key)
            except Exception:
                pass  # Логируем, но не падаем

        # Удаляем связи
        await self._repo.delete_links_by_artifact(artifact_id)
        
        # Удаляем артефакт
        await self._repo.delete(obj)
        return True

    async def attach_to_project(self, artifact_id: UUID, project_id: UUID) -> None:
        """Привязать существующий артефакт к проекту"""
        existing = await self._repo.get_by_project_and_artifact(project_id, artifact_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Артефакт уже привязан к этому проекту"
            )
        await self._create_link(artifact_id, project_id=project_id, meeting_id=None)

    async def attach_to_meeting(self, artifact_id: UUID, meeting_id: UUID) -> None:
        """Привязать существующий артефакт к встрече"""
        existing = await self._repo.get_by_meeting_and_artifact(meeting_id, artifact_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Артефакт уже привязан к этой встрече"
            )
        await self._create_link(artifact_id, project_id=None, meeting_id=meeting_id)

    async def detach_from_project(self, artifact_id: UUID, project_id: UUID) -> None:
        """Отвязать артефакт от проекта"""
        from sqlalchemy import delete
        await self._repo.session.execute(
            delete(ArtifactLinkModel).where(
                ArtifactLinkModel.artifact_id == artifact_id,
                ArtifactLinkModel.project_id == project_id,
            )
        )
        await self._repo.session.commit()

    async def detach_from_meeting(self, artifact_id: UUID, meeting_id: UUID) -> None:
        """Отвязать артефакт от встречи"""
        from sqlalchemy import delete
        await self._repo.session.execute(
            delete(ArtifactLinkModel).where(
                ArtifactLinkModel.artifact_id == artifact_id,
                ArtifactLinkModel.meeting_id == meeting_id,
            )
        )
        await self._repo.session.commit()

    def _validate_target(self, project_id: Optional[UUID], meeting_id: Optional[UUID]) -> None:
        if not project_id and not meeting_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Необходимо указать project_id или meeting_id"
            )
        if project_id and meeting_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Можно указать только один из: project_id или meeting_id"
            )

    async def _create_link(
        self,
        artifact_id: UUID,
        project_id: Optional[UUID] = None,
        meeting_id: Optional[UUID] = None,
    ) -> None:
        link = ArtifactLinkModel(
            artifact_id=artifact_id,
            project_id=project_id,
            meeting_id=meeting_id,
        )
        self._repo.session.add(link)
        await self._repo.session.commit()

    @staticmethod
    def _detect_type_by_mime(content_type: str) -> ArtifactType:
        if content_type.startswith("video/"):
            return ArtifactType.VIDEO
        return ArtifactType.FILE

    @staticmethod
    def _extract_s3_key(url: str) -> Optional[str]:
        """Извлечь ключ из S3 URL"""
        # Формат: {public_host}/{bucket_name}/artifacts/uuid/filename
        try:
            # Находим bucket в URL и берём всё после него
            parts = url.split("/")
            # Ищем индекс bucket name — обычно это предпоследняя часть перед ключом
            # Проще: берём всё после 4-го слеша (http://host/bucket/key)
            from urllib.parse import urlparse
            path = urlparse(url).path  # /bucket/artifacts/uuid/file
            # Убираем ведущий слеш и bucket name
            path = path.lstrip("/")
            bucket_name = settings.s3.artifacts_bucket.name
            if path.startswith(bucket_name + "/"):
                return path[len(bucket_name) + 1:]
            return path
        except Exception:
            return None


def artifact_service_getter(
    repo: ArtifactRepository = Depends(artifact_repository_getter),
) -> ArtifactService:
    return ArtifactService(repo)