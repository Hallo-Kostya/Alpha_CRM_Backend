from fastapi import UploadFile
import boto3
import json
from botocore.client import Config
from botocore.exceptions import ClientError
from boto3_type_annotations.s3 import Client
from app.core.config import settings


class S3Client:
    def __init__(self, bucket: str, policy: dict):
        self.client: Client = boto3.client(
            "s3",
            endpoint_url=settings.s3.private_host,
            aws_access_key_id=settings.s3.access_key,
            aws_secret_access_key=settings.s3.secret_key,
            region_name=settings.s3.region,
            config=Config(signature_version="s3v4")
        )
        self.bucket = bucket
        self.bucket_policy = policy

    def list_objects(self, prefix: str | None = None) -> dict:
        return self.client.list_objects_v2(self.bucket, Prefix=prefix)

    def put_object(self, file_name: str, file: UploadFile) -> dict:
        return self.client.put_object(Bucket=self.bucket, Key=file_name, Body=file.file, ContentType=file.content_type)

    def get_object(self, object_name: str) -> dict:
        return self.client.get_object(Bucket=self.bucket, Key=object_name)

# TODO: переделать под put и get object чтобы сразу с фронта грузить в с3 но мб fput и fget оставить чтобы по яндексу делать по кайфу
# а ещё сделать для загрузки записей встреч - генерацию presigned юрлов и эндпоинтов для загрузки долгой файлов в минио сразу
