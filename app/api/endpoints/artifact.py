# app/api/v1/artifacts.py
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Response

from app.api.dependencies import get_current_curator
from app.common.enums import ArtifactEntityType
from app.schemas.artifacts import ArtifactCreate, ArtifactFileUpload, ArtifactResponse, ArtifactUpdate
from app.services.artifact_service import ArtifactService, artifact_service_getter

router = APIRouter(
    prefix="/artifacts",
    tags=["artifacts"],
    responses={404: {"description": "Artifact not found"}},
    dependencies=[Depends(get_current_curator)]
)


@router.get("/")
async def get_artifacts(
    project_id: UUID | None = None,
    meeting_id: UUID | None = None,
    service: ArtifactService = Depends(artifact_service_getter),
):
    return await service.list(
        project_id=project_id,
        meeting_id=meeting_id,
    )


@router.post("/{project_id}/artifacts")
async def upload_project_artifact(
    project_id: UUID,
    file: UploadFile,
    service: ArtifactService = Depends(artifact_service_getter),
):
    return await service.create_and_attach(
        file=file,
        entity_type=ArtifactEntityType.PROJECT,
        entity_id=project_id,
    )
    

@router.post("/{meeting_id}/artifacts")
async def upload_meeting_artifact(
    meeting_id: UUID,
    file: UploadFile,
    service: ArtifactService = Depends(artifact_service_getter),
):
    return await service.create_and_attach(
        file=file,
        entity_type=ArtifactEntityType.MEETING,
        entity_id=meeting_id,
    )


@router.post("/intervew/{interview_id}/artifacts")
async def upload_interview_artifact(
    interview_id: UUID,
    file: UploadFile,
    service: ArtifactService = Depends(artifact_service_getter),
):
    return await service.create_and_attach(
        file=file,
        entity_type=ArtifactEntityType.INTERVIEW,
        entity_id=interview_id,
    )


@router.delete("/{artifact_id}/links")
async def detach_artifact(
    artifact_id: UUID,
    entity_type: ArtifactEntityType,
    entity_id: UUID,
    service: ArtifactService = Depends(artifact_service_getter),
):
    await service.detach(
        artifact_id=artifact_id,
        entity_type=entity_type,
        entity_id=entity_id,
    )