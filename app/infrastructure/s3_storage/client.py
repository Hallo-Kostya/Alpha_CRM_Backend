from contextlib import asynccontextmanager

import aioboto3

from app.core.config import settings


session = aioboto3.Session()


@asynccontextmanager
async def get_s3_client():
    async with session.client(
        service_name="s3",
        endpoint_url=settings.s3.private_host,
        aws_access_key_id=settings.s3.access_key,
        aws_secret_access_key=settings.s3.secret_key,
        region_name=settings.s3.region,
    ) as client:
        yield client