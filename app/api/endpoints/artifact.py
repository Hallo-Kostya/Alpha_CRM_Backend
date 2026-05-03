# app/api/v1/artifacts.py
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response

from app.schemas.artifacts import ArtifactCreate, ArtifactFileUpload, ArtifactResponse, ArtifactUpdate
from app.services.artifact_service import ArtifactService, artifact_service_getter

router = APIRouter(
    prefix="/artifacts",
    tags=["artifacts"],
    responses={404: {"description": "Artifact not found"}},
)


@router.post("/link", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def create_link_artifact(
    data: ArtifactCreate,
    service: ArtifactService = Depends(artifact_service_getter),
):
    """Создать артефакт-ссылку (URL, видео-ссылку) и привязать к проекту или встрече."""
    return await service.create_link_artifact(data)


@router.post("/upload", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_artifact(
    file: UploadFile = File(..., description="Файл для загрузки"),
    name: Optional[str] = Form(None, description="Название артефакта (если не указано — имя файла)"),
    description: Optional[str] = Form(None),
    project_id: Optional[UUID] = Form(None),
    meeting_id: Optional[UUID] = Form(None),
    service: ArtifactService = Depends(artifact_service_getter),
):
    """Загрузить файл в S3, создать артефакт и привязать к проекту/встрече."""
    meta = ArtifactFileUpload(
        name=name,
        description=description,
        project_id=project_id,
        meeting_id=meeting_id,
    )
    return await service.upload_file_artifact(file, meta)


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: UUID,
    service: ArtifactService = Depends(artifact_service_getter),
):
    """Получить артефакт по ID."""
    artifact = await service.get_by_id(artifact_id)
    if not artifact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Артефакт с ID {artifact_id} не найден"
        )
    return artifact


@router.patch("/{artifact_id}", response_model=ArtifactResponse)
async def update_artifact(
    artifact_id: UUID,
    data: ArtifactUpdate,
    service: ArtifactService = Depends(artifact_service_getter),
):
    """Обновить название/описание артефакта."""
    updated = await service.update(artifact_id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Артефакт с ID {artifact_id} не найден"
        )
    return updated


@router.delete("/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artifact(
    artifact_id: UUID,
    service: ArtifactService = Depends(artifact_service_getter),
):
    """Удалить артефакт и файл из S3 (если применимо)."""
    deleted = await service.delete(artifact_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Артефакт с ID {artifact_id} не найден"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{artifact_id}/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def attach_to_project(
    artifact_id: UUID,
    project_id: UUID,
    service: ArtifactService = Depends(artifact_service_getter),
):
    """Привязать существующий артефакт к проекту."""
    await service.attach_to_project(artifact_id, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{artifact_id}/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_from_project(
    artifact_id: UUID,
    project_id: UUID,
    service: ArtifactService = Depends(artifact_service_getter),
):
    """Отвязать артефакт от проекта."""
    await service.detach_from_project(artifact_id, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{artifact_id}/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def attach_to_meeting(
    artifact_id: UUID,
    meeting_id: UUID,
    service: ArtifactService = Depends(artifact_service_getter),
):
    """Привязать существующий артефакт к встрече."""
    await service.attach_to_meeting(artifact_id, meeting_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{artifact_id}/meetings/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def detach_from_meeting(
    artifact_id: UUID,
    meeting_id: UUID,
    service: ArtifactService = Depends(artifact_service_getter),
):
    """Отвязать артефакт от встречи."""
    await service.detach_from_meeting(artifact_id, meeting_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)