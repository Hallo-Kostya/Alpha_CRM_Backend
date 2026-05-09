from botocore.exceptions import ClientError
import json

from app.core.config import settings
from app.infrastructure.s3_storage.client import get_s3_client


async def ensure_bucket_exists(bucket: str):
    async with get_s3_client() as s3:

        try:
            await s3.head_bucket(Bucket=bucket)

        except ClientError:
            await s3.create_bucket(Bucket=bucket)


async def init_s3():
    await ensure_bucket_exists(settings.s3.curator_bucket.name)
    await ensure_bucket_exists(settings.s3.artifacts_bucket.name)

    async with get_s3_client() as s3:
        await s3.put_bucket_policy(
            Bucket=settings.s3.curator_bucket.name,
            Policy=json.dumps(settings.s3.curator_bucket.policy),
        )
        await s3.put_bucket_policy(
            Bucket=settings.s3.artifacts_bucket.name,
            Policy=json.dumps(settings.s3.artifacts_bucket.policy),
        )