from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.infrastructure.s3_storage.client import get_s3_client


class StorageService:
    
    async def upload_curator_img(
        self,
        file: UploadFile,
        key_prefix: str,
    ) -> str:

        ext = file.filename.split(".")[-1]

        key = f"{key_prefix}/{uuid4()}.{ext}"

        async with get_s3_client() as s3:
            await s3.upload_fileobj(
                file.file,
                settings.s3.curator_bucket.name,
                key,
                ExtraArgs={
                    "ContentType": file.content_type,
                }
            )

        return key

    async def upload_artifacts(
        self,
        file: UploadFile,
        key_prefix: str,
    ) -> str:

        ext = file.filename.split(".")[-1]

        key = f"{key_prefix}/{uuid4()}.{ext}"

        async with get_s3_client() as s3:
            await s3.upload_fileobj(
                file.file,
                settings.s3.artifacts_bucket.name,
                key,
                ExtraArgs={
                    "ContentType": file.content_type,
                }
            )

        return key

    async def generate_private_url(
        self,
        key: str,
        expires: int = 3600,
    ) -> str:

        async with get_s3_client() as s3:
            return await s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": settings.s3.artifacts_bucket.name,
                    "Key": key,
                },
                ExpiresIn=expires,
            )

    async def delete_curator_img(
        self,
        key: str,
    ):
        async with get_s3_client() as s3:
            await s3.delete_object(
                Bucket=settings.s3.curator_bucket.name,
                Key=key,
            )

    async def delete_artifacts(
        self,
        key: str,
    ):

        async with get_s3_client() as s3:
            await s3.delete_object(
                Bucket=settings.s3.artifacts_bucket.name,
                Key=key,
            )
            
def storage_service_getter() -> StorageService:
    return StorageService()