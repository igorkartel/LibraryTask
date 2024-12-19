from fastapi import UploadFile

from configs.settings import settings
from repositories.abstract_repositories import AbstractMinioS3Repository


class MinioS3Repository(AbstractMinioS3Repository):
    async def is_existing_bucket(self, bucket_name: str) -> None:
        await self.s3_client.head_bucket(Bucket=bucket_name)

    async def create_bucket(self, bucket_name: str) -> None:
        await self.s3_client.create_bucket(
            Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": settings.MINIO_REGION}
        )

    async def upload_file_and_get_preassigned_url(self, bucket_name: str, file: UploadFile) -> None:
        await self.s3_client.upload_fileobj(file.file, bucket_name, file.filename)

    async def delete_file(self, bucket_name: str, filename: str) -> None:
        await self.s3_client.delete_object(Bucket=bucket_name, Key=filename)
