# app/infrastructure/s3/s3_client.py
import aioboto3
import json
from botocore.config import Config as BotoConfig
from types_aiobotocore_s3.client import S3Client as TypedS3Client

from app.core.config import settings


class S3Client:
    """Async S3 client wrapper. Works with AWS S3, MinIO, Yandex Cloud, etc."""

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: str | None = None,
        public_host: str | None = None,
        region_name: str = "us-east-1",
    ):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url or settings.s3.private_host or settings.s3.public_host
        self.public_host = public_host or settings.s3.public_host
        self.region_name = region_name
        
        self._boto_config = BotoConfig(
            s3={"addressing_style": "path"},
            retries={"max_attempts": 3, "mode": "standard"},
        )
        self._session = aioboto3.Session()

    async def _get_client(self) -> TypedS3Client:
        client = self._session.client(
            "s3",
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.s3.access_key,
            aws_secret_access_key=settings.s3.secret_key,
            config=self._boto_config,
        )
        return await client.__aenter__()

    async def ensure_bucket_exists(self, policy: dict | None = None) -> None:
        """Create bucket if not exists and apply policy."""
        client = await self._get_client()
        try:
            await client.head_bucket(Bucket=self.bucket_name)
        except client.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                await client.create_bucket(Bucket=self.bucket_name)
                if policy:
                    await client.put_bucket_policy(
                        Bucket=self.bucket_name,
                        Policy=json.dumps(policy),
                    )
            else:
                raise
        finally:
            await client.__aexit__(None, None, None)

    async def put_object(
        self,
        key: str,
        body: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload object and return public URL."""
        client = await self._get_client()
        try:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=body,
                ContentType=content_type,
            )
            public_url = f"{self.public_host}/{self.bucket_name}/{key}"
            return public_url
        finally:
            await client.__aexit__(None, None, None)

    async def delete_object(self, key: str) -> None:
        """Delete object by key."""
        client = await self._get_client()
        try:
            await client.delete_object(Bucket=self.bucket_name, Key=key)
        finally:
            await client.__aexit__(None, None, None)

    async def get_object(self, key: str) -> bytes:
        """Download object."""
        client = await self._get_client()
        try:
            resp = await client.get_object(Bucket=self.bucket_name, Key=key)
            async with resp["Body"] as stream:
                return await stream.read()
        finally:
            await client.__aexit__(None, None, None)